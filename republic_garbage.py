import urllib
import re
from urlparse import urlparse, urlunparse, parse_qs

from download_helper import GetResponseSoup
from settings import APARTMENT_UTILITIES_PATH, RG_USERNAME, RG_PASSWORD

username = RG_USERNAME
password = RG_PASSWORD
SAVE_PATH = APARTMENT_UTILITIES_PATH + "Garbage"

login_url = "https://secure.republiconline.com:443/pkmslogin.form"

fields = {
    r'username': username,
    r'password': password,
    r'login-form-type': r'pwd',
}

rg = GetResponseSoup(login_url, fields)
rg.update('https://secure.republiconline.com/secureeportal/_layouts/fissinglesignon.aspx')

authTkn = rg.soup.find('input', {'name': 'authTkn'})['value']
keyTkn = rg.soup.find('input', {'name': 'keyTkn'})['value']

fields = {
    r'slchannel': 'ALWRSA',
    r'client': '701122300',
    r'unitCode': 'ALW',
    r'type': 'ApplicationMenu',
    r'enc': 'web',
    r'authTkn': authTkn,
    r'keyTkn': keyTkn
}

rg.update('https://secure3.billerweb.com/alw/inetSrv', fields)

# At this point, we're at the page where the invoices are listed.
# Let's find the invoice IDs


def clean_due_date(s):
    cleaned_up = s.strip().replace('/', '-').replace('Due: ', '')
    # now looks like MM-DD-YYYY
    month, day, year = cleaned_up.split('-')
    return "{0}-{1}-{2}".format(year, month, day)


def invoice_info(link):
    doc_id_search = re.compile(r'viewDocument\(\'(\d+)\'')
    find_id = doc_id_search.search(link['href'])
    doc_name = "{} {}".format(clean_due_date(link.contents[-1]),
                              link.contents[0].strip().replace(': ', '-'))
    return dict(
        filename=doc_name,
        id=find_id.group(1)
    )

invoice_links = rg.soup.findAll('a', href=re.compile('viewDocument'))
doc_ids = map(invoice_info, invoice_links)

sessionHandle = rg.soup.find('input', {'name': 'sessionHandle'})['value']
client = rg.soup.find('input', {'name': 'client'})['value']


for invoice in doc_ids:
    fields = {
        r'sessionHandle': sessionHandle,
        r'type': 'UserService',
        r'action': 'ViewDocument',
        r'client': client,
        r'logoutUrl': '',
        r'operation': "search",
        r'startPos': '0',
        r'newBean': '',
        r'mode': '',
        r'documentId': invoice['id'],
        r'accountServiceId': '4',
        r'documentSetId': '',
        r'invoiceNumber': '',
        r'selectedAccount': '',
        r'accountSelection': '',
        r'payDocumentId': '',
        r'accountSelection': 'allActiveAccounts',
    }

    rg.update('https://secure3.billerweb.com/alw/inetSrv', fields)

    # src = rg.soup.find('frame')['src'].replace('/alw/inetSrv', '')
    src = rg.soup.find('frame')['src']
    parsed_url = urlparse(src)
    parsed_query = parse_qs(parsed_url.query)

    to_open = 'https://secure3.billerweb.com/alw/inetSrv/document.pdf'
    fields = {
        'action': 'ShowPdf',
        'type': parsed_query['type'][0],
        'client': parsed_query['client'][0],
        'sessionHandle': parsed_query['sessionHandle'][0],
        'hasToc': 'false',
        'beginPage': '1',
        'endPage': '2',
        'docId': invoice['id']
    }

    # there has to be a cleaner way to do this
    url_to_open = urlunparse(list(urlparse(to_open))[:4] + [urllib.urlencode(fields)] + [''])
    invoice['url'] = url_to_open

rg.download_invoices(doc_ids, SAVE_PATH)
