#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
    Hrida is a http interface for Frida
    md5_salt[at]qq.com (http://5alt.me)
"""
import frida
import codecs
import sys
import json
import os
from urllib import unquote
import optparse

from flask import Flask, request
app = Flask(__name__)

def on_message(message, data):
    if message['type'] == 'send':
        print("[*] {0}".format(message['payload']))
    else:
        print(message)

class FridaInterface:
    def __init__(self, frida_script):
        self.frida_script = frida_script
        self.application_id = None
        self.pid = None
        self.device = None
        self.session = None

    def load(self):
        with codecs.open(self.frida_script, 'r', 'utf-8') as f:
            source = f.read()
        return source

    def check_session(self):
        if self.session:
            try:
                self.session.disable_debugger()
                return True
            except:
                pass
        return False

    def spawn_application(self,application_id=None,remote=True):

        if self.check_session():
            return

        os.system("adb forward tcp:27042 tcp:27042")

        self.application_id = application_id if application_id else self.application_id

        if not self.application_id:
            return

        if remote == True:
            self.device = frida.get_remote_device()
        else:
            self.device = frida.get_usb_device()

        for app in self.device.enumerate_applications():
            if app.identifier == application_id and hasattr(app, 'pid'):

                self.pid = app.pid

                self.session = self.device.attach(self.pid)
                self.script = self.session.create_script(self.load())
                self.script.load()

                return

        if not self.pid:

            self.pid = self.device.spawn([self.application_id])
            self.session = self.device.attach(self.pid)

            self.script = self.session.create_script(self.load())
            self.script.load()

            self.device.resume(self.pid)

        return

    def reload_script(self):

        with codecs.open(self.frida_script, 'r', 'utf-8') as f:
            source = f.read()

        self.script = self.session.create_script(source)
        self.script.load()

        return

    def disconnect_application(self):

        self.device.kill(self.pid)
        return

    def callexportfunction(self, methodName, args):
        method_to_call = getattr(self.script.exports, methodName)

        # Take the Java list passed as argument and create a new variable list of argument
        # (necessary for bridge Python - Java, I think)
        s = []
        for i in args:
            s.append(i)

        return_value = method_to_call(*s)
        return return_value

@app.route("/spawn")
def spawn():
    if request.args.get('app', None):
        interface.spawn_application(request.args.get('app'))
        return "1"
    return "failed to attach to app"

@app.route("/call", methods=['POST'])
def call():
    if not request.method == 'POST':
        #return "method is not allowed"
        return ""

    if not interface.application_id:
        #return "spawn an application first"
        return ""

    if not request.form.get('method', None):
        #return "method is empty"
        return ""

    method = request.form.get('method')

    if not request.form.get('args', None):
        args = []
    else:
        args = json.loads(unquote(request.form.get('args')))
        if type(args) != type([]):
            #return "bad args type"
            return ""

    if not interface.check_session():
        interface.spawn_application()

    return interface.callexportfunction(method, args)
    #return "1"

@app.route("/reload")
def reload():
    interface.reload_script()
    return "1"

if __name__ == '__main__':
    parser = optparse.OptionParser('usage: %prog [options] frida_script', add_help_option=False)
    parser.add_option('-h', dest='host', default='127.0.0.1',
                      help='Listen address.')
    parser.add_option('-p', dest='port', default=8800,
                      help='Listen port.')
    parser.add_option('-a', dest='application_id', default=None,
                      help='Application that frida will attach to.')

    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.print_help()
        sys.exit(0)

    interface = FridaInterface(args[0])
    if options.application_id:
        interface.spawn_application(options.application_id)

    app.run(host=options.host,port=options.port, debug=True)

