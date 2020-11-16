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
import traceback
import sys
import random


app = Flask(__name__)


@app.route('/', methods=['POST'])
def index():
    return cft_etp()


@app.route('/cft-etp', methods=['POST'])
def cft_etp():
    res = {}
    data = request.data.decode("UTF-8")
    ind = data.find("<")
    xml_sig = data[ind:]
    if d.dbg:
        print_log(xml_sig)
    tree = ET.ElementTree(ET.fromstring(xml_sig))
    root = tree.getroot()
    xml_orig = base64.b64decode(root[1].text).decode("utf-8")
    if d.dbg:
        print_log(xml_orig)
    tree = ET.ElementTree(ET.fromstring(xml_orig))
    root = tree.getroot()
    id = root[2].text
    if d.dbg:
        print_log(id)
    if len(root[7]) == 1:
        start_time = time.time()
        if d.find_queue(id):
            find = d.remove(id)
            d.status.update({
                'last_check_delay': start_time-find,
                'success': d.status['success']+1
            })
            d.add_request({
                id: {
                    "start_time": find,
                    "check_delay": start_time-find
                }
            })
            d.status.update({'queue': d.len_queue()})
        else:
            d.add_error()
    elif len(root[7]) == 2:
        print_log("Send buisness ACK")
        s.buisness_ack(root[0].text)
        start_time = time.time()
        if d.find_reqest(id):
            find_dict = d.find(id)
            d.status.update({
                'last_request_delay': start_time-find_dict["start_time"],
                'success': d.status['success']+1
            })
            find_dict.update({
                "request_delay": start_time-find_dict["start_time"]
            })
            d.add_elem({id: find_dict})
        else:
            d.add_error()
    return jsonify(res)


@app.route('/print_queue')
def print_queue():
    return jsonify(d.print_queue())


@app.route('/print_requests')
def print_requests():
    return jsonify(d.print_req())


@app.route('/status')
def print_status():
    return jsonify(d.print_status())


@app.route('/send', methods=['POST'])
def send():
    data = request.data.decode("UTF-8")
    tree = ET.ElementTree(ET.fromstring(data))
    root = tree.getroot()
    id = root[0].text
    if d.dbg:
        print_log('send message :' + data)
    start_time = time.time()
    try:
        s.send_to_service(msg=data, start_time=start_time)
    except Exception as e:
        if d.dbg:
            print_log(e)
        res = {"status": e}
        d.service_status({'service_status': 'service connection failed'})
    else:
        if d.find_queue(id):
            d.remove(id)
        d.add_elem({id: start_time})
        d.service_status({'service_status': 'OK'})
        res = {"status": "send"}
#    finally:
#        if d.dbg:
#            print_log(str(d.print_queue()))
    return jsonify(res)


class Daemon(Thread):
    queue_list = {}
    status = {
            'service_status': 'OK',
            'last_check_delay': 0,
            'last_request_delay': 0,
            'queue': 0,
            'error': 0,
            'success': 0
    }
    dbg = 0
    request_list = {}

    def add_elem(self, elem):
        self.queue_list.update(elem)
        self.status.update({'queue': self.len_queue()})

    def add_req(self, elem):
        self.request_list.update(elem)

    def print_queue(self):
        return self.queue_list

    def print_req(self):
        return self.request_list

    def find_queue(self, id):
        return self.queue_list.get(id)

    def find_req(self, id):
        return self.request_list.get(id)

    def remove(self, id):
        if self.dbg:
            print_log("remove id " + id)
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

    def len_queue(self):
        return len(queue_list)


def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--web', action='store_true')
    parser.add_argument('--url', nargs='?')
    parser.add_argument('--delay', nargs='?')
    parser.add_argument('--debug', nargs='?')
    return parser


def print_log(msg):
    fmt = time.strftime("%Y-%m-%d %X")
    print("[" + time.strftime(fmt) + "] " + msg)


class Sender:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def send_to_service(self, msg="", i=0, start_time="", type_doc="PartyCheckRq"):
        if not msg:
            xml = "<?xml version='1.0' encoding='UTF-8'?>" + \
                "<PartyCheckRq xmlns='http://www.sberbank.ru/edo/oep/edo-oep-proc'>" + \
                "<MsgID>" + i + "</MsgID><MsgTm>" + \
                time.strftime("%Y-%m-%dT%X", time.gmtime(start_time)) + "</MsgTm>" + \
                "<OperatorName>BSPB_TEST</OperatorName>" + \
                "<BankID>SPB</BankID>" + \
                "<ClientType>1</ClientType>" + \
                "<INN>7727000000</INN>" + \
                "<KPP>772700000</KPP></PartyCheckRq>"
        else:
            xml = msg
        sig_xml = "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>" + \
            "<Package xmlns='http://www.sberbank.ru/edo/oep/edo-oep-document'>" + \
            "<TypeDocument>" + type_doc + "</TypeDocument><Document>" + \
            base64.b64encode(xml.encode("UTF-8")).decode("UTF-8") + \
            "</Document><Signature>1</Signature></Package>"
        requests.post(self.url, data=sig_xml, headers=self.headers)

    def buisness_ack(self, id):
        msg = "<?xml version='1.0' encoding='UTF-8'?>" + \
            "<BusinessRsAck xmlns='http://www.sberbank.ru/edo/oep/edo-oep-proc'>" + \
            "<MsgID>0</MsgID><MsgTm>" + \
            time.strftime("%Y-%m-%dT%X", time.gmtime(time.time())) + \
            "</MsgTm><CorrelationID>" + id + "</CorrelationID>" + \
            "<OperatorName>BSPB_TEST</OperatorName>" + \
            "<BankID>SPB</BankID>" + \
            "<Status><StatusCode>0" + \
            "</StatusCode></Status></BusinessRsAck>"
        self.send_to_service(msg=msg, type_doc="BusinessRsAck")


def generate_id():
    ind = "TEST_"
    rand = lambda: hex(random.randint(0, 15))[2:]
    for i in range(27):
        ind += rand()
    return ind


def main(web, delay, dbg):
    while 1:
        ind = generate_id()
        start_time = time.time()
        if dbg:
            print_log("Send msg id " + str(i))
        try:
            s.send_to_service(i=ind, start_time=start_time)
        except Exception:
            if dbg:
                traceback.print_exc(file=sys.stdout)
            if web:
                d.service_status({'service_status': 'service connection failed'})
        else:
            if web:
                d.add_elem({ind: start_time})
                d.service_status({'service_status': 'OK'})
        finally:
            if dbg:
                print_log(str(d.print_queue()))
        time.sleep(60*delay)


if __name__ == '__main__':
    d = Daemon()
    parser = createParser()
    namespace = parser.parse_args()
    if namespace.delay:
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
    s = Sender(url, headers)
    main(namespace.web, delay, dbg)
