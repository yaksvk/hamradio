#!/usr/bin/env python3

import os

from flask import Flask, request, redirect, url_for, render_template, jsonify, make_response, Blueprint, current_app, Response
from werkzeug.utils import secure_filename

from .vhf_edi import VhfEdiActivity

vkv_edi = Blueprint('vkv_edi', __name__, template_folder='templates')

@vkv_edi.route('/')
def vkv_edi_start():
    return redirect(url_for('vkv_edi.upload'))


@vkv_edi.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('vkv_edi/start.html')

    if 'file' in request.files:

        # upload file to upload location
        up_file = request.files['file']
        upload_location = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(up_file.filename))
        up_file.save(upload_location)

        # process file to activity
        act1 = VhfEdiActivity(adif_file=upload_location)
        act1.meta['gridsquare'] = request.values.get('gridsquare', None)

        for attr in ('my_call', 'category', 'email'):
            act1.meta[attr] = request.values.get(attr, None)

        act1.calculate_scores()

        id = act1.store()

        return redirect(url_for('vkv_edi.uploaded_adif',id=id))


@vkv_edi.route('/log/<id>')
def uploaded_adif(id):

    log = VhfEdiActivity(id=id)

    return render_template(
        'vkv_edi/render.html',
        log=log,
    )


@vkv_edi.route('/log/<id>/export/edi')
def export_edi(id):
    log = VhfEdiActivity(id=id)

    # max callsign column width
    #len1 = len(log.meta['my_call'])
    len2 = max([len(qso.call) for qso in log.qsos])

    output = render_template(
        'vkv_edi/export.edi',
        log=log,
        formats={
           # 'len1': len1,
            'len2': len2
        },
    )

    #my_call = log.meta['my_call'].upper()
    #TODO

    my_call = 'TEST_CALL'

    return Response(
        output,
        mimetype='text/plain',
        headers={
            'Content-Disposition': f'attachment; filename="export_{my_call}.edi"',
        }
    )

