RUNENV="prod"
DEBUG=False
IS_DEVELOPMENT_MACHINE=False

ALLOWED_HOSTS = ['<HOST SERVER IP OR NAME>']

#Add here any possible legitimate origin (wildcard do NOT work with credentials too)
CORS_ALLOWED_ORIGIN_REGEXES = [
  #r"^http://localhost.*$",               #comment out when not needed for debugging
  r"^<HOST SERVER IP OR NAME>:'<HOST SERVER PORT>$",
]

CSRF_TRUSTED_ORIGINS = [
   #"http://localhost:4000",             #comment out when not needed for debugging
   "https://'<HOST SERVER IP OR NAME>:'<HOST SERVER PORT>",
]

from corsheaders.defaults import default_headers

CORS_ALLOW_HEADERS = (
    *default_headers,
    'origin',
    'accept-encoding',
)

# For Djoser EMails
#DEFAULT_FROM_EMAIL = ""         # This is actually a Django global setting
#DOMAIN = ""
#SITE_NAME = ""
