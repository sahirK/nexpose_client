# !/bin/python

import urllib2
import requests
from lxml import etree
import random
import base64
import threading


# Dump Object Function
def dump(obj):
    for attr in dir(obj):
        print "obj.%s = %s" % (attr, getattr(obj, attr))


# Creates class for the client
class Client:
    def __init__(self, server='', port=3780, api_ver='1.1', username='', password='', logger=None):
        """ Client Class init call """
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.api_ver = api_ver
        self.url_prefix = 'https://{}:{}/api/'.format(self.server, self.port)
        # self.version = apiver  << remove once determine not necessary
        self.authtoken = None
        self.logger = logger

        # force urllib2 to not use a proxy
        # proxy_handler = urllib2.ProxyHandler({})  << switching to requests, though may need similar?
        # opener = urllib2.build_opener(proxy_handler)
        # urllib2.install_opener(opener)
        # self.login()  Remove from init - now must explicitly call it (b/c it's different for each api ver)

    # Request parser
    def request(self, call, api_ver='1.1', **params):
        """ Processes a Request for an API call """
        url = self.url_prefix + api_ver + '/xml' \
                                          ''
        xml = etree.Element(call + "Request")

        # if it has a token it adds it to the request
        if self.authtoken:
            xml.set('session-id', self.authtoken)
            xml.set('sync-id', str(random.randint(1, 65535)))  # seems like this could cause duplicate "request ID's"

        # parses parameters from calls
        for param, value in params.iteritems():
            xml.set(param, str(value))

        # makes request and returns response
        data = etree.tostring(xml)
        headers = {'content-type':'text/xml'}
        print url
        print headers
        print data
        response = requests.post(self.url_prefix + self.api_ver, data=data, headers=headers)
        # r = urllib2.Request(self.url + self.api_ver, data)
        # r.add_header('Content-Type', 'text/xml')

        # response = urllib2.urlopen(r)
        # response = etree.XML(response.read())
        response = etree.XML(response)
        # return response
        return response

    def login(self, api_ver='1.1'):
        """ logs you into the device """
        response = self.request("Login")
        self.authtoken = response.attrib['session-id']

    def get_auth_token(self):
        return self.authtoken

    def adhoc_report(self, query, site_ids):
        """Takes in a query object in the for of SQL and an array with site ids"""
        response = self.ad_hoc_report_request("ReportAdhocGenerate", query, site_ids)
        return response

    def asset_group_config(self, groupid):
        response = self.request("SiteConfig")
        return etree.tostring(response)

    def asset_group_delete(self, groupid):
        response = self.request("AssetGroupDelete")
        return etree.tostring(response)

    def asset_group_listing(self):
        response = self.request("AssetGroupListing")
        return etree.tostring(response)

    def asset_group_save(self, groupid):
        response = self.request("AssetGroupSave")
        return etree.tostring(response)

    def device_delete(self, deviceid):
        response = self.request("DeviceDelete")
        return etree.tostring(response)

    def download_report(self, reporturl):
        req = urllib2.Request(self.baseurl + reporturl)
        req.add_header('Cookie', 'nexposeCCSessionID=%s' % self.token)
        response = urllib2.urlopen(req)
        resxml = etree.XML(response.read())
        return resxml

    def engine_activity(self, engineid):
        response = self.request("EngineActivity")
        return etree.tostring(response)

    def engine_listing(self):
        response = self.request("EngineListing")
        return etree.tostring(response)

    def logout(self):
        response = self.request("Logout")
        return response.attrib['success']

    def report_generate(self, reportid):
        response = self.request("ReportConfig")
        return etree.tostring(response)

    def report_listing(self):
        response = self.request("ReportListing")
        return etree.tostring(response)

    def report_template_listing(self):
        response = self.request("ReportTemplateListing")
        return etree.tostring(response)

    def report_history(self, reportcfgid):
        response = self.request("ReportHistory")
        return etree.tostring(response)

    def restart(self):
        response = self.request("Restart")
        return etree.tostring(response)

    def scan_activity(self):
        response = self.request("ScanActivity")
        return etree.tostring(response)

    def scan_pause(self, scanid):
        response = self.request("ScanPause")
        return etree.tostring(response)

    def scan_resume(self, scanid):
        response = self.request("ScanResume")
        return etree.tostring(response)

    def scan_statistics(self, scanid):
        response = self.request("ScanStatistics")
        return etree.tostring(response)

    def scan_status(self, scanid):
        response = self.request("ScanStatus")
        return etree.tostring(response)

    def scan_stop(self, scanid):
        response = self.request("ScanStop")
        return etree.tostring(response)

    def site_config(self, siteid):
        response = self.request("SiteConfig")
        return etree.tostring(response)

    def site_delete(self, siteid):
        response = self.request("SiteDelete")
        return etree.tostring(response)

    def site_device_listing(self, siteid):
        response = self.request("SiteDeviceListing")
        return etree.tostring(response)

    def site_name_listing(self):
        response = self.request("SiteListing")
        return response.xpath("/SiteListingResponse/SiteSummary/@name")

    def site_id_listing(self):
        response = self.request("SiteListing")
        return response.xpath("/SiteListingResponse/SiteSummary/@id")

    def site_scan(self, siteid):
        response = self.request("SiteScan")
        return etree.tostring(response)

    def site_scan_history(self, siteid):
        response = self.request("SiteScanHistory")
        return etree.tostring(response)

    def system_update(self):
        response = self.request("SystemUpdate")
        return etree.tostring(response)

    def system_information(self):
        response = self.request("SystemInformation")
        return etree.tostring(response)

    def user_authenticator_listing(self):
        response = self.request("UserAuthenticatorListing")
        return etree.tostring(response)

    def user_config(self, userid):
        response = self.request("UserConfig")
        return etree.tostring(response)

    def user_delete(self, userid):
        response = self.request("UserDelete")
        return etree.tostring(response)

    def user_listing(self):
        response = self.request("UserListing")
        return etree.tostring(response)

    def vulnerability_details(self, vulnid):
        response = self.request("VulnerabilityDetails")
        return etree.tostring(response)

    def vulnerability_listing(self):
        response = self.request("VulnerabilityListing")
        return etree.tostring(response)

    def ad_hoc_report_request(self, call, query, site_id=[]):
        # adhoc report request parser
        self.logger.info("In AdHoc generate")
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
