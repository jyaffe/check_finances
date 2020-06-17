# https://github.com/monzo/reference-receipts-app/blob/master/config-example.py

# Register your third party application on http://developers.monzo.com by logging in with your personal 
# Monzo account. Copy this file into config.py, and enter your credentials into the file.
MONZO_CLIENT_ID = "oauth2client_YOUR_CLIENT_ID_HERE"
MONZO_CLIENT_SECRET = "mnzpub.YOUR_CLIENT_SECRET_HERE"

# Configurations you should not need to change.
MONZO_OAUTH_HOSTNAME = "auth.monzo.com"
MONZO_API_HOSTNAME = "api.monzo.com"
MONZO_RESPONSE_TYPE = "code"
MONZO_AUTH_GRANT_TYPE = "authorization_code"
MONZO_REFRESH_GRANT_TYPE = "refresh_token"
MONZO_OAUTH_REDIRECT_URI = "http://127.0.0.1:21234/" # For receiving the auth code, not currently used.
MONZO_CLIENT_IS_CONFIDENTIAL = True 
# If your application runs on a backend server with client secret hidden from user, it should be registered 
# as confidential and will have the ability to refresh access tokens.

# The following variables are set by the oauth2.py script and default as None
MONZO_ACCESS_TOKEN = None
MONZO_REFRESH_TOKEN = None
MONZO_USER_ID = None
