#!/usr/bin/env python3

import os

from flask import Flask, request, redirect, url_for, render_template, jsonify, make_response, Blueprint, current_app
from werkzeug.utils import secure_filename


ssb_liga = Blueprint('ssb_liga', __name__)

@ssb_liga.route('/')
def start():
    return redirect(url_for('ssb_liga.upload'))

@ssb_liga.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('ssb_liga/start.html')
