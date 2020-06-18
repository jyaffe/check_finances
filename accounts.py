from utils import error

class Account:
    ''' Takes the response object from the get accounts API call and creates an account object based on the retuned details '''

    def __init__(self,account):
        self.id = account['id']
        self.description = account['description']

        if 'type' in account and account['type'] == 'uk_retail':
            self.type = 'personal'
            print('Retreived personal account information.')
        elif 'type' in account and account['type'] == 'uk_retail_joint':
            self.type = 'joint'
            print('Retreived joint account information.')
        else:
            error('Account type not recognised.')
    
    def add_main_balances(self,response):
        self.main_balance = response['balance']/100
        self.total_balance = response['total_balance']/100

    def add_pot_balances(self,response):
        self.pots = []

        for pot in response['pots']:
            self.pots.append(Pot(pot))

    def show_balances(self):
        print('')
        print(self, self.main_balance)
        for pot in self.pots:
            if pot.deleted == False:
                print(pot.name, pot.balance)

    def __repr__(self):
        return '{} account'.format(self.type.capitalize())
        

class Pot:
    ''' Creates a pot object from the pots get API call '''

    def __init__(self,pot):
        self.id = pot['id']
        self.name = pot['name']
        self.balance = pot['balance']/100
        self.deleted = pot['deleted']

    def __repr__(self):
        return '{}'.format(self.name)
