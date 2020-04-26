import requests
import os
import json
from dotenv import load_dotenv

# no need to give a path to .env if in same directory
load_dotenv() 

monzo_base_endpoint = 'https://api.monzo.com'
arguments = '?account_id={}'.format(os.getenv('ACCOUNT_ID'))
bearer_token = 'Bearer {}'.format(os.getenv('ACCESS_TOKEN'))
headers = {'Authorization': bearer_token}

def get_main_balance():
    """ Query the Monzo API for main account balance. """
    balance_path = '/balance'
    r = requests.get(monzo_base_endpoint+balance_path+arguments,headers=headers)
    response = r.json()
    balance = response['balance']
    main_account = ('main',balance/100)
    return main_account

def get_pot_balances():
    """ Query the Monzo API for balances of all active pots. """
    pots_path = '/pots'
    r = requests.get(monzo_base_endpoint+pots_path,headers=headers)
    response = r.json()
    pots = []
    
    # only append active pots to the pots list
    for pot in response['pots']:
        if pot['deleted'] == False:
            name = pot['name']
            balance = pot['balance']/100
            pot_details = (name,balance)
            pots.append(pot_details)
    return pots

def main():
    main_account = get_main_balance()
    pots = get_pot_balances()
    print(main_account)
    for pot in pots:
        print(pot)


if __name__ == '__main__':
    main()