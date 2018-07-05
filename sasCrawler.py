#!/usr/bin/python3

import sys
import requests
import argparse
import getpass
import csv
from datetime import datetime


def getAccessToken(eb, pw):
    r = requests.post('https://api.flysas.com/authorize/oauth/token',
                      data={'grant_type': 'password', 'username': eb, 'password': pw},
                      headers={'Referer': 'https://www.sas.no/',
                               'Origin': 'https://www.sas.no',
                               'Authorization': 'Basic U0FTLVVJOg==',
                               'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                               'accept': 'application/json, text/plain, */*'
                      },
                      )
    rjson = r.json()
    return rjson

def fetch_page(pageno, tokenjson):
    print("Fetching page {0}".format(pageno))
    token = tokenjson['access_token']
    sessionid = tokenjson['customerSessionId']
    r = requests.get('https://api.flysas.com/customer/euroBonus/getAccountInfo?pageNumber={0}&customerSessionId={1}'.format(pageno, sessionid),
                    headers={'Authorization': token,
                             'Referer': 'https://www.sas.se/',
                             'Origin': 'https://www.sas.se',
                             'Accept': 'application/json, text/plain, */*',
                    },
                    )
    if r.status_code != 200:
        print("Failed to get page {0}:".format(pageno))
        print(r.text)
        sys.exit(1)

    return r.json()['euroBonus']

def fetch_price(From, To, Return=True, outDate, inDate, Award):
    ''' Fetch prices from SAS API

        fetch_price(From, To, Return=True, outDate, inDate, Award)
        
        example url: (parameteres in new line for readability)
        
        https://api.flysas.com/offers/flights?
        to=AGP&
        from=OSL&
        outDate=20180715&
        inDate=20180729&
        adt=2&
        chd=0&
        inf=0&
        yth=0&
        bookingFlow=revenue&
        pos=no&
        channel=web&
        displayType=upsell
    '''

    baseurl = 'https://api.flysas.com/offers/flights?'
    url = baseurl + 'to={0}&from={1}&outDate={2}&inDate={3}&adt={4}&chd=0&inf=0&yth=0&bookingFlow=revenue&pos=no&channel=web&displayType=upsell

    

    r = requests.get(



destination_lists = [('CPH','NRT'),
                     ('ARN','EWR'),
                     ('ARN','HKG'),
                     ('CPH','HKG'),
                     ('ARN','LAX'),
                     ('ARN','ORD'),
                     ('CPH','ORD'),
                     ('CPH','BOS'),
                     ('CPH','PVG'),
                     ('CPH','EWR'),
                     ('CPH','IAD'),
                     ('CPH','MIA'),
                     ('CPH','PEK'),
                     ('CPH','SFO'),
                     ('OSL','EWR'),
                     ('OSL','MIA')]
                     

