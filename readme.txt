Quick Start:

1. Get all of your accounts in ofxclient or mint. Any that you can't get,
   manually download an .ofx into the folder from which you run dodown.py
2. Copy public.py to private.py and update your mint username and password.
   Also, to customize the display names:
   a. For accounts on mint, edit the display name in mint.
   b. For accounts with manual .ofx download, edit ACCTNUMMAP to map the
      account number to the name.
   c. For accounts on ofxclient, either (i) edit the "description" for each
      account in ofxclient.ini, or (ii) edit ACCTNUMMAP
3. Touch template.csv in the same folder as dodown.py.
4. Run dodown.py. It will print out the name of each account and its balance.
5. If you want an assets.csv, edit template.csv to include the names of any
   accounts you want listed in assets.csv. Each account will appear in 
   assets.csv just as it appears in template.csv. Any text that doesn't match
   an account name will be passed unchanged. You can add multiple accounts
   together with +. This also means that + isn't usable in account names.
6. If you already have an Excel spreadsheet that does some computation, you can
   paste the resulting assets.csv into that spreadsheet by using Paste Special,
   Values, Ignore Blanks.

--------------------------------------------------------------------------------
This is a little personal finance downloader that I built for myself. 
It supports the following sources of data:

1. Any bank that supports OFX connection (using the ofxclient package).
   Set them up in ofxclient command-line and dodown.py will download them.
2. Mint (using mintapi). Set your username and password in private.py.
3. Transamerica Retirement Services (balances only, by screen scraping).
   Set your username and password in private.py.
4. Any .ofx files in the current working directory, for banks that support
   neither OFX nor Mint. If your filesystem is case sensitive, they MUST
   be named .ofx, NOT .OFX. They cannot be named .qfx.
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
   example, Mint account names are stripped of spaces.) dodown.py supports
   joining multiple account names with a + (but therefore does not support
   using a + in an account name). If multiple account names are joined with 
   a +, but only some of those names are known, it will not replace any of 
   the names, but will rather print a warning.

It further prints any accounts that are not listed in the template.

v0.1 (3/25/15): Initial release
v0.2 (3/26/15): Support for + in template.csv. Added ACCTNUMMAP for downloaded
		OFX files. Made everything except ofxclient conditional on the
		configuration file parameters.
v0.3 (3/28/15): Better README, fixed a bug in Google Sheets.
