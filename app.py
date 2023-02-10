#!/usr/bin/env python3

import os
from dotenv import load_dotenv

from flask import Flask, request, redirect, url_for, render_template, jsonify, make_response

# import blueprints
from lib.vkv_pa.routes import vkv_pa
from lib.ssb_liga.routes import ssb_liga
from lib.om_activity.routes import om_activity

# for local development, import ENV variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.getenv('TMP', default='/tmp')

@app.route('/')
def start():
    return render_template(
        'index.html',
    )

app.register_blueprint(vkv_pa, url_prefix="/vkv-prevadzkovy-aktiv")
app.register_blueprint(ssb_liga, url_prefix="/ssb-liga")
app.register_blueprint(om_activity, url_prefix="/om-activity")


# formatters
@app.template_filter('time_filter')
def _jinja2_filter_time(time):
    return ':'.join((time[0:2],time[2:4]))

@app.template_filter('date_filter')
def _jinja2_filter_date(date):
    return '-'.join((date[0:4],date[4:6],date[6:8]))

if not os.getenv('DEVELOPMENT', default=False):
    # generic error handlers
    @app.errorhandler(Exception)
    def default_error_handler(error):
        return render_template(
            'error.html',
            error=error
        )
    app.register_error_handler(Exception, default_error_handler)

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
