#!/usr/bin/env python3

import os

from flask import Flask, request, redirect, url_for, render_template, jsonify, make_response, Blueprint, current_app
from werkzeug.utils import secure_filename

from .vhfacthamactivity import VhfActHamActivity

vkv_pa = Blueprint('vkv_pa', __name__)

@vkv_pa.route('/')
def vkv_pa_start():
    return redirect(url_for('vkv_pa.vkv_pa_upload'))

@vkv_pa.route('/upload', methods=['GET', 'POST'])
def vkv_pa_upload():
    if request.method == 'GET':
        return render_template('vkv_pa/start.html')

    if 'file' in request.files:

        # upload file to upload location
        up_file = request.files['file']
        upload_location = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(up_file.filename))
        up_file.save(upload_location)

        # process file to activity
        act1 = VhfActHamActivity(adif_file=upload_location)
        act1.meta['gridsquare'] = request.values.get('gridsquare', None)
        id = act1.store()

        return redirect(url_for('vkv_pa.vkv_pa_uploaded_adif',id=id))

@vkv_pa.route('/log/<id>')
def vkv_pa_uploaded_adif(id):

    # gridsquare will be guessed from ADIF, if possible, but can be overridden
    log = VhfActHamActivity()
    log.init_from_storage(id)
    log.calculate_scores()

    # create json data for the map
    web = [{
        'call': qso.call,
        'from': log.meta['latlng'],
        'to': qso.latlng,
        'gridsquare': qso.gridsquare,
        'distance': qso.distance,
        'top': qso.top_distance
    } for qso in log.qsos]

    return render_template(
        'vkv_pa/render.html',
        log=log,
        web=web,
        me={'map_center': log.meta['latlng'], 'gridsquare': log.meta['gridsquare']},
        scores=log.meta['scores'],
    )


