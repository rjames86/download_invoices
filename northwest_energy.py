import re

from download_helper import GetResponseSoup
from settings import APARTMENT_UTILITIES_PATH, NWE_USERNAME, NWE_PASSWORD


def format_invoice_ds(ds):
    """assumes 20150101"""
    return "{}-{}-{}".format(ds[0:4], ds[4:6], ds[6:])


def prepare_and_download():
    # Get the invoice urls
    account_name = nwe.soup.find('option', attrs={'selected': 'selected'})['value']
    invoice_base_url = 'https://myaccount.northwesternenergy.com/NWESSP/'
    invoice_urls = map(lambda x: x['href'],
                       nwe.soup.findAll('a', attrs={'href': re.compile('^ECISBillStatement')}))

    invoice_dates = [format_invoice_ds(url.split('?')[1]) for url in invoice_urls]

    transaction_list = [dict(url=invoice_base_url + url, filename="{} {}".format(file_name, account_name))
                        for url, file_name in zip(invoice_urls, invoice_dates)]

    nwe.download_invoices(transaction_list, save_path)


def extract_fields(fields, field_names):
    # Extract the field names from the site
    for field in field_names:
        find_field = nwe.soup.find(id=field)
        fields[field] = find_field['value'] if find_field else ''


username = NWE_USERNAME
password = NWE_PASSWORD
save_path = APARTMENT_UTILITIES_PATH + '/Electric'
login_url = "https://myaccount.northwesternenergy.com/NWESSP/index.aspx"
billhistory_url = 'https://myaccount.northwesternenergy.com/NWESSP/BillHistory.aspx'

field_names = [
    "__EVENTTARGET",
    "__VIEWSTATE",
    "__EVENTARGUMENT",
    "__VIEWSTATEGENERATOR",
    "__EVENTVALIDATION",
    "__LASTFOCUS",
]

fields = {
    "ctl00$StaticContentWebView1$staticContentLocation": "StaticContent/NWEHeaderIndex.htm",
    "ctl00$body_content$txtUsername": username,
    "ctl00$body_content$txtPassword": password,
    "ctl00$StaticContentWebView2$staticContentLocation": "StaticContent/NWEFooterIndex.htm",
    "ctl00$body_content$btnLogin.x": "25",
    "ctl00$body_content$btnLogin.y": "11",

}

nwe = GetResponseSoup(login_url)

# Extract the field names from the site
extract_fields(fields, field_names)

# Logging in
nwe.update(login_url, fields)

# Go to Payments page where the invoices are
nwe.update(billhistory_url)
prepare_and_download()

# Get all the account numbers on my account
nwe.update(billhistory_url)
account_numbers = [o['value'] for o in nwe.soup.find('select', attrs={'name': 'ctl00$AccountSummaryHeaderControl1$headerAccountSelector'}).findAll('option') if o['value'] != '3168266-9']
field_names.append("ctl00$body_content$AccountSummaryDynamicLinksView1$hdSpeedPayAccountNumber")
field_names.append("ctl00$body_content$AccountSummaryDynamicLinksView1$hdSpeedPayState")

for account_number in account_numbers:
    if nwe.url != billhistory_url:
        nwe.update(billhistory_url)

    fields = {
        "ctl00$StaticContentWebView1$staticContentLocation": "StaticContent/NWEHeader.htm",
        "TC08BCDB1053_ctl00_ctl00_siteMapControl_customnavigation_ClientState": "",
        "ctl00$AccountSummaryHeaderControl1$headerAccountSelector": account_number,
        "ctl00$body_content$AccountSummaryDynamicLinksView1$hdSpeedPayURL:https": "//paynow7.speedpay.com/northwestern/index.asp",
        "ctl00$body_content$StaticContentWebView1$staticContentLocation": "StaticContent/BillViewRequirements.htm",
        "ctl00$StaticContentWebView2$staticContentLocation": "StaticContent/NWEFooter.htm"
    }

    # Extract the field names from the site
    extract_fields(fields, field_names)

    nwe.update(billhistory_url, fields)
    prepare_and_download()
