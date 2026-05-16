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

    web = [{
        'call': qso.call,
        'from': log.meta['latlng'],
        'to': qso.latlng,
        'gridsquare': qso.gridsquare,
        'distance': qso.distance,
        'top': qso.top_distance,
    } for qso in log.qsos]

    return render_template(
        'vkv_edi/render.html',
        log=log,
        web=web,
        me={'map_center': log.meta['latlng']},
    )


@vkv_edi.route('/log/<id>/export/edi')
def export_edi(id):
    log = VhfEdiActivity(id=id)

    # custom EDI logic for qsos, additional atttributes
    unique_calls = set()
    unique_gridsquares = set()
    unique_dxcc = set()

    for qso in log.qsos:

        # duplicity
        if qso.call not in unique_calls:
            unique_calls.add(qso.call)
            qso.dupe = ''
        else:
            qso.dupe = 'D'

        # multipliers
        if qso.gridsquare not in unique_gridsquares:
            unique_gridsquares.add(qso.gridsquare)
            qso.new_gridsquare = 'N'
        else:
            qso.new_gridsquare = ''

        # dxccs
        if qso.dxcc not in unique_dxcc:
            unique_dxcc.add(qso.dxcc)
            qso.new_dxcc = 'N'
        else:
            qso.new_dxcc = ''

    output = render_template(
        'vkv_edi/export.edi',
        log=log,
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


@vkv_edi.app_template_filter('edi_mode_filter')
def _jinja2_filter_edi_mode(mode):
    mapping = {
        'ssb': 1,
        'cw': 2,
        'fm': 6,
    }
    return mapping.get(mode.lower(), 0)


@vkv_edi.app_template_filter('edi_date_filter')
def _jinja2_filter_edi_date(date):
    return ''.join((date[0:4], date[4:6], date[6:8]))

