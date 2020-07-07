'''
Created on 2020-04-07

@author: wf
'''
from flask import Flask
from flask import render_template
from flask import request
import os
from flask.helpers import send_from_directory
import argparse
import sys
from ptp.lookup import Lookup

scriptdir=os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__,static_url_path='',static_folder=scriptdir+'/../web', template_folder=scriptdir+'/../templates')
lookup=Lookup("webserver")

@app.route('/')
def home():
    return index()

def index(titles="",tc=None,errs=None,result=None,message=None):
    """ render index page with the given parameters"""
    return render_template('index.html',titles=titles,tc=tc,errs=errs,result=result,message=message)

@app.route('/parse', methods=['POST'])
def parseTitles():
    """ endpoint for proceedings title parsing"""
    titleLines=request.form.get('titles')
    tp=lookup.tp
    tp.fromLines(titleLines.splitlines(), 'line',clear=True)
    tc,errs,result=tp.parseAll()
    return index(titleLines,tc,errs,result)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Proceedings Title Parser webservice")
    parser.add_argument('--debug',
                                 action='store_true',
                                 help="run in debug mode")
    parser.add_argument('--port',
                                 type=int,
                                 default=5004,
                                 help="the port to use")
    parser.add_argument('--host',
                                 default="0.0.0.0",
                                 help="the host to serve for")
    args=parser.parse_args(sys.argv[1:])
    app.run(debug=args.debug,port=args.port,host=args.host)