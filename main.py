import os
import json
from bottle import route, request, static_file, run


@route('/upload', method='POST')
def do_upload():
    upload = request.files.get('data')
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR')
    filename = "/tmp/" + client_ip + upload.filename
    upload.save(filename)
    stream = os.popen('perl lynis-report-converter.pl -j -i {FILE}'.format(FILE=filename))
    raw = stream.read()
    data = json.loads(raw)
    print(data)

if __name__ == '__main__':
    run(host='0.0.0.0', port=8080)

