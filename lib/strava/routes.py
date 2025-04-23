#!/usr/bin/env python3

import os

from flask import Flask, request, redirect, url_for, render_template, jsonify, make_response, Blueprint,\
    current_app, Response
from werkzeug.utils import secure_filename

strava = Blueprint('strava', __name__, template_folder='templates')

@strava.route('/')
def start():
    return render_template('strava/index.html')
