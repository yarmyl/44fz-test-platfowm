#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import socket
import requests
import base64
from threading import Thread
import xml.etree.ElementTree as ET


class Daemon(Thread):
    queue_list = {}
    def add_elem(self, elem):
        self.queue_list.update(elem)
    def print_queue(self):
        return self.queue_list
    def find(self, id):
        return self.queue_list.get(id)
    def remove(self, id):
        return self.queue_list.pop(id)
    def run(self):
        try:
            sock = socket.socket()
            sock.bind(('', 8090))
            sock.listen()
            while True:
                conn, _ = sock.accept()
                try:
                    data = conn.recv(1024)
                    while not data:
                        data = conn.recv(1024)
                    print(data)
                    ind = data.decode("UTF-8").find("<")
                    xml_sig = data.decode("UTF-8")[ind:]
                    tree = ET.ElementTree(ET.fromstring(xml_sig))
                    root = tree.getroot()
                    xml_orig = base64.b64decode(root[1].text).decode("utf-8")
                    tree = ET.ElementTree(ET.fromstring(xml_orig))
                    root = tree.getroot()
                    id = root[0].text
                    print(id)
                    start_time = root[1].text
                    if self.find(id):
                        print(self.remove(id))
                except:
                    print("Some socket Error!")
                finally:
                    conn.close()
        finally: sock.close()



def main():
    d = Daemon()
    d.start()
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
        requests.post(url, data=sig_xml, headers=headers)
        d.add_elem({hex(i)[2:]: start_time})
        print(d.print_queue())
        time.sleep(10*1)


if __name__ == '__main__':
    main()