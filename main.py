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
        self._account_id = None
        self. balances = []


    def do_auth(self):
        ''' Perform OAuth2 flow mostly on command line and retreive information of the authorised user's current account information, rather than from a joint account if present. Also waits for the user to confirm access to their data in their Monzo app -- this is required for the client to be compliant with Strong Customer Authentication and be able to access user data. '''

        print('Starting OAuth2 flow...')
        self._api_client.start_auth()

        print('OAuth2 flow completed, testing API call...')
        response = self._api_client.test_api_call()
        if 'authenticated' in response:
            print('API call test successful')
        else:
            error('OAuth2 flow seems to have failed.')
        self._api_client_ready = True

        print('Please open your Monzo app, client \"Allow access to your data\" and follow the instructions.')
        input('Once approved, press [Enter] to continue:')

        print('Retrieving account information...')
        success, response = self._api_client.api_get('accounts',{})
        if not success or 'accounts' not in response or len(response['accounts']) < 1:
            error('Count not retrieve accounts information: {}'.format(response))

        # this restricts it to personal accounts only.
        for account in response['accounts']:
            if 'type' in account and account['type'] == 'uk_retail':
                self._account_id = account['id']
                print('Retrieved account information.')
                return
        
        if self._account_id is None:
            error('Count not find a personal account')

    def list_balances(self):
        ''' An example call to the end point documented in https://docs.monzo.com/#balance'''

        if self._api_client is None or not self._api_client_ready:
            error('API client not initialised.')

        success, response = self._api_client.api_get('balance',{'account_id': self._account_id})

        if not success or 'balance' not in response:
            error('Could not get balance ({})'.format(response))

        self.balances = response['balance']
        print('Balance loaded.')

if __name__ == '__main__':
    monzo =  MonzoClient()
    monzo.do_auth()
    monzo.list_balances()
    print(monzo.balances)