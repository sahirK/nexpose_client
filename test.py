#!/usr/bin/env python

import argparse
import getpass

import nexpose as nx

p = argparse.ArgumentParser()
p.add_argument('--server')
args = p.parse_args()

user = raw_input('Username: ')
pwd = getpass.getpass()

nxclient = nx.Client(server=args.server, username=user, password=pwd)

print nxclient.authtoken

nxclient.login()

print nxclient.authtoken