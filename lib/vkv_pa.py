#!/usr/bin/env python3

import os

from flask import Flask, request, redirect, url_for, render_template, jsonify, make_response, Blueprint, current_app
from werkzeug.utils import secure_filename

from .common_libs.adif import Adif
from .common_libs.hamactivity import HamActivity
from .common_libs.gridsquare import gridsquare2latlng, small_square_distance, is_gridsquare,\
    extract_gridsquare, dist_ham, gridsquare2latlngedges

vkv_pa = Blueprint('vkv_pa', __name__)

@vkv_pa.route('/vkv-prevadzkovy-aktiv')
def vkv_pa_start():
    return redirect(url_for('vkv_pa.vkv_pa_upload'))

@vkv_pa.route('/vkv-prevadzkovy-aktiv/upload', methods=['GET', 'POST'])
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

@vkv_pa.route('/vkv-prevadzkovy-aktiv/log/<id>')
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


class VhfActHamActivity(HamActivity):

    @staticmethod
    def points(point_distance):
        return 2 + point_distance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def calculate_scores(self):
        self.meta['comments'] = {}
        self.meta['scores'] = {}

        if self.meta.get('gridsquare'):
            print('there is gridsquare in meta')
            self.meta['latlng'] = gridsquare2latlng(self.meta['gridsquare'])
            self.meta['latlng_edges'] = gridsquare2latlngedges(self.meta['gridsquare'])
            self.meta['latlng_large_edges'] = gridsquare2latlngedges(self.meta['gridsquare'][0:4])
        else:
            print('there is no gridsquare in meta')

        # calculate distances
        for qso in self.qsos:
            if self.meta['latlng'] and qso.latlng:
                qso.distance = dist_ham(self.meta['latlng'], qso.latlng)

            if self.meta['gridsquare'] and qso.gridsquare:
                qso.points = self.points(small_square_distance(self.meta['gridsquare'], qso.gridsquare))

        # pick qsos with max 3 distances
        top_qsos = sorted(self.qsos,key=lambda x: -x.distance)[:3]
        for qso in self.qsos:
            if qso in top_qsos:
                qso.top_distance = True

        orig_qsos = {}
        orig_gridsquares = {}
        orig_large_gridsquares = {}

        # my own gridsquare is a natural multiplier
        orig_gridsquares[self.meta['gridsquare']] = 1

        for qso in self.qsos:
            ident = qso.call + getattr(qso, 'band', getattr(qso, 'freq', ''))
            if qso.gridsquare:
                orig_qsos[ident] = qso.gridsquare
                orig_gridsquares[qso.gridsquare] = orig_gridsquares.get(qso.gridsquare, 0) + 1
                orig_large_gridsquares[qso.gridsquare[0:4].upper()] = orig_large_gridsquares.get(qso.gridsquare[0:4].upper(), 0) + 1

        # compute scores
        score = 0
        max_dist = 0
        locator_max = ''

        for qth in orig_qsos.values():
            if (self.meta.get('gridsquare', None) and qth):
                dist = small_square_distance(self.meta['gridsquare'], qth)
                score += self.points(dist)
                if dist > max_dist:
                    max_dist = dist
                    locator_max = qth

        self.meta['scores'] = {
            'original_qso_count' : len(orig_qsos.values()),
            'multiplier_count' : len(orig_large_gridsquares.keys()),
            'score' : score,
            'score_multiplied': score*len(orig_large_gridsquares.keys()),
            'max_gridsquare' : locator_max,
            'multipliers' : orig_large_gridsquares.keys(),
            'paint_squares' : list(map(lambda x: gridsquare2latlngedges(x), orig_large_gridsquares.keys())),
            'max_dist' : max_dist
        }
