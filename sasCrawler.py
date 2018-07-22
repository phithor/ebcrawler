#!/usr/bin/python3

import sys
import requests
import argparse
import getpass
import csv
from datetime import datetime
import pandas as pd


def getAccessToken(eb, pw):
    ''' Get access token to poll api '''
    r = requests.post('https://api.flysas.com/authorize/oauth/token',
                      data={'grant_type': 'password', 'username': eb, 'password': pw},
                      headers={'Referer': 'https://www.sas.no/',
                               'Origin': 'https://www.sas.no',
                               'Authorization': 'Basic U0FTLVVJOg==',
                               'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                               'accept': 'application/json, text/plain, */*'
                      },
                      )
    if r.status_code != 200:
        print("Failed to log in:")
        print(r.text)
        sys.exit(1)

    rjson = r.json()
    return rjson


def fetch_page(pageno, tokenjson):
    ''' Fetch page of EB history '''
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

def fetch_price(From, To, outDate, inDate, booking_type, tokenjson="not"):
    ''' Fetch prices from SAS API:

        fetch_price(From, To, outDate, inDate, booking_type)
        
        example url: (parameteres in new line for readability)
        
        https://api.flysas.com/offers/flights?
        to="Airport Code"&
        from="Airport Code"&
        outDate=20180715& #YYYYMMDD
        inDate=20180729& #YYYYMMDD
        adt=2&
        chd=0&
        inf=0&
        yth=0&
        bookingFlow="points" / "revenue" /"star"&
        pos=no&
        channel=web&
        displayType=upsell
    '''

    
    
    baseurl = 'https://api.flysas.com/offers/flights?'
    url = baseurl + 'to={0}&from={1}&outDate={2}&inDate={3}&adt={4}&chd=0&inf=0&yth=0&bookingFlow={5}&pos=no&channel=web&displayType=upsell'.format(To, From, outDate, inDate, "2" ,booking_type)

    if tokenjson != "not":  #Not needed to get an offer
        token = tokenjson['access_token'] 
        sessionid = tokenjson['customerSessionId'] 

    r = requests.get(url)
    rjson = r.json()
    return rjson


eb_destination_list = [('CPH','NRT'),
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
                     

# Works
#a = fetch_price("OSL", "SIN", "20181101", "20181108", "star")

def parse_results(results):

    ### Divide reulsts dict in the two halves
    outflights = results["outboundFlights"]
    inflights = results["inboundFlights"]

    print("Number of results Out: " +str(len(outflights)))
    print("Number of results In: " +str(len(inflights)))

    ### Define parse functions that are not lambdable

    def parse_via(x):
        stop_str = ''
        counter = 0
        for i in range(len(x)):
            if counter > 0:
                stop_str += ','
            counter += 1
            stop_str += x[i]['code']
            
        return stop_str

    def parse_fares(x):
        fare_keys = list(x.keys())
        avl_seats = ""
        counter = 0
        for i in range(len(x)):
            if counter > 0:
                avl_seats += ','
            avl_seats += str(x[fare_keys[i]]['avlSeats'])
            counter += 1
        return avl_seats

    def parse_prices(x):
        fare_keys = list(x.keys())
        prices = ""
        counter = 0
        for i in range(len(x)):
            if counter > 0:
                prices += ','
            prices += str(int(x[fare_keys[i]]['points']))
            counter += 1
        return prices

    def to_df(flights):
        #df3 = df_in.copy()

        df_flights = pd.DataFrame.from_dict({(i): flights[i] 
                               for i in flights.keys()},
                           orient='index')

        df_new = pd.DataFrame(index=df_flights.index.copy())
        df_new['origin'] = df_flights.origin.apply(lambda x: x["code"])
        df_new['destination'] = df_flights.destination.apply(lambda x: x["code"])
        df_new['Departure Date'] = df_flights.startTimeInLocal.apply(lambda x: x.split('T')[0])
        df_new['Departure Time'] = df_flights.startTimeInLocal.apply(lambda x: x.split('T')[1].split('.')[0])
        df_new['Arrival Date'] = df_flights.endTimeInLocal.apply(lambda x: x.split('T')[0])
        df_new['Arrival Time'] = df_flights.endTimeInLocal.apply(lambda x: x.split('T')[1].split('.')[0])
        df_new['connectionDuration'] = df_flights['connectionDuration']
        df_new['via'] = df_flights.via.apply(parse_via)
        df_new['Cabin Classes'] = df_flights.cabins.apply(lambda x: list(x.keys()) if x != 'NaN' else '-NA-')
        df_new['avlSeats'] = df_flights.lowestFares.apply(parse_fares)
        df_new['Points'] = df_flights.lowestFares.apply(parse_prices)
        df_new.head()

        return df_new

    df_outflights = to_df(outflights)
    df_inflights = to_df(inflights)

    return df_outflights, df_inflights



#def scan_availability(From, To, FromDate, ToDate):
#    
