#!/usr/bin/python

### Libraries for ofxclient, since some code is copied from there.
import ofxclient
from ofxclient import config
from ofxclient.util import combined_download

### Libraries for my code
import ofxparse
import argparse
import re
import csv
import sys
import os
import time
import requests
import StringIO
import timestring
import mintapi
import datetime
import glob
from yahoo_finance import Currency

### Configuration constants
mypath = os.path.realpath(__file__).replace('dodown.py', '')
execfile(mypath + 'private.py')
balance = {}
datethresh = timestring.Date(str(DOWNLOAD_DAYS) + " days ago").date

# Start the Mint fetch so that we can get to it later.
if MINT_USERNAME:
  mint = mintapi.Mint(MINT_USERNAME, MINT_PASSWORD)
  mint.initiate_account_refresh()

# Custom scrapers: Yahoo currencies, Kitco precious metals, TRS Retirement
for curr in YAHOO_CURRENCIES:
  balance[curr] = float(Currency(curr).get_ask())

if KITCO_PMS:
  r = requests.get("http://www.kitco.com/market/")
  kitcosep = ".*\n *<td>([^<]*)"
  for pm in KITCO_PMS:
    matches = re.search(pm + (kitcosep*4), r.text)
    balance[pm] = matches.group(3)

if TRS_USERNAME:
  url = "https://ddol.divinvest.com/ddol/util/login.html?submitted=true"
  payload = {"username": TRS_USERNAME, "fpassword": "Password",
             "password": TRS_PASSWORD,
             "signOutURI": "https://my.trsretire.com/webportal/ah/index.html",
             "submit": "Sign In"}
  r = requests.post(url, data=payload)
  matches = re.findall("(TT[\d ]+)\r\n.*\n.*\n.*\n[^\$]*\$([\d\.,]*)", r.text)
  balance['TRS'] = sum(map(lambda x: float(x[1].replace(',','')), matches))

### The transactions file that we're going to write everywhere
transfile = open('trans.csv', 'w')
transwrite = csv.writer(transfile, delimiter=',', quotechar='"', 
                        quoting=csv.QUOTE_MINIMAL)

### Google Sheets data fetcher
googlebase = "https://docs.google.com/feeds/download/spreadsheets/Export?key="

# On the old-generation (key starts with 0), this export function wants a
# Google sign-in. The /spreadsheets/d/(key) approach also doesn't work with
# those sheets, so I created an account exclusively for fetching. Yay, Google.
headers = {'Cookie': GOOGLE_COOKIE}

for acct in googleaccts:
  r = requests.get(googlebase + googleaccts[acct]["key"] +
                   "&exportFormat=csv&gid=" + googleaccts[acct]["gid"],
                   headers=headers)
  datecol = googleaccts[acct]["datecol"]
  inv = -1 if googleaccts[acct]['isinv'] else 1
  match = re.match("^text/csv", r.headers['content-type'])
  if match is not None:
    rcsv = StringIO.StringIO(r.text)
    rcsvr = csv.reader(rcsv, delimiter=',', quotechar='"')
    tmp = ''
    for row in rcsvr:
      if row[datecol]:
        try:
          if timestring.Date(row[datecol]) >= datethresh:
            transwrite.writerow([timestring.Date(row[datecol]), acct, '', '', 
                                 '', '', row[googleaccts[acct]["descrcol"]], 
                                 row[googleaccts[acct]["amtcol"]], ''])
          tmp = row[googleaccts[acct]['col']]
        except timestring.TimestringInvalid:
          if row[datecol] != "Date":
            print "Illegal date " + row[datecol]
    balance[acct] = float(tmp.replace('$', '').replace(',', '')) * inv
  else:
    print 'Failed: got wrong content-type ' + r.headers['content-type']
    sys.exit(1)

### Use the age of the download.ofx file to decide whether or not we want
### to do a new download.
dodownload = 1
if os.path.isfile('download.ofx'):
  if time.time() < (os.path.getmtime('download.ofx')+MAX_OFX_AGE):
    dodownload = 0

# Set the config variables outside the if statement because we use them later
# for getting the config's description, which is not embedded in the .ofx file.
# Boo. Shamelessly ripped from cli.py in ofxclient.
GlobalConfig = config.OfxConfig()
accounts = GlobalConfig.accounts()

# Shamelessly ripped from cli.py in ofxclient. I've chosen to write a file
# and then read it for fewer network accesses while debugging.
if dodownload:
  print "Downloading..."
  ofxdata = combined_download(accounts, days=DOWNLOAD_DAYS)
  ofxfile = open('download.ofx', 'w')
  ofxfile.write(ofxdata.read())
  ofxfile.close()

# Loop through the accounts in the downloads, export transactions, and
# determine their value.
ofxfiles = glob.glob("*.ofx")
for fname in ofxfiles:
  ofx = ofxparse.OfxParser.parse(file(fname))
  for acct in ofx.accounts:
    acctnum = "Unknown account number " + acct.number + " " + str(acct)
    for cfgacct in accounts:
      if cfgacct.number == acct.number:
        acctnum = str(cfgacct.description)
    if acct.number in ACCTNUMMAP: acctnum = ACCTNUMMAP[acct.number]
    if type(acct.statement) == ofxparse.ofxparse.InvestmentStatement:
      balance[acctnum] = sum(map(lambda x: x.units*x.unit_price,
                                 acct.statement.positions))
    else:
      balance[acctnum] = acct.statement.balance;
      for trans in acct.statement.transactions:
        if trans.date >= datethresh:
          transwrite.writerow([trans.date, acctnum, trans.checknum, trans.memo,
                               trans.mcc, trans.sic, trans.payee, trans.amount,
                               trans.type])

### Mint. At the bottom to let the earlier fetch complete.
if MINT_USERNAME:
  minttrans = mint.get_transactions()
  mintaccts = mint.get_accounts()
  for acct in mintaccts:
    inv = -1 if (acct["klass"] == 'credit') or (acct["klass"] == 'loan') else 1
    balance[acct["name"].replace(' ', '')] = acct["currentBalance"] * inv
    age = datetime.datetime.now()-acct["lastUpdatedInDate"]
    if age.total_seconds() > 3600:
      print "Warning: "+acct["name"]+" age is "+(str(age).split('.',2)[0])
  for trans in minttrans.values:
    if trans[0] >= datethresh:
      date = (str(trans[0].month) + "/" + str(trans[0].day) + "/" +
              str(trans[0].year))
      inv = -1 if trans[4] == 'debit' else 1
      transwrite.writerow([date, trans[6], '', trans[1], '', trans[5],
                           trans[2], trans[3]*inv, trans[4]])

# Write out the assets csv
templatefile = open(mypath + 'template.csv')
templatecsvr = csv.reader(templatefile, delimiter=',', quotechar='"')
assetfile = open('assets.csv', 'w')
assetcsvw = csv.writer(assetfile, delimiter=',', quotechar='"', 
                       quoting=csv.QUOTE_MINIMAL)
for row in templatecsvr:
  for i in range(len(row)):
    rowaccts = row[i].split('+')
    count = 0
    for j in range(len(rowaccts)):
      if rowaccts[j] in balance:
        tmp = balance[rowaccts[j]]
        del balance[rowaccts[j]]
        rowaccts[j] = tmp
        count = count+1
    if count == len(rowaccts):
      row[i] = sum(map(lambda x: float(x), rowaccts))
    elif count != 0:
      print "Warning: partial match. " + row[i] + " -> " + str(rowaccts)
  assetcsvw.writerow(row)

for key in balance:
  print "{:15s}".format(key) + " " + "{:10.2f}".format(balance[key])
