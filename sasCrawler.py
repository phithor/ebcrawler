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

def fetch_price(From, To, outDate, inDate, booking_type, passengers, tokenjson="not"):
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
    url = baseurl + 'to={0}&from={1}&outDate={2}&inDate={3}&adt={4}&chd=0&inf=0&yth=0&bookingFlow={5}&pos=no&channel=web&displayType=upsell'.format(To, From, outDate, inDate, str(passengers) ,booking_type)

    if tokenjson != "not":  #Not needed to get an offer
        token = tokenjson['access_token'] 
        sessionid = tokenjson['customerSessionId'] 

    r = requests.get(url)
    rjson = r.json()
    rjson["parameters"] = {"from": From,
                           "to": To,
                           "outdate": outDate,
                           "indate": inDate,
                           "booking type": booking_type,
                           "passengers": passengers}
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
     
        ### -- Tabs are not working at the moment(always NA)
        ###    kept for potential future use
##        outbound = results["tabsInfo"]["outboundInfo"]
##        inbound = results["tabsInfo"]["inboundInfo"]
##        def tabsInfo(boundinfo):
##            for i in range(len(boundinfo)):
##                if "price" in boundinfo[i]:
##                    if boundinfo[i]['price'] == "NA":
##                        print("Date: ", boundinfo[i]["date"], " Price: ", "No Avilability")
##                    elif boundinfo[i]['price'] != "NA":
##                        print("Date: ", boundinfo[i]["date"], " Price: ", str(boundinfo[i]["price"]))
##                else:
##                    print("Date: ", boundinfo[i]["date"], " Price: ", str(int(boundinfo[i]["points"])), "points")
##        print("Availability closest days out:" )
##        tabsInfo(outbound)
##        print("Availability closest days in:" )
##        tabsInfo(inbound)
            

        ### Define parse functions that are not lambdable

        def parse_via(x):
            if pd.isnull(x).all() == False:
                stop_str = ''
                counter = 0
                for i in range(len(x)):
                    if counter > 0:
                        stop_str += ','
                    counter += 1
                    stop_str += x[i]['code']
            else:
                stop_str = "-"
                
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

        
        def parse_aircraft(x):
            aircraft = "" #Empty string
            counter = 0
            for i in range(len(x)):
                if counter > 0:
                    aircraft += ', '
                aircraft += x[i]["airCraft"]["name"].split("(")[0] #Add to string with sharklet/winglet parentheses
                counter += 1
            return aircraft

        def parse_carrier(x):
            carrier = "" #Empty string
            counter = 0
            for i in range(len(x)):
                if counter > 0:
                    if carrier != x[i]["operatingCarrier"]["code"]: #Do not add to string if it is the same name
                        carrier += ', '
                        carrier += x[i]["operatingCarrier"]["code"]
                else:
                    carrier += x[i]["operatingCarrier"]["code"] #Add to string
                    counter += 1 # Only really needed once
            return carrier
                
        def to_df(flights):
            

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
            df_new['Carrier(s)'] = df_flights.segments.apply(parse_carrier)
            df_new['Cabin Classes'] = df_flights.cabins.apply(lambda x: ','.join(str(x) for x in list(x.keys())) if x != 'NaN' else '-NA-')
            df_new['avlSeats'] = df_flights.lowestFares.apply(parse_fares)
            df_new['Points'] = df_flights.lowestFares.apply(parse_prices)
            df_new['Aircrafts'] = df_flights.segments.apply(parse_aircraft)
            df_new.head()

            return df_new
        
        ### If the route direction exists, divide resulsts dict in the two halves and parse result to df

        if "outboundFlights" in results:
            outflights = results["outboundFlights"]
            print("Number of results Out: " +str(len(outflights)))
            df_outflights = to_df(outflights)
        else:
            print("No available flights on the outbound date")
            df_outflights = "empty"
        
        
        if "inboundFlights" in results:
            inflights = results["inboundFlights"]
            print("Number of results In: " +str(len(inflights)))
            df_inflights = to_df(inflights)
        else:
            print("No available flights on the inbound date")
            df_inflights = "empty"
        
        if "errors" in results:
            errors = results["errors"]
            print("The following errors were returned:")
            for i in range(len(errors)):
                print(str(i)+":",errors[i]['errorMessage'])

        return df_outflights, df_inflights



#def scan_availability(From, To, FromDate, ToDate):
#    date_range = pd.date_range(pd.datetime.today(), '2019-01-04')
