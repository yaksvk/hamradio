#!/usr/bin/env python3

import os

from flask import Flask, request, redirect, url_for, render_template, jsonify, make_response, Blueprint,\
    current_app, Response
from werkzeug.utils import secure_filename
from .omactivity import OmActivity

om_activity = Blueprint('om_activity', __name__, template_folder='templates')

@om_activity.route('/')
def start():
    return redirect(url_for('om_activity.upload'))


@om_activity.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('om_activity/start.html')

    if 'file' in request.files:

        # upload file to upload location
        up_file = request.files['file']
        upload_location = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(up_file.filename))
        up_file.save(upload_location)

        # process file to activity
        act1 = OmActivity(adif_file=upload_location)

        for attr in ('my_call', 'category', 'email'):
            act1.meta[attr] = request.values.get(attr, None)

        act1.pre_process()
        id = act1.store()

        return redirect(url_for('om_activity.uploaded_adif',id=id))


@om_activity.route('/log/<id>')
def uploaded_adif(id):

    log = OmActivity(id=id)

    return render_template(
        'om_activity/render.html',
        log=log,
    )

@om_activity.route('/log/<id>/export/cabrillo')
def export_cabrillo(id):
    log = OmActivity(id=id)

    # max callsign column width
    len1 = len(log.meta['my_call'])
    len2 = max([len(qso.call) for qso in log.qsos])
    len3 = max([len(qso.stx) for qso in log.qsos])
    len4 = max([len(qso.srx) for qso in log.qsos])

    output = render_template(
        'om_activity/export.cabrillo',
        log=log,
        formats={
            'len1': len1,
            'len2': len2,
            'len_r1': len3,
            'len_r2': len4,
        },
    )

    my_call = log.meta['my_call'].upper()

    return Response(
        output,
        mimetype='text/plain',
        headers={
            'Content-Disposition': f'attachment; filename="om_activity_{my_call}.cab"',
        }
    )

@om_activity.app_template_filter('mode_filter')
def _jinja2_filter_date(mode):
    modes = {
        'SSB': 'PH',
        'CW': 'CW'
    }
    return modes.get(mode, 'PH')
