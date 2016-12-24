#!/usr/bin/env python

import urllib2
import requests
from lxml import etree
import random
import base64
import threading
import sys


# Dump Object Function
def dump(obj):
    for attr in dir(obj):
        print "obj.%s = %s" % (attr, getattr(obj, attr))


# Creates class for the client
class Client:
    def __init__(self, server='', port=3780, api_ver='1.1', username='', password='',
                 validate_certs=True, cert_store=None, logger=None):
        print 'Client.init:cert_store: ', cert_store
        print 'Client.init:validate_certs', validate_certs
        if validate_certs and cert_store is None:
            sys.exit('**Nexpose client init failed:\n    Cert validation enabled but no cert store provided...exiting')

        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.api_ver = api_ver  # todo determine if this is still required
        self.url_prefix = 'https://{}:{}/api/'.format(self.server, self.port)
        self.authtoken = None
        self.validate_certs = validate_certs
        self.cert_store = cert_store
        self.logger = logger

    def request_generator(self, call, api_ver='1.1', **attribs):
        """
        construct API requests in the appropriate format

        the api URL is of the form: https://<srv>:<port>/api/<ver>/xml.  The API is XML based (not RESTful).  All
        actions are of the form: <action>{Request,Response}, e.g. for <action> = Login the actions are:
        LoginReqeust or LoginResponse.  Of course that has to be modled into some XML to be sent to the server.  It
        appears that all action parameters are attributes (NB: I've seen only a very small subset of the API actions).
        Use lxml.etree to build up requests/actions.

        There are two versions of the API: 1.1 and 1.2.  There is very little overlap, 1.2. is very nearly a disjoint
        extension of 1.1.  They overlap for Login actions (and ???).  The versions are validated differently, 1.1 is
        via DTD's and 1.2 is via XML schemas.  The nexpose class is being updated to switch between the two on demand.

        :param call: name of the action, e.g. Login
        :param api_ver: which version of the API to use, currently {'1.1', '1.2'}
        :param attribs: dict of key, value pairs that will become element attributes in the request XML
        :return: string of XML containing values of interest
        """
        url = self.url_prefix + api_ver + '/xml'
        xml = etree.Element(call + "Request")

        # if it has a token it adds it to the request
        if self.authtoken:
            xml.set('session-id', self.authtoken)
            xml.set('sync-id', str(random.randint(1, 65535)))  # seems like this could cause duplicate "request ID's"

        # adds attributes to api action/request
        for attrib, value in attribs.iteritems():
            xml.set(attrib, str(value))

        # makes request and returns response
        data = etree.tostring(xml)
        headers = {'content-type': 'text/xml'}
        response = requests.post(url, data=data, headers=headers, verify=self.cert_store)
        return etree.XML(response.content)

    def login(self, api_ver='1.1'):
        attribs = {'user-id': self.username, 'password': self.password}
        response = self.request_generator('Login', **attribs)
        self.authtoken = response.attrib['session-id']

    def get_auth_token(self):
        return self.authtoken

    def adhoc_report(self, query, site_ids):
        """Takes in a query object in the for of SQL and an array with site ids"""
        response = self.ad_hoc_report_request("ReportAdhocGenerate", query, site_ids)
        return response

    def asset_group_config(self, groupid):
        response = self.request_generator("SiteConfig")
        return etree.tostring(response)

    def asset_group_delete(self, groupid):
        response = self.request_generator("AssetGroupDelete")
        return etree.tostring(response)

    def asset_group_listing(self):
        response = self.request_generator("AssetGroupListing")
        return etree.tostring(response)

    def asset_group_save(self, groupid):
        response = self.request_generator("AssetGroupSave")
        return etree.tostring(response)

    def device_delete(self, deviceid):
        response = self.request_generator("DeviceDelete")
        return etree.tostring(response)

    def download_report(self, reporturl):
        req = urllib2.Request(self.baseurl + reporturl)
        req.add_header('Cookie', 'nexposeCCSessionID=%s' % self.token)
        response = urllib2.urlopen(req)
        resxml = etree.XML(response.read())
        return resxml

    def engine_activity(self, engineid):
        response = self.request_generator("EngineActivity")
        return etree.tostring(response)

    def engine_listing(self):
        response = self.request_generator("EngineListing")
        return etree.tostring(response)

    def logout(self):
        response = self.request_generator("Logout")
        return response.attrib['success']

    def report_generate(self, reportid):
        response = self.request_generator("ReportConfig")
        return etree.tostring(response)

    def report_listing(self):
        response = self.request_generator("ReportListing")
        return etree.tostring(response)

    def report_template_listing(self):
        response = self.request_generator("ReportTemplateListing")
        return etree.tostring(response)

    def report_history(self, reportcfgid):
        response = self.request_generator("ReportHistory")
        return etree.tostring(response)

    def restart(self):
        response = self.request_generator("Restart")
        return etree.tostring(response)

    def scan_activity(self):
        response = self.request_generator("ScanActivity")
        return etree.tostring(response)

    def scan_pause(self, scanid):
        response = self.request_generator("ScanPause")
        return etree.tostring(response)

    def scan_resume(self, scanid):
        response = self.request_generator("ScanResume")
        return etree.tostring(response)

    def scan_statistics(self, scanid):
        response = self.request_generator("ScanStatistics")
        return etree.tostring(response)

    def scan_status(self, scanid):
        response = self.request_generator("ScanStatus")
        return etree.tostring(response)

    def scan_stop(self, scanid):
        response = self.request_generator("ScanStop")
        return etree.tostring(response)

    def site_config(self, siteid):
        response = self.request_generator("SiteConfig")
        return etree.tostring(response)

    def site_delete(self, siteid):
        response = self.request_generator("SiteDelete")
        return etree.tostring(response)

    def site_device_listing(self, siteid):
        response = self.request_generator("SiteDeviceListing")
        return etree.tostring(response)

    def site_name_listing(self):
        response = self.request_generator("SiteListing")
        return response.xpath("/SiteListingResponse/SiteSummary/@name")

    def site_id_listing(self):
        response = self.request_generator("SiteListing")
        return response.xpath("/SiteListingResponse/SiteSummary/@id")

    def site_scan(self, siteid):
        response = self.request_generator("SiteScan")
        return etree.tostring(response)

    def site_scan_history(self, siteid):
        response = self.request_generator("SiteScanHistory")
        return etree.tostring(response)

    def system_update(self):
        response = self.request_generator("SystemUpdate")
        return etree.tostring(response)

    def system_information(self):
        response = self.request_generator("SystemInformation")
        return etree.tostring(response)

    def user_authenticator_listing(self):
        response = self.request_generator("UserAuthenticatorListing")
        return etree.tostring(response)

    def user_config(self, userid):
        response = self.request_generator("UserConfig")
        return etree.tostring(response)

    def user_delete(self, userid):
        response = self.request_generator("UserDelete")
        return etree.tostring(response)

    def user_listing(self):
        response = self.request_generator("UserListing")
        return etree.tostring(response)

    def vulnerability_details(self, vulnid):
        response = self.request_generator("VulnerabilityDetails")
        return etree.tostring(response)

    def vulnerability_listing(self):
        response = self.request_generator("VulnerabilityListing")
        return etree.tostring(response)

    def ad_hoc_report_request(self, call, query, site_id=[]):
        # adhoc report request parser
        self.logger.info("In AdHoc generate")
        """ Processes a Request for an API call """
        # Could be integrated into regular request, although it could complicate that function
        xml = etree.Element(call + "Request")

        # if it has a token it adds it to the request
        if self.authtoken != '':
            xml.set('session-id', self.authtoken)
            xml.set('sync-id', str(random.randint(1, 65535)))

        # create configuration object
        config = etree.Element('AdhocReportConfig')
        config.set('format', 'sql')

        # create object to store multiple filters
        filters = etree.Element("Filters")

        # create filters
        filter_ver = etree.Element("filter")
        filter_ver.set('type', 'version')
        filter_ver.set('id', self.version)

        filter_query = etree.Element("filter")
        filter_query.set('type', 'query')
        filter_query.set('id', query)

        # append version and query filter to the query object
        filters.append(filter_ver)
        filters.append(filter_query)

        # add sites as filters as well
        for site in site_id:
            filter_n = ''
            filter_n = site
            filter_n = etree.Element("filter")
            filter_n.set('type', 'site')
            filter_n.set('id', str(site))

            # append it to the query object
            filters.append(filter_n)

        # put the queries as part of the config object
        config.append(filters)
        # place the config inside the request object
        xml.append(config)

        # flatten the xml object
        data = etree.tostring(xml)
        self.logger.info("Making Query:\n" + data)
        request = urllib2.Request(self.url_prefix + self.api_ver, data)
        request.add_header('Content-Type', 'application/xml')

        # make request
        response = urllib2.urlopen(request)
        response_data = response.read()

        # because the response comes back in base64 and with a header
        # we need to truncate the header and parse the base64
        # remove the first 230 characters - header
        # the response should be a csv output

        error = 'Error parsing response for site(s) <' + str(
            site_id) + '>, there might have been a problem. See response below.\n' + response_data

        if response_data.startswith("<ReportAdhocGenerateResponse success=\"0\">"):
            response_data = error + response_data
            self.logger.error(response_data)
            return None
        else:
            try:
                decoded_data = base64.b64decode(response_data[230:])
                return decoded_data
            except:
                response_data = error + response_data
                self.logger.error(response_data)
                return None
        self.logger.info("Leaving AdHoc generate")

    def setup_adhoc_report_request(self, call, query, site_id=[]):
        # adhoc report request parser
        lock = threading.RLock()
        lock.acquire()
        try:
            self.logger.info("In setup_adhoc_report_request")
            """ Processes a Request for an API call """
            # Could be integrated into regular request, although it could complicate that function
            xml = etree.Element(call + "Request")

            # if it has a token it adds it to the request
            if (self.authtoken != ''):
                xml.set('session-id', self.authtoken)
                xml.set('sync-id', str(random.randint(1, 65535)))

            # create configuration object
            config = etree.Element('AdhocReportConfig')
            config.set('format', 'sql')

            # create object to store multiple filters
            filters = etree.Element("Filters")

            # create filters
            filter_ver = etree.Element("filter")
            filter_ver.set('type', 'version')
            filter_ver.set('id', self.version)

            filter_query = etree.Element("filter")
            filter_query.set('type', 'query')
            filter_query.set('id', query)

            # append version and query filter to the query object
            filters.append(filter_ver)
            filters.append(filter_query)

            # add sites as filters as well
            for site in site_id:
                filter_n = ''
                filter_n = site
                filter_n = etree.Element("filter")
                filter_n.set('type', 'site')
                filter_n.set('id', str(site))

                # append it to the query object
                filters.append(filter_n)

            # put the queries as part of the config object
            config.append(filters)
            # place the config inside the request object
            xml.append(config)

            # flatten the xml object
            data = etree.tostring(xml)
            self.logger.info("Making Query:\n" + data)
            request = urllib2.Request(self.url_prefix + self.api_ver, data)
            request.add_header('Content-Type', 'application/xml')
            return request
        finally:
            lock.release()

    def send_adhoc_report_request(self, request):
        self.logger.info("In send_adhoc_report_request")
        # make request
        response = urllib2.urlopen(request)
        response_data = response.read()

        # because the response comes back in base64 and with a header
        # we need to truncate the header and parse the base64
        # remove the first 230 characters - header
        # the response should be a csv output

        error = 'Error parsing response there might have been a problem. See response below.\n' + response_data

        if response_data.startswith("<ReportAdhocGenerateResponse success=\"0\">"):
            response_data = error + response_data
            self.logger.error(response_data)
            return None
        else:
            try:
                decoded_data = base64.b64decode(response_data[230:])
                return decoded_data
            except:
                response_data = error + response_data
                self.logger.error(response_data)
                return None
        self.logger.info("Leaving AdHoc generate")
