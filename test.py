#!/usr/bin/env python

import argparse
import getpass
import os
import sys

import nexpose as nx

try:
    cert_store = os.environ['REQUESTS_CA_BUNDLE']
except KeyError:
    cert_store = None

p = argparse.ArgumentParser()
p.add_argument('--server')
p.add_argument('--cert-store', help='path to trusted CA certs', default=cert_store)
p.add_argument('--validate-certs', help='flag indicating server certs should be validated', action='store_true')
args = p.parse_args()

user = raw_input('\n'*10 + 'Username: ')
pwd = getpass.getpass()

nxclient = nx.Client(server=args.server, username=user, password=pwd, cert_store=args.cert_store)

print 'test.py:nx token: ', nxclient.authtoken

nxclient.login()

print 'test.py:nx token: ', nxclient.authtoken