# https://github.com/monzo/reference-receipts-app/blob/master/oauth2.py

import sys
import uuid
import base64
import urllib.parse as urllib
import json

import requests

from utils import error
from utils import refresh_config
from utils import reset_config

# A very simple OAuth2 client for the Monzo Third Party API. You presently cannot use
# this API for public applications, as only a small amount of users you nominate can
# authorise your application to their Monzo account with this API. This API however
# grants access to more resource than the AISP API for regulated AISPs including receipts.

try:
    import config
except:
    print("Cannot import config, register your application on developers.monzo.com, \
copy config-example.py to config.py, and configure your client credentials.")
    sys.exit(1)

class OAuth2Client:
    ''' This auth flow implements the process of acquiring an access token from the
        Monzo Third Party Developer API, as described in 
        https://docs.monzo.com/#acquire-an-access-token
    '''
    
    def __init__(self):
        self._user_id = ""
        self._is_confidential_client = config.MONZO_CLIENT_IS_CONFIDENTIAL
        # Your client should only be confidential if it is a backend application, with
        # OAuth secret hidden from the user.
        self._oauth_state = uuid.uuid4().hex
        # OAuth state uses a randomised alphanumeric state to protect the client  
        # browser from cross site forgery attacks. While we don't need it as a 
        # command-line application, we still send a randomised state nevertheless 
        # to demonstrate.
        self._access_token = config.MONZO_ACCESS_TOKEN
        self._refresh_token = config.MONZO_REFRESH_TOKEN
        self._user_id = config.MONZO_USER_ID
        
    
    def start_auth(self):
        ''' Builds an auth URL to be used to initiate OAuth2 flow on the web OAuth portal. '''
        
        oauth2_GET_params = {
            "client_id": config.MONZO_CLIENT_ID,
            "redirect_uri": config.MONZO_OAUTH_REDIRECT_URI,
            "response_type": config.MONZO_RESPONSE_TYPE,
            "state": self._oauth_state
        }
        request_url = "https://{}/?{}".format(config.MONZO_OAUTH_HOSTNAME,
            urllib.urlencode(oauth2_GET_params, doseq=True))
        print("Visit {} and follow email received to obtain your temporary authorization code...".format(request_url))
        self.wait_for_auth_flow()
    

    def wait_for_auth_flow(self):
        ''' Parses the temporary authorization code returned from authenticating with Email login link. '''
        
        callback_url = input("Once you have obtained the callback link by right-clicking the login button in your email and copying the link, paste your callback URL here: ").strip()
        try:
            callback = urllib.urlparse(callback_url).query
        except:
            error("Cannot parse callback URL, try again.")

        callback_qs = dict(urllib.parse_qsl(callback))
        if "code" not in callback_qs:
            error("Cannot find temporary auth code in callback URL.")
        if "state" not in callback_qs:
            error("Cannot find randomised auth state in callback URL.")
        if callback_qs["state"].strip() != self._oauth_state:
            error("Invalid randomised auth state in callback URL, did you use the most recent login link?")
        
        self._auth_code = callback_qs["code"].strip()
        self.exchange_auth_code()
    
    
    def exchange_auth_code(self):
        '''Exchanges the temporary authorization code with an access token for the application. '''
        
        if self._auth_code == "":
            error("No auth code, have you completed intial auth flow.")

        oauth2_POST_params = {
            "grant_type": config.MONZO_AUTH_GRANT_TYPE,
            "client_id": config.MONZO_CLIENT_ID,
            "client_secret": config.MONZO_CLIENT_SECRET,
            "redirect_uri": config.MONZO_OAUTH_REDIRECT_URI,
            "code": self._auth_code,
        }
        request_url = "https://{}/oauth2/token?".format(config.MONZO_API_HOSTNAME)
        response = requests.post(request_url, data=oauth2_POST_params)
        if response.status_code != 200:
            error("Auth failed, bad status code returned: {} ({}).".format(response.status_code,
                response.text))

        response_object = response.json()
        if "access_token" in response_object:
            print("Auth successful, access token received.") 
            self._access_token = response_object["access_token"]

            if "refresh_token" in response_object:
                self._refresh_token = response_object["refresh_token"]
            else:
                self._is_confidential_client = False
                if config.MONZO_CLIENT_IS_CONFIDENTIAL:
                    print("Warning: this client is not registered as confidential, we will not be able to refresh token.")
    
            if "user_id" not in response_object:
                error("Could not retrieve user_id from token exchange response: {}.", response_object)
            self._user_id = response_object["user_id"]

        refresh_config(self._access_token,self._refresh_token,self._user_id)


    def refresh_access_token(self):
        ''' If we are a confidential client, we can refresh the access token to get a new one derived from the same OAuth
            authorisation. 
        '''
        if not self._is_confidential_client:
            error("Not a confidential client, cannot refresh access token.")

        oauth2_POST_params = {
            "grant_type": config.MONZO_REFRESH_GRANT_TYPE,
            "client_id": config.MONZO_CLIENT_ID,
            "client_secret": config.MONZO_CLIENT_SECRET,
            "refresh_token": self._refresh_token,
        }
        request_url = "https://{}/oauth2/token?".format(config.MONZO_API_HOSTNAME)
        response = requests.post(request_url, data=oauth2_POST_params)
        if response.status_code != 200:
            error("Token refreshed failed, bad status code returned: {} ({}).".format(response.status_code,
                response.text))
        
        response_object = response.json()
        if "access_token" in response_object:
            self._access_token = response_object["access_token"]
        else:
            error("No access token returned in token refresh response.")
        if "refresh_token" in response_object:
            self._refresh_token = response_object["refresh_token"]
        else:
            error("No refresh token returned in token refresh response.")
        print("Token refreshed, new access token and refresh token recorded.")

        refresh_config(self._access_token,self._refresh_token,self._user_id)
    

    def api_get(self, path, params_data):
        ''' Uses the access token to send a GET API call to the Monzo API. '''

        if path.startswith("/"):
            path = path[1:]
        response = requests.get("https://{}/{}".format(config.MONZO_API_HOSTNAME, path), 
            headers={"Authorization": "Bearer {}".format(self._access_token)},
            params=params_data)

        try:
            resp = response.json()
        except json.decoder.JSONDecodeError:
            resp = response.text

        if response.status_code != 200:
            return False, resp

        return True, resp

    
    def api_post(self, path, params_data):
        ''' Uses the access token to send a POST API call to the Monzo API. '''

        if path.startswith("/"):
            path = path[1:]
        response = requests.post("https://{}/{}".format(config.MONZO_API_HOSTNAME, path), 
            headers={"Authorization": "Bearer {}".format(self._access_token)},
            data=params_data)

        try:
            resp = response.json()
        except json.decoder.JSONDecodeError:
            resp = response.text


        if response.status_code != 200:
            return False, resp
        
        return True, resp
    
    def api_put(self, path, params_data):
        ''' Uses the access token to send a PUT API call to the Monzo API. '''

        if path.startswith("/"):
            path = path[1:]
        response = requests.put("https://{}/{}".format(config.MONZO_API_HOSTNAME, path), 
            headers={"Authorization": "Bearer {}".format(self._access_token)},
            data=params_data)

        try:
            resp = response.json()
        except json.decoder.JSONDecodeError:
            resp = response.text
        
        if response.status_code != 200:
            return False, resp

        return True, resp
    

    def test_api_call(self):
        ''' Sends a GET ping API call to the Monzo API to test the auth state. '''

        success, response = self.api_get("ping/whoami", {})
        return success, response

    def log_out(self):
        ''' Sends a post API call to force a hard log out of the client and resets the config file. '''

        success, response = self.api_post("oauth2/logout",{})
        reset_config()

        if success:
            print('Successfully logged out.')
        else:
            success, response = self.test_api_call()
            if success:
                print('Logout failed.')



if __name__ == "__main__":
    client = OAuth2Client()
    client.start_auth()
    client.test_api_call()
    client.refresh_access_token()