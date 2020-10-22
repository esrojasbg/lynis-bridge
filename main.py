import os
import json
from bottle import route, request, static_file, run
import mariadb
import tempfile

def db_connection():
    db = mariadb.connect(
        host = os.environ.get('DATABASE_HOST') or 'mariadb',
        port = 3306,
        user = os.environ.get('DATABASE_USER') or 'lynis',
        password = os.environ.get('DATABASE_PASSWORD') or 'lynis',
        database = os.environ.get('DATABASE') or 'lynis')
    db.autocommit = True
    return db

def init_db():
    db = db_connection()
    sql = """
    create
        table if not exists
            reports(
            id bigint UNSIGNED not null AUTO_INCREMENT,
            dt datetime default now(),
            hostname varchar(256) not null,
            ip varchar(64) not null,
            report json not null,
            KEY (id),
            PRIMARY KEY(hostname, ip),
            hardening_index int GENERATED ALWAYS AS (cast(JSON_EXTRACT(`report`, '$.hardening_index') as int)),
            vulnerable_packages_found int GENERATED ALWAYS AS (cast(JSON_EXTRACT(`report`, '$.vulnerable_packages_found') as int))
        ) 
            ENGINE=InnoDB
            PAGE_COMPRESSED=1
            WITH SYSTEM VERSIONING;
    """
    cursor = db.cursor()
    cursor.execute(sql)
    cursor.close()

@route('/upload', method='POST')
def do_upload():
    upload = request.files.get('data')
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR')
    filename = "/tmp/{name}".format(name=next(tempfile._get_candidate_names()))
    upload.save(filename)
    stream = os.popen('perl lynis-report-converter.pl -j -i {FILE}'.format(FILE=filename))
    raw = stream.read()
    os.remove(filename)
    data = json.loads(raw)
    data['hardening_index'] = int(data['hardening_index'])
    data['vulnerable_packages_found'] = int(data['vulnerable_packages_found'])
    db = db_connection()
    sql = """
        insert into reports (hostname, ip, report) values (?, ?, ?) ON DUPLICATE KEY UPDATE report = ?, dt = now();
    """
    cursor = db.cursor()
    cursor.execute(sql, (data['hostname'], client_ip, json.dumps(data), json.dumps(data)))
    cursor.close()
    db.close()
        



if __name__ == '__main__':
    init_db()
    run(host='0.0.0.0', port=8080)

