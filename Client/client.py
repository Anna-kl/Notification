import requests
import re
import os


myheaders={'Content-type':'application/json', 'Accept':'application/json'}
# data= {"Username": os.environ['Username'],
#        "Password": os.environ['password'], "RememberLogin": False,
#      "ReturnUrl":os.environ['return_url']}


data= {"Username": 'weather',
       "Password": 'weather', "RememberLogin": False,
     "ReturnUrl":'/connect/authorize/callback?client_id=js&redirect_uri=https://monitoring.gpn.supply/callback.html&response_type=id_token token&scope=openid profile api&state=4ed6893afaf744fe9cfd6663a670adf0&nonce=304a3e4804db4966872e6a9d4e07f005' }

def get_token():
    params = {'button': 'login'}
    #r=requests.post('https://core.gpn.supply/Account/Login/',  verify=False, data=data, params=params)
    r = requests.post('https://test.gpn.supply/Account/Login/', verify=False, data=data, params=params)
    r=requests.get(r.url, verify=False)
    r = requests.get(r.url, verify=False)
    params = r.url.split('#')[1]
    d = dict(re.findall(r'([^=\&]*)=([^\&]*)', params))
    return d
