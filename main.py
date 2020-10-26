import os
import json
from bottle import route, request, HTTPResponse, static_file, run
import mariadb
import tempfile
import bottle

# some globals :)
VERSION = 2.1
SQL = """
    insert into reports (hostname, ip, report) values (?, ?, ?) ON DUPLICATE KEY UPDATE report = ?;
"""

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
            hostname varchar(256) not null,
            ip varchar(64) not null,
            report json not null WITH SYSTEM VERSIONING,
            KEY (id),
            PRIMARY KEY(hostname, ip),
            hardening_index int GENERATED ALWAYS AS (cast(JSON_EXTRACT(`report`, '$.hardening_index') as int)),
            vulnerable_packages_found int GENERATED ALWAYS AS (cast(JSON_EXTRACT(`report`, '$.vulnerable_packages_found') as int)),
            index (hardening_index, vulnerable_packages_found),
            index (ROW_START, ROW_END)
        ) 
            ENGINE=InnoDB
            PAGE_COMPRESSED=1;
    """
    cursor = db.cursor()
    cursor.execute(sql)
    sql = """
    create or replace view description as with t as (
        select
            *
        from
            seq_0_to_999)
        SELECT
            hostname,
            ip,
            json_unquote(json_extract(`report`, CONCAT('$.details[', cast(t.seq as char), '].id'))) as id,
            json_unquote(json_extract(`report`, CONCAT('$.details[', cast(t.seq as char), '].description.desc'))) as description,
            json_unquote(json_extract(`report`, CONCAT('$.details[', cast(t.seq as char), '].description.value'))) as `from`,
            json_unquote(json_extract(`report`, CONCAT('$.details[', cast(t.seq as char), '].description.prefval'))) as `to`,
            json_unquote(json_extract(`report`, CONCAT('$.details[', cast(t.seq as char), '].description.field'))) as `in`
        from
            reports
        join t
        HAVING
            id is not null;
    """
    cursor.execute(sql)
    sql = """
    create or replace view suggestions as with t as (
        select
            *
        from
            seq_0_to_999)
        SELECT
            hostname,
            ip,
            json_unquote(json_extract(`report`, CONCAT('$.suggestion[', cast(t.seq as char), '].description'))) as suggest,
            json_unquote(json_extract(`report`, CONCAT('$.suggestion[', cast(t.seq as char), '].id'))) as id,
            json_unquote(json_extract(`report`, CONCAT('$.suggestion[', cast(t.seq as char), '].severity'))) as severity
        from
            reports
        join t
        HAVING
            suggest IS NOT NULL;
    """
    cursor.execute(sql)
    cursor.close()
    db.close()

def int_float_str(s):
    if isinstance(s,dict) or isinstance(s,list) or isinstance(s, int) or isinstance(s, float):
        return s
    if s.isdigit():
        return int(s)
    else:
        try:
            return float(s)
        except ValueError:
            return s

def preprocessing(data):
    keys = list(data.keys())
    for key in keys:
        data[key] = int_float_str(data.get(key))
        data[key.replace('[]','')] = data.pop(key)
    return data

@route('/')
def index():
    return HTTPResponse(status=200)

@route('/upload', method='POST')
def do_upload():

    agent = request.environ.get('HTTP_USER_AGENT') 
    if agent != 'lynis-bridge':
        return HTTPResponse(status=403)

    else:
        upload = request.files.get('data')
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR')

        filename = "/tmp/{name}".format(name=next(tempfile._get_candidate_names()))
        upload.save(filename)

        stream = os.popen('perl lynis-report-converter.pl -j -i {FILE}'.format(FILE=filename))
        raw = stream.read()
        os.remove(filename)
        data = preprocessing(json.loads(raw))
    
        db = db_connection()
        cursor = db.cursor()
        cursor.execute(SQL, (data['hostname'], client_ip, json.dumps(data), json.dumps(data)))
        cursor.close()
        db.close()
        return HTTPResponse(status=200)
        



if __name__ == '__main__':
    init_db()
    run(host='0.0.0.0', port=8080)

app = bottle.default_app()