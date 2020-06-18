# reference used https://github.com/monzo/reference-receipts-app/blob/master/main.py 

import json
import uuid

import requests

import config
import oauth2
from utils import error

class MonzoClient:
    ''' Balances object '''

    def __init__(self):
        self._api_client = oauth2.OAuth2Client()
        self._api_client_ready = False
        self._personal_account_id = None
        self._joint_account_id = None
        self.balances = []


    def check_auth(self):
        ''' Check if authentication has already been completed by reviewing auth variables in config and testing an API call '''
        
        config_vars = [
            oauth2.config.MONZO_ACCESS_TOKEN,
            oauth2.config.MONZO_REFRESH_TOKEN,
            oauth2.config.MONZO_USER_ID
        ]

        if None in config_vars:
            print("Authentication is needed to set config variables")
            self.do_auth()
        else:
            print("Access and refresh tokens exist, testing API call...")
            success, response = self._api_client.test_api_call()
            if not success:
                print("API test call failed, refreshing access token...")
                self._api_client.refresh_access_token()
                success, response = self._api_client.test_api_call()
                if not success:
                    try:
                        error("API test call failed after refresh, bad status code returned: {} ({})".format(response.status_code,
                            response))
                    except:
                        error("API test call failed after refresh, no status code returned")
        
            print("API test call successful.")
            self._api_client_ready = True


    def do_auth(self):
        ''' Perform OAuth2 flow mostly on command line. Waits for the user to confirm access to their data in their Monzo app -- this is required for the client to be compliant with Strong Customer Authentication and be able to access user data. '''

        print('Starting OAuth2 flow...')
        self._api_client.start_auth()

        print('OAuth2 flow completed, testing API call...')
        success, response = self._api_client.test_api_call()
        if not success:
            try:
                error("API test call failed on initial auth, bad status code returned: {} ({})".format(response.status_code,
                    response))
            except:
                error("API test call failed on initial auth, no status code returned")
        
        print("API test call successful.")
        self._api_client_ready = True

        print('Please open your Monzo app, client \"Allow access to your data\" and follow the instructions.')
        input('Once approved, press [Enter] to continue:')



    def get_account(self):
        ''' Retreive information of the authorised user's personal and joint account information '''

        print('Retrieving account information...')
        success, response = self._api_client.api_get('accounts',{})
        if not success or 'accounts' not in response or len(response['accounts']) < 1:
            error('Count not retrieve accounts information: {}'.format(response))

        for account in response['accounts']:
            if 'type' in account and account['type'] == 'uk_retail':
                self._personal_account_id = account['id']
                print('Retrieved personal account information.')
            if 'type' in account and account['type'] == 'uk_retail_joint':
                self._joint_account_id = account['id']    
                print('Retrieved joint account information.')
            
        
        if self._personal_account_id is None:
            error('Count not find a personal account')
        
        if self._joint_account_id is None:
            print('Count not find a joint account')
            

    def list_balances(self,account):
        ''' An example call to the end point documented in https://docs.monzo.com/#balance'''

        if self._api_client is None or not self._api_client_ready:
            error('API client not initialised.')

        success, response = self._api_client.api_get('balance',{'account_id': account})

        if not success or 'balance' not in response:
            error('Could not get balance ({})'.format(response))

        self.balances = response['balance']
        print('Balance loaded.')


if __name__ == '__main__':
    monzo =  MonzoClient()
    monzo.check_auth()
    monzo.get_account()
    monzo.list_balances(monzo._personal_account_id)
    print(monzo.balances)