import io
import os
import time
import uuid
import zipfile
from random import randint
from flask import Flask, request, jsonify, render_template, send_file, redirect, Response
from base64 import b64decode
from werkzeug.utils import secure_filename
import shutil

static_folder = '../sechack365-keyboard-survey-app/dist'
app = Flask(__name__, static_folder=static_folder)
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = os.environ.get("UPLOAD_FOLDER", "./uploads")

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.mkdir(app.config['UPLOAD_FOLDER'])


@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')


@app.route('/<path:path>', methods=['GET'])
def static_files(path):
    # Safe joinしているから安全なはず
    # https://github.com/pallets/flask/blob/94f436013792249a9bb7206c2868d4c6c21fd887/flask/helpers.py#L612
    if not os.path.isdir(static_folder + '/' + path):
        return app.send_static_file(path)
    else:
        return app.send_static_file(path + '/index.html')


@app.route('/view', methods=['GET'])
def view_files():
    uuid_dir = request.args.get('uuid')
    key = request.args.get('key')
    file = request.args.get('file')
    action = request.args.get('action')

    if uuid_dir is None or \
            key is None or \
            action is None:
        return 'Bad Request', 400

    if not uuid_dir or \
            not key or \
            not action:
        return 'Bad Request', 400

    uuid_dir = secure_filename(uuid_dir)
    uuid_path = os.path.join(app.config['UPLOAD_FOLDER'], uuid_dir)

    if os.path.isdir(uuid_path):
        key_path = os.path.join(uuid_path, '.key')
        if os.path.isfile(key_path):
            key_str = ''
            with open(key_path) as f:
                key_str = f.readline()
            if key_str == key:
                if action == 'get':
                    if file is None:
                        files = os.listdir(uuid_path)
                        files = filter(lambda x: not x.startswith('.'), files)
                        return render_template(
                            'view.html',
                            dirname='uploads/' + uuid_dir,
                            files=files,
                            uuid=uuid_dir,
                            key=key
                        )
                    else:
                        file = secure_filename(file)
                        file_path = os.path.join(uuid_path, file)
                        if not os.path.isfile(file_path):
                            return 'Bad Request', 400
                        return send_file(file_path)
                elif action == 'download':
                    fileIO = io.BytesIO()
                    with zipfile.ZipFile(fileIO, 'w') as zip_file:
                        files = os.listdir(uuid_path)
                        files = filter(lambda x: not x.startswith('.'), files)
                        for f in files:
                            zip_file.write(f'{uuid_path}/{f}', arcname=f'{uuid_dir}/{f}')
                    fileIO.seek(0)
                    return Response(fileIO.getvalue(),
                                    mimetype='application/zip',
                                    headers={'Content-Disposition': f'attachment;filename={uuid_dir}.zip'})
                elif action == 'delete':
                    shutil.rmtree(uuid_path)
                    return redirect('/')

    return 'Bad Request', 400


@app.route('/api/v1/txt', methods=['GET'])
def v1_txt():
    mode = request.args.get('mode', '')

    if mode not in ['word', 'ss', 'ls']:
        return jsonify(
            {
                "message": "Invalid mode"
            }
        ), 400

    text_dir_path = os.path.join(static_folder, 'text')
    mode_dir_path = os.path.join(text_dir_path, mode)

    files = [f for f in os.listdir(mode_dir_path) if f.endswith('.json')]

    if len(files) == 0:
        return jsonify(
            {
                "message": "Failed to fetch json files"
            }
        ), 500

    file = files[randint(0, len(files) - 1)]

    return jsonify(
        {
            "file": f"/text/{mode}/{file}"
        }
    )


@app.route('/api/v1/upload', methods=['POST'])
def v1_upload():
    for param in ['user_log', 'audio_info', 'audio_data', 'questions']:
        if param not in request.form:
            return jsonify(
                {
                    "message": "The request hasn't `" + param + "`"
                }
            ), 400

    user_log = request.form['user_log']
    audio_info = request.form['audio_info']
    questions = request.form['questions']
    fingerprints = request.form['fingerprints']

    audio_data = request.form['audio_data']
    header, encoded = audio_data.split(',', 1)
    audio_raw_data = b64decode(encoded)

    upload_id = str(uuid.uuid4())
    upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], upload_id)
    os.mkdir(upload_dir)

    user_log_path = os.path.join(upload_dir, 'user_log.json')
    with open(user_log_path, "w", encoding='utf-8') as file:
        file.write(user_log)

    audio_info_path = os.path.join(upload_dir, 'audio_info.json')
    with open(audio_info_path, "w", encoding='utf-8') as file:
        file.write(audio_info)

    questions_path = os.path.join(upload_dir, 'questions.json')
    with open(questions_path, "w", encoding='utf-8') as file:
        file.write(questions)

    fingerprints_path = os.path.join(upload_dir, 'fingerprints.json')
    with open(fingerprints_path, "w", encoding='utf-8') as file:
        file.write(fingerprints)

    audio_data_path = os.path.join(upload_dir, 'audio_data.webm')
    with open(audio_data_path, "wb") as file:
        file.write(audio_raw_data)

    key_str = uuid.uuid4().hex
    key_path = os.path.join(upload_dir, '.key')
    with open(key_path, "w", encoding='utf-8') as file:
        file.write(key_str)

    return jsonify(
        {
            "upload_id": upload_id,
            "view_key": key_str
        }
    )


if __name__ == '__main__':
    app.run()
