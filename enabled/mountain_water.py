import re

from lib import GetResponseSoup, format_datestring
from lib import APARTMENT_UTILITIES_PATH, MW_USERNAME, MW_PASSWORD

SAVE_PATH = APARTMENT_UTILITIES_PATH + "/Water"

username = MW_USERNAME
password = MW_PASSWORD
login_url = "http://myaccount.mtnwater.com/UserLogin.aspx"


def main():
    # Extract view_state and event_validation variables:
    field_names = [
        r'__EVENTARGUMENT',
        r'__VIEWSTATE',
        r'__EVENTVALIDATION',
        r'__VIEWSTATEGENERATOR',
        r'__VIEWSTATEENCRYPTED',
        r'__EVENTVALIDATION',
    ]

    fields = {
        r'dnn$ctr487$Login$Login_DNN$txtUsername': username,
        r'dnn$ctr487$Login$Login_DNN$txtPassword': password,
        r'__ASYNCPOST': 'true',
        r'ScrollTop': '301',
        r'ScriptManager_TSM' : ';;System.Web.Extensions, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35:en:f319b152-218f-4c14-829d-050a68bb1a61:ea597d4b:b25378d2;Telerik.Web.UI, Version=2012.2.724.35, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en:3fe22950-1961-4f26-b9d4-df0df7356bf6:16e4e7cd:f7645509:ed16cbdc',
        r'StylesheetManager_TSSM': ';Telerik.Web.UI, Version=2012.2.724.35, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en-US:3fe22950-1961-4f26-b9d4-df0df7356bf6:45085116:27c5704c',
        r'ScriptManager': r'dnn$ctr487$dnn$ctr487$Login_UPPanel|dnn$ctr487$Login$Login_DNN$cmdLogin',
        r'__EVENTTARGET': 'dnn$ctr487$Login$Login_DNN$cmdLogin',
        r'__dnnVariable': {"__scdoff":"1","containerid_dnn_ctr395_ModuleContent":"395","cookieid_dnn_ctr395_ModuleContent":"_Module395_Visible","min_icon_395":"/Portals/_default/Containers/eCAReDefault/ar_closemenu.gif","max_icon_395":"/Portals/_default/Containers/eCAReDefault/ar_openmenu.gif","max_text":"Maximize","min_text":"Minimize"},
        r'RadAJAXControlID': r'dnn_ctr487_Login_UP',
    }

    # Login page (but not logging in)
    mw = GetResponseSoup(login_url)

    # Extract the field names from the site
    for field in field_names:
        find_field = mw.soup.find(id=field)
        fields[field] = find_field['value'] if find_field else ''

    # Actually log in
    mw.update(login_url, fields)

    mw.update('http://myaccount.mtnwater.com/Home.aspx')

    transaction_table = mw.soup.find('table', {'id': 'dnn_ctr479_BillingHistory_GridView1'})
    transaction_rows = [row for row in transaction_table.findAll('tr') if not row.find('th')]

    downloadable_transactions = [
        dict(
            filename=format_datestring(row.find('a', attrs={'href': re.compile(r'^javascript')}).text),
            url=row.find('a', {'href': re.compile(r'onlinebiller')})['href']
        )
        for row in transaction_rows
    ]

    mw.download_invoices(downloadable_transactions, SAVE_PATH)

if __name__ == '__main__':
    main()
