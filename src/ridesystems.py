""" Scraper with Ridesystems website"""
from bs4 import BeautifulSoup
import mechanize


class Ridesystems:
    """Setup for Ridesystems session"""

    def __init__(self, username, password, baseurl="https://cityofbaltimore.ridesystems.net"):
        self.browser = mechanize.Browser()
        self._login(username, password, baseurl)

    def _login(self, username, password, baseurl):
        self.browser.addheaders = [('User-agent',
                                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                                    'like Gecko)Chrome / 86.0.4240.183 Safari / 537.36')]
        self.browser.open("{}/login.aspx".format(baseurl))
        self.browser.select_form('aspnetForm')

        username_control = self.browser.form.find_control(type='text')
        username_control.value = username
        password_control = self.browser.form.find_control(type='password')
        password_control.value = password

        self.browser.submit()

        # Login validation
        resp = self.browser.response()
        page_contents = resp.read()
        soup = BeautifulSoup(page_contents, features="html.parser")
        assert soup.find('div', {'class': 'login-panel'}) is None, "Login failed"
