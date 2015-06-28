from BeautifulSoup import BeautifulSoup as Soup
import urllib
import mechanize
import os


class GetResponseSoup(object):
    def __init__(self, url, fields=''):
        self.fields = fields
        self._url = url
        self._resp = self._get_response()
        self._read_response = None

    @property
    def url(self):
        return self._url

    @property
    def read_response(self):
        if not self._read_response:
            self._read_response = self._resp.read()
        return self._read_response

    @property
    def encoded_fields(self):
        return urllib.urlencode(self.fields)

    @property
    def soup(self):
        return Soup(self.read_response)

    def update(self, url, fields=''):
        """pass the class a new url and optionally fields.
        This will update the response object and soup
        """
        self._url = url
        self.fields = fields
        self._resp = self._get_response()
        self._read_response = None

    def _get_response(self):
        return mechanize.urlopen(self._get_request())

    def _get_request(self):
        return mechanize.Request(self.url, self.encoded_fields)

    @classmethod
    def from_url(cls, url, fields=''):
        return cls(url, fields)

    def download_invoices(self, transaction_list, save_path):
        """Expects a list of transaction dictionaries with filename and url
        along with the path where the files should be saved
        """
        for transaction_row in transaction_list:
            filename = save_path + '/{}.pdf'.format(transaction_row['filename'])
            if os.path.exists(filename):
                print 'skipping (already downloaded): ' + filename
                continue
            print 'downloading ' + transaction_row['url'] + ' to ' + filename
            with open(filename, 'w') as f:
                self.update(transaction_row['url'])
                f.write(self.read_response)


def format_datestring(ds):
    """
    Expects date strings like
        1/5/15
        12/10/2015
        02/03/14
    """
    zero_pad = lambda x: "0{}".format(x) if len(x) == 1 else x
    cleaned_up = ds.strip().replace('/', '-')
    month, day, year = cleaned_up.split('-')
    if len(year) == 2:
        year = '20{}'.format(year)
    return "{0}-{1}-{2}".format(year, zero_pad(month), zero_pad(day))
