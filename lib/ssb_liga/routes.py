#!/usr/bin/env python3

import os

from flask import Flask, request, redirect, url_for, render_template, jsonify, make_response, Blueprint,\
    current_app, Response
from werkzeug.utils import secure_filename
from .ssbliga import SsbLiga


ssb_liga = Blueprint('ssb_liga', __name__, template_folder='templates')


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

        for attr in ('district_code', 'my_call', 'category', 'email'):
            act1.meta[attr] = request.values.get(attr, None)

        act1.pre_process()
        id = act1.store()

        return redirect(url_for('ssb_liga.uploaded_adif',id=id))


@ssb_liga.route('/log/<id>')
def uploaded_adif(id):

    log = SsbLiga(id=id)

    return render_template(
        'ssb_liga/render.html',
        log=log,
    )

@ssb_liga.route('/log/<id>/export/cabrillo')
def export_cabrillo(id):
    log = SsbLiga(id=id)

    # max callsign column width
    len1 = len(log.meta['my_call'])
    len2 = max([len(qso.call) for qso in log.qsos])

    output = render_template(
        'ssb_liga/export.cabrillo',
        log=log,
        formats={
            'len1': len1,
            'len2': len2
        },
    )

    my_call = log.meta['my_call'].upper()

    return Response(
        output,
        mimetype='text/plain',
        headers={
            'Content-Disposition': f'attachment; filename="ssb_liga_{my_call}.cab"',
        }
    )
