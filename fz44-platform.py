#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import socket
import requests
import base64
from threading import Thread
import xml.etree.ElementTree as ET
from flask import Flask, request, jsonify, url_for, redirect
import json
from waitress import serve
import argparse


app = Flask(__name__)


@app.route('/', methods=['POST'])
def index():
    return cft_etp()


@app.route('/cft-etp', methods=['POST'])
def cft_etp():
    res = {}
    data = request.data
    if d.dbg:
        print(data)
    ind = data.decode("UTF-8").find("<")
    xml_sig = data.decode("UTF-8")[ind:]
    if d.dbg:
        print(xml_sig)
    tree = ET.ElementTree(ET.fromstring(xml_sig))
    root = tree.getroot()
    xml_orig = base64.b64decode(root[1].text).decode("utf-8")
    if d.dbg:
        print(xml_orig)
    tree = ET.ElementTree(ET.fromstring(xml_orig))
    root = tree.getroot()
    id = root[0].text
    if d.dbg:
        print(id)
#    start_time = root[1].text
    start_time = time.time()
    if d.find(id):
        d.status.update({
            'last_delay': start_time-d.remove(id),
            'success': d.status['success']+1
        })
        d.status.update({'queue': len(d.queue_list)})
    else:
        d.add_error()
    return jsonify(res)


@app.route('/print_queue')
def print_queue():
    return jsonify(d.print_queue())


@app.route('/status')
def print_status():
    return jsonify(d.print_status())


class Daemon(Thread):
    queue_list = {}
    status = {
            'service_status': 'OK',
            'last_delay': 0,
            'queue': 0,
            'error': 0,
            'success': 0
    }
    dbg = 0

    def add_elem(self, elem):
        self.queue_list.update(elem)
        self.status.update({'queue': len(self.queue_list)})

    def print_queue(self):
        return self.queue_list

    def find(self, id):
        return self.queue_list.get(id)

    def remove(self, id):
        if self.dbg:
            print("remove id " + id)
        return self.queue_list.pop(id)

    def run(self):
        serve(app, host='0.0.0.0', port='8080')

    def service_status(self, error):
        self.status.update(error)

    def print_status(self):
        return self.status

    def add_error(self):
        self.status.update({'error': self.status['error']+1})

    def set_debug(self, dbg):
        self.dbg = dbg


def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--web', action='store_true')
    parser.add_argument('--url', nargs='?')
    parser.add_argument('--delay', nargs='?')
    parser.add_argument('--debug', nargs='?')
    return parser


def main(namespace):
    if namespace.delay:
        print(namespace.delay)
        delay = int(namespace.delay)
    else:
        delay = 1
    if namespace.web:
        d.start()
    if namespace.debug == '1':
        dbg = 1
        d.set_debug(1)
    else:
        dbg = 0
    if namespace.url:
        url = namespace.url
    else:
        url = "http://127.0.0.1:8080/cft-etp"
    headers = {'Content-Type': 'application/xml'}
    i = 0
    while 1:
        i += 1
        start_time = time.time()
        xml = "<?xml version='1.0' encoding='UTF-8'?>" + \
            "<PartyCheckRq xmlns='http://www.sberbank.ru/edo/oep/edo-oep-proc'>" + \
            "<MsgID>" + hex(i)[2:] + "</MsgID><MsgTm>" + \
            time.strftime("%Y-%m-%dT%X", time.gmtime(start_time)) + "</MsgTm>" + \
            "<OperatorName>BSPB_TEST</OperatorName>" + \
            "<BankID>SPB</BankID>" + \
            "<ClientType>1</ClientType>" + \
            "<INN>7727000000</INN>" + \
            "<KPP>772700000</KPP></PartyCheckRq>"
        sig_xml = "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>" + \
            "<Package xmlns='http://www.sberbank.ru/edo/oep/edo-oep-document'>" + \
            "<TypeDocument>PartyCheckRq</TypeDocument><Document>" + \
            base64.b64encode(xml.encode("UTF-8")).decode("UTF-8") + \
            "</Document><Signature>1</Signature></Package>"
        if namespace.web:
            try:
                if dbg:
                    print("Send msg id " + str(i))
                requests.post(url, data=sig_xml, headers=headers)
            except Exception:
                if dbg:
                     formated_error = traceback.format_exception()
                d.service_status({'service_status': 'service connection failed'})
            else:
                d.add_elem({hex(i)[2:]: start_time})
                d.service_status({'service_status': 'OK'})
            finally:
                print(d.print_queue())
        time.sleep(60*delay)


if __name__ == '__main__':
    d = Daemon()
    parser = createParser()
    namespace = parser.parse_args()
    main(namespace)
