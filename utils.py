# https://github.com/monzo/reference-receipts-app/blob/master/utils.py

import sys
from tempfile import mkstemp
from shutil import move
import os

def error(message):
    print(f'Error: {message}')
    sys.exit(1)


def refresh_config(access_token,refresh_token,user_id):
    ''' Take the access token, refresh token and re-write them into the config file for future auth requests. ''' 

    print('Storing authentication details to config.')

    # get the absolute directory path of this file and append config.py to get direct file path for config
    util_dir_path = os.path.dirname(__file__)
    source_file_path = os.path.join(util_dir_path,'config.py')

    # this dictionary is used to replace the config lines
    replacements = {
        'MONZO_ACCESS_TOKEN' : f'MONZO_ACCESS_TOKEN = "{access_token}" \n',
        'MONZO_REFRESH_TOKEN' : f'MONZO_REFRESH_TOKEN = "{refresh_token}" \n',
        'MONZO_USER_ID' : f'MONZO_USER_ID = "{user_id}"\n'
        }
    
    # make a secure temporary file, write the config file into the temp file with replacements and then replace the config with the temp file
    fh, target_file_path = mkstemp()
    with open(target_file_path, 'w') as target_file:
        with open(source_file_path, 'r') as source_file:
            for line in source_file:
                for r_key, r_val in replacements.items():
                    if r_key in line:
                        line = r_val
                target_file.write(line)
    os.remove(source_file_path)
    move(target_file_path,source_file_path)

    print('Authentication details stored to config.')
