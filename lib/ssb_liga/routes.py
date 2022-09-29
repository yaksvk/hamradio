#!/usr/bin/env python3

import os

from flask import Flask, request, redirect, url_for, render_template, jsonify, make_response, Blueprint, current_app
from werkzeug.utils import secure_filename
from .ssbliga import SsbLiga


ssb_liga = Blueprint('ssb_liga', __name__)


@ssb_liga.route('/')
def start():
    return redirect(url_for('ssb_liga.upload'))


@ssb_liga.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('ssb_liga/start.html')

    if 'file' in request.files:

        # upload file to upload location
        up_file = request.files['file']
        upload_location = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(up_file.filename))
        up_file.save(upload_location)

        # process file to activity
        act1 = SsbLiga(adif_file=upload_location)
        act1.meta['district_code'] = request.values.get('district_code', None)
        id = act1.store()

        return redirect(url_for('ssb_liga.uploaded_adif',id=id))


@ssb_liga.route('/log/<id>')
def uploaded_adif(id):

    log = SsbLiga()
    log.init_from_storage(id)
    log.pre_process()

    return render_template(
        'ssb_liga/render.html',
        log=log,
    )
