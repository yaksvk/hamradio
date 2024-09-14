#!/usr/bin/env python3

import os

from flask import Flask, request, redirect, url_for, render_template, jsonify, make_response, Blueprint,\
    current_app, Response
from werkzeug.utils import secure_filename
from .s2s import S2s

s2s = Blueprint('s2s', __name__, template_folder='templates')

@s2s.route('/')
def start():
    return redirect(url_for('s2s.upload'))


@s2s.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('s2s/start.html')

    if 'file' in request.files:

        # upload file to upload location
        up_file = request.files['file']
        upload_location = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(up_file.filename))
        up_file.save(upload_location)

        # process file to activity
        act1 = S2s(csv_file=upload_location)
        id = act1.store()

        return redirect(url_for('s2s.uploaded_csv',id=id))


@s2s.route('/map/<id>')
def uploaded_csv(id):

    log = S2s(id=id)

    return render_template(
        's2s/render.html',
        log=log,
    )
