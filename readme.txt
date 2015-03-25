This is a little personal finance downloader that I built for myself. 
It supports the following sources of data:

1. Any bank that supports OFX connection (using the ofxclient package).
   Set them up in ofxclient command-line and dodown.py will download them.
2. Mint (using mintapi). Set your username and password in private.py.
3. Transamerica Retirement Services (balances only, by screen scraping).
   Set your username and password in private.py.
4. Any .ofx files in the current working directory, for banks that support
   neither OFX nor Mint.
5. Any accounts you keep using Google Sheets (via Google Drive csv export).
   Requires the key for that spreadsheet, the gid of the worksheet, and the
   column numbers of columns that hold relevant information. Older 
   generation spreadsheets (with key beginning with a 0) require a Google 
   account to download; extract your Google cookie and put it in private.py.
6. Currency information from Yahoo (via the yahoo_finance package) and
   precious metals prices from Kitco (by screen scraping)

It then exports two csv files:
1. trans.csv, which contains all transactions in the last DOWLOAD_DAYS
   and perhaps some extraneous ones (thanks to Mint and the .ofx files).
2. assets.csv, generated from the template template.csv. The name of each
   account can be placed in the template, and they are replaced exactly once
   with that account's current balance or value. (Some caveats here: for 
   example, Mint account names are stripped of spaces.)
It further prints any accounts that are not listed in the template.
