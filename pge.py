import re

from download_helper import GetResponseSoup, format_datestring
from settings import DROPBOX_DOCUMENTS, PGE_USERNAME, PGE_PASSWORD

username = PGE_USERNAME
password = PGE_PASSWORD
SAVE_PATH = DROPBOX_DOCUMENTS + "/Invoices/PGE"

fields = {
    'USER': username,
    'PASSWORD': password,
    'REALMOID': '06-40da262c-b9d7-00ef-0000-28ff000028ff',
    'TARGET': 'https://www.pge.com/myenergyweb/appmanager/pge/customer',
    'SMAUTHREASON': 0,
    'FCC': 'DEFAULT',
    'PROTOCOL': 'DEFAULT'
}

pge = GetResponseSoup('https://www.pge.com/eum/login', fields)

# Get to the statements page
pge.update('https://www.pge.com/myenergyweb/appmanager/pge/customer?_nfpb=true&_pageLabel=BillingPaymentHistory&_nfls=false')


transaction_table = pge.soup.find('table', {'id': 'transaction-history-table'})
downloadable_transaction_rows = [
    dict(
        filename=format_datestring(row.find('span', text=re.compile(r'\d{2}/\d{2}/\d{2}'))),
        url=row.find('a', {'class': 'download-pdf-lft'})['href']
    )
    for row in transaction_table.findAll('tr')
    if row.find('a', {'class': 'download-pdf-lft'}, text='Download')
]

pge.download_invoices(downloadable_transaction_rows, SAVE_PATH)
