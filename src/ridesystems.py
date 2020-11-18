"""
Scraper with Ridesystems website

CREATE TABLE [ccc_arrival_times2] (
[date] [date] NOT NULL,
[route] varchar(50) NOT NULL,
[stop] varchar(max) NOT NULL,
[blockid] varchar(100) NOT NULL,
[scheduledarrivaltime] [time] NOT NULL,
[actualarrivaltime] [time],
[scheduleddeparturetime] [time] NOT NULL,
[actualdeparturetime] [time],
[ontimestatus] varchar(20),
[vehicle] varchar(50) );
"""
import logging
import re
from io import StringIO
import csv

import mechanize
import requests
from retry import retry
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Scraper:
    """Setup for Ridesystems session"""

    def __init__(self, username, password, baseurl="https://cityofbaltimore.ridesystems.net"):
        self.browser = mechanize.Browser()
        self.browser.addheaders = [('User-agent',
                                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                    '(KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36')]

        self.baseurl = baseurl
        self._login(username, password)

    @retry(tries=3, delay=10)
    def _login(self, username, password):
        self.browser.open("{}/login.aspx".format(self.baseurl))
        self.browser.select_form('aspnetForm')

        username_control = self.browser.form.find_control(type='text')
        username_control.value = username
        password_control = self.browser.form.find_control(type='password')
        password_control.value = password

        self.browser.submit()

        # Login validation
        page_contents = self.browser.response().read()
        soup = BeautifulSoup(page_contents, features="html.parser")
        assert soup.find('div', {'class': 'login-panel'}) is None, "Login failed"

    @retry(tries=3, delay=10)
    def _make_response_and_submit(self, ctrl_dict, html):
        """
        Helper to regenerate a response, assign it to the form, and resubmit it. Used for postbacks
        :param ctrl_dict: Dictionary of page control ids and the values they should be set to
        :return:
        """
        response = mechanize.make_response(html, [('Content-Type', 'text/html')],
                                           self.browser.geturl(), 200, 'OK')
        self.browser.set_response(response)
        self.browser.select_form('aspnetForm')
        self.browser.form.set_all_readonly(False)

        self._set_controls(ctrl_dict)

        return self.browser.submit().read()

    @retry(tries=3, delay=10)
    def get_otp(self, start_date, end_date):
        """ Pulls the on time performance data
        :param start_date: The start date to search, inclusive. Searches starting from 12:00 AM
        :param end_date: The end date to search, inclusive. Searches ending at 11:59:59 PM
        :return: Returns an interator with each row being a dictionary wth the keys 'date', 'route', 'stop',
        'blockid', 'scheduledarrivaltime', 'actualarrivaltime', 'scheduleddeparturetime', 'actualdeparturetime',
                   'ontimestatus', 'vehicle

        """
        # Pull the page the first time to get the form that we will need to resubmit a few times
        resp = self.browser.open("{}/Secure/Admin/Reports/ReportViewer.aspx?Path=%2fOldRidesystems%2fPerformance+"
                                 "Reports%2fOn+Time+Performance".format(self.baseurl)).read()
        soup = BeautifulSoup(resp, features="html.parser")
        html = soup.find('form', id='aspnetForm').prettify().encode('utf8')

        self.browser.select_form('aspnetForm')
        self.browser.form.set_all_readonly(False)

        ctrl_dict = {
            # Start Date
            'ctl00$MainContent$ssrsReportViewer$ctl08$ctl03$txtValue': start_date.strftime('%#m/%#d/%Y'),
            # End Date
            'ctl00$MainContent$ssrsReportViewer$ctl08$ctl05$txtValue': end_date.strftime('%#m/%#d/%Y 11:59:59 PM'),
            # Seconds For Early
            'ctl00$MainContent$ssrsReportViewer$ctl08$ctl11$txtValue': '30',
            # Seconds For Late
            'ctl00$MainContent$ssrsReportViewer$ctl08$ctl13$txtValue': '300',
            # Status based on (departure)
            'ctl00$MainContent$ssrsReportViewer$ctl08$ctl15$ddValue': ['1'],
            # Force assign block (No)
            'ctl00$MainContent$ssrsReportViewer$ctl08$ctl17$ddValue': ['2'],
            # Status
            'ctl00$MainContent$ssrsReportViewer$ctl08$ctl19$txtValue': 'On Time,Early,Late,Missing',
            'ctl00$MainContent$ssrsReportViewer$ctl08$ctl19$divDropDown$ctl01$HiddenIndices': '0,1,2,3',
            # Hours
            'ctl00$MainContent$ssrsReportViewer$ctl08$ctl21$txtValue': ','.join([str(x) for x in range(24)]),
            'ctl00$MainContent$ssrsReportViewer$ctl08$ctl21$divDropDown$ctl01$HiddenIndices':
                ','.join([str(x) for x in range(24)]),
            # Group Data
            'ctl00$MainContent$ssrsReportViewer$ctl08$ctl23$ddValue': ['1'],

            # Other values
            'ctl00$MainContent$ssrsReportViewer$ctl15': 'standards',
            'ctl00$MainContent$ssrsReportViewer$AsyncWait$HiddenCancelField': 'False',
            '__EVENTTARGET': 'ctl00$MainContent$ssrsReportViewer$ctl08$ctl05',
            '__ASYNCPOST': 'true',
            'ctl00$MainContent$scriptManager':
                'ctl00$MainContent$scriptManager|ctl00$MainContent$ssrsReportViewer$ctl08$ctl05'
        }

        self._set_controls(ctrl_dict)
        resp = self.browser.submit().read()
        soup = BeautifulSoup(resp, features='html.parser')

        # set the controls
        routes = [x.text.replace('\xa0', ' ') for x in soup.find_all('label', {
            'for': re.compile(r'ctl00_MainContent_ssrsReportViewer_ctl08_ctl07_divDropDown_ctl(0[2-9]|[1-9][0-9]*)')})]

        ctrl_dict['ctl00$MainContent$ssrsReportViewer$ctl08$ctl07$divDropDown$ctl01$HiddenIndices'] = \
                         ','.join([str(x) for x in range(len(routes))])
        ctrl_dict['ctl00$MainContent$ssrsReportViewer$ctl08$ctl07$txtValue'] = ','.join(routes)
        ctrl_dict['__EVENTTARGET'] = 'ctl00$MainContent$ssrsReportViewer$ctl08$ctl07'
        ctrl_dict['__ASYNCPOST'] = 'true'
        ctrl_dict['ctl00$MainContent$scriptManager'] = \
                  'ctl00$MainContent$scriptManager|ctl00$MainContent$ssrsReportViewer$ctl08$ctl07'

        resp = self._make_response_and_submit(ctrl_dict, html)

        # turn the values in the page into a dictionary
        resp_dict = self.parse_ltiv_data(resp.decode())

        soup = BeautifulSoup(resp, features='html.parser')

        stops = [x.text.replace('\xa0', ' ') for x in soup.find_all('label', {
            'for': re.compile(r'ctl00_MainContent_ssrsReportViewer_ctl08_ctl09_divDropDown_ctl(0[2-9]|[1-9][0-9]*)')})]

        # Setup the required values
        ctrl_dict['ctl00$MainContent$ssrsReportViewer$ctl08$ctl09$txtValue'] = ','.join(stops)
        ctrl_dict['ctl00$MainContent$ssrsReportViewer$ctl08$ctl09$divDropDown$ctl01$HiddenIndices'] = \
            ','.join([str(x) for x in range(len(stops))])
        ctrl_dict['__VIEWSTATE'] = resp_dict['__VIEWSTATE'][0]
        ctrl_dict['__EVENTVALIDATION'] = resp_dict['__EVENTVALIDATION'][0]
        ctrl_dict['__EVENTTARGET'] = ''
        ctrl_dict['ctl00$MainContent$ssrsReportViewer$ctl08$ctl00'] = 'View Report'
        ctrl_dict['ctl00$MainContent$ssrsReportViewer$ctl14'] = 'ltr'
        ctrl_dict['ctl00$MainContent$scriptManager'] = \
            'ctl00$MainContent$scriptManager|ctl00$MainContent$ssrsReportViewer$ctl08$ctl00'

        resp = self._make_response_and_submit(ctrl_dict, html)
        response_url_base = re.search(r'"ExportUrlBase":"(.*?)"', resp.decode()).group(1)

        resp_dict = self.parse_ltiv_data(resp.decode())

        # Setup the required values
        ctrl_dict['null'] = '100'
        ctrl_dict['ctl00$MainContent$ssrsReportViewer$ctl09$ctl03$ctl00'] = ''
        ctrl_dict['__EVENTTARGET'] = 'ctl00$MainContent$ssrsReportViewer$ctl13$Reserved_AsyncLoadTarget'
        ctrl_dict['__VIEWSTATE'] = resp_dict['__VIEWSTATE'][0]
        ctrl_dict['__EVENTVALIDATION'] = resp_dict['__EVENTVALIDATION'][0]
        ctrl_dict['__EVENTTARGET'] = 'ctl00$MainContent$ssrsReportViewer$ctl13$Reserved_AsyncLoadTarget'
        ctrl_dict['ctl00$MainContent$scriptManager'] = \
            'ctl00$MainContent$scriptManager|ctl00$MainContent$ssrsReportViewer$ctl13$Reserved_AsyncLoadTarget'
        ctrl_dict['ctl00$MainContent$ssrsReportViewer$ctl09$ctl00$CurrentPage'] = ''

        self._make_response_and_submit(ctrl_dict, html)
        csv_data = requests.get("{}{}CSV".format(self.baseurl, response_url_base.replace(r'\u0026', '&')),
                                cookies=self.browser.cookiejar,
                                headers={
                                    'referer': 'https://cityofbaltimore.ridesystems.net/Secure/Admin/Reports/'
                                               'ReportViewer.aspx?Path=%2fOldRidesystems%2fRidership%2fAll+Ridership+'
                                               'By+Vehicle',
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                                  '(KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'},
                                )

        csv_iter = csv.reader(StringIO(csv_data.text), delimiter=',')
        logging.debug("Got %s bytes of data", len(csv_data.text))

        # Lets flush the header stuff; break on the first blank line
        while csv_iter.__next__():
            continue
        csv_iter.__next__()  # flush the header

        for row in csv_iter:
            if not row:
                break  # on the first blank row, break because we want to drop the footer stuff
            yield {'date': row[0], 'route': row[1], 'stop': row[2], 'blockid': row[3], 'scheduledarrivaltime': row[4],
                   'actualarrivaltime': row[5], 'scheduleddeparturetime': row[6], 'actualdeparturetime': row[7],
                   'ontimestatus': row[8], 'vehicle': row[9]}

    @staticmethod
    def parse_ltiv_data(data):
        """ Parses the data that comes back from the aspx pages. Its in the format LENGTH|TYPE|ID|VALUE"""

        def get_next_element(idata, ilength=None):
            if ilength is not None:
                assert ilength < len(idata) and idata[ilength] == '|', \
                    "Malformed input. Expected delimiter where there wasn't one. idata: {}".format(idata[:100])
                iret = idata[:ilength]
                idata = idata[ilength + 1:]  # drop the delimiter
                return iret, idata
            return get_next_element(idata, idata.index('|'))

        ret = {}

        while data:
            length, data = get_next_element(data)
            length = int(length)
            data_type, data = get_next_element(data)
            data_id, data = get_next_element(data)
            value, data = get_next_element(data, length)

            ret[data_id] = (value, data_type)
        return ret

    def _set_controls(self, ctrl_dict):
        for ctrl_id, val in ctrl_dict.items():
            try:
                ctrl = self.browser.form.find_control(name=ctrl_id)
                ctrl.disabled = False
                ctrl.value = val
            except mechanize.ControlNotFoundError:
                self.browser.form.new_control('hidden', ctrl_id, {'value': val})
        self.browser.form.fixup()
        self._log_controls()

    def _log_controls(self):
        logging.debug('\n'.join(
            ['%s: %s *%s*' % (c.name, c.value, c.disabled) if c.disabled else '%s: %s' % (c.name, c.value) for c in
             self.browser.form.controls]))
