DOWNLOAD_DAYS = 45
MAX_OFX_AGE   = 36000

MINT_USERNAME = 
MINT_PASSWORD = 

TRS_USERNAME = 
TRS_PASSWORD = 

YAHOO_CURRENCIES = [] # e.g., EURUSD
KITCO_PMS        = [] # e.g., PLATINUM

# Google sheets accounts. Get the key from the thing following
# key= or /d/(blah) and the gid from the editing URL.
# Isinv should be true if this is a sheet describing what you owe, and false
# if it is a sheet describing your assets.
# There are four columns that we use: datecol holds the date, descrcol holds
# the description of the transaction (for transaction export), amtcol holds the
# delta amount, and col holds the total. The sheet assumes that the col column
# in the last row that has a non-empty date represents the current balance
# (in other words, that the )
googleaccts = {"name": {"key": "from share URL",
                        "gid": "from edit URL", "isinv": 1,
                        "col": 3, "datecol": 0, "descrcol": 1, "amtcol": 2}}

# Log in to your google account in Chrome, go to dev tools, and copy the cookie
# from there.
GOOGLE_COOKIE = 
