#!/usr/bin/env python
PROGRAM_NAME = "pa-import-address-obj.py"
PROGRAM_DESCRIPTION = """
Prisma SASE script description
---------------------------------------
This script imports Address Objects into a Prisma Access Cloud Manager Folder based on an input CSVFile
usage: pa-import-address-obj.py [-h] [--token "MYTOKEN"]
                               [--authtokenfile "MYTOKENFILE.TXT"] --csvfile
                               csvfile

Prisma SASE script
---------------------------------------

optional arguments:
  -h, --help            show this help message and exit
  --token "MYTOKEN", -t "MYTOKEN"
                        specify an bearer token to use for Prisma Access 
                        Cloud Manager authentication
  --authtokenfile "user-api.csv", -f "user-api.csv"
                        a CSV file containing the Client Secret and Token downloaded from the TSG
  --csvfile csvfile, -c csvfile
                        the CSV Filename to read that contains IP address objects to
                        add with the columns as *** name, ip_netmask, description ***
  --target folder, -t folder (DEFAULT:'Shared')
                        Case Sensitive Value of target Folder May be:
                            - Shared (DEFAULT)
                            - Mobile Users
                            - Remote Networks
                            - Service Connections
                            - Mobile Users Container
                            - Mobile Users Explicit Proxy



Notes:
    If Folder is not specified, Shared will be used
    The authtokenfile should be the same file as downloaded from the TSG 
    manager when creating a service account as it will find the last row and use column 1 for Client-ID
    and column 2 for Client-secret

"""

####Library Imports
import os
import sys
import argparse
import base64
from csv import reader
import requests


## Folder May be:
##  - Shared
##  - Mobile Users
##  - Remote Networks
##  - Service Connections
##  - Mobile Users Container
##  - Mobile Users Explicit Proxy

def create_access_token(username,password):
    auth_to_bytes = str(username + ":" + password).encode("ascii")
    basic_authorization = base64.b64encode(auth_to_bytes).decode('ascii')
    headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': 'Basic ' + basic_authorization
    }
    body = 'grant_type=client_credentials'
    base_url = "https://auth.apps.paloaltonetworks.com"
    request_url = base_url + '/auth/v1/oauth2/access_token'
    api_request = requests.post(request_url, headers=headers, data=body)
    return api_request

def validate_auth(username,password):
    auth_result = create_access_token(username,password)
    if auth_result.status_code == 200:
        print("Authentication Successful")
        if (auth_result.json()['access_token']):
            return auth_result.json()['access_token']
        else:
            sys.exit("Error, 200 OK Authentication but no Access token in JSON response")
    else:
        print(auth_result.json())
        print("Error, did not get HTTP 200 response for authentication")
    return False

def parse_arguments():
    CLIARGS = {}
    parser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=PROGRAM_DESCRIPTION
            )
    parser.add_argument('--client-id', '-u', metavar='"username"', type=str, 
                    help='client-id for Service Account for Cloud Manager authentication (not a user account)', default=None)
    parser.add_argument('--client-secret', '-p', metavar='"password"', type=str, 
                    help='client-secret for Service Account for Cloud Manager authentication (not user password)', default=None)
    parser.add_argument('--authtokenfile', '-f', metavar='"MYTOKENFILE.TXT"', type=str, 
                    help='a file containing the bearer token', default=None)
    parser.add_argument('--csvfile', '-c', metavar='csvfile', type=str, 
                    help='the CSV Filename to read that contains address objects to add', required=True)
    parser.add_argument('--target', '-t', metavar='target', type=str, 
                    help='the Value of target Folder (Default:Shared)', default='Shared')
    args = parser.parse_args()
    CLIARGS.update(vars(args))
    return CLIARGS

def create_address(bearer_token, folder, ip_netmask, description, name):
    base_url = "https://api.sase.paloaltonetworks.com"
    request_url = base_url + '/sse/config/v1/addresses?folder=' + folder
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + bearer_token
    }
    body = {
        "description": str(description),
        "name": str(name),
        "ip_netmask": str(ip_netmask)
        }
    api_request = requests.post(request_url, headers=headers, data=body)
    if api_request.status_code == 201: ### 201 = Created
        return api_request
    print(api_request.json())
    return api_request

def read_un_pw_from_authtoken_file(filename):
    with open(filename, 'r') as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader: ## iterate through and only grab the last line from this file. fist line is header.
            username = row[0]
            password = row[1]
    return (username, password)

##########MAIN FUNCTION#############
def go(CLIARGS):
    csvfilename = CLIARGS['csvfile']
    folder = CLIARGS['target']
    if folder not in [ 'Shared', 'Mobile Users', 'Remote Networks', 'Service Connections', 'Mobile Users Container', 'Mobile Users Explicit Proxy' ]:
        sys.exit("Error, Folder must be either 'Shared', 'Mobile Users', 'Remote Networks', 'Service Connections', 'Mobile Users Container', 'Mobile Users Explicit Proxy'")
    if CLIARGS['authtokenfile']:
        (username, password) = read_un_pw_from_authtoken_file(CLIARGS['authtokenfile'])
    else: 
        password = CLIARGS['client_secret']
    bearer_token = validate_auth(username,password)
    if not bearer_token:
        sys.exit("Authorization Failed for API call")
    
    # open file in read mode
    with open(csvfilename, 'r') as read_obj:
        csv_reader = reader(read_obj)
        print("Opened File",csvfilename,"successfully")
        prefix_list = []
        counter = 0
        for row in csv_reader:
            counter += 1
            name = row[0]
            ip_netmask = row[1]
            description = row[2]
            #input_prefix = str(row).strip().replace(",","").replace(" ","").replace("[","").replace("]","").replace("'","").replace("\"","")
            result = create_address(bearer_token, folder, ip_netmask, description, name)
            if result.status_code != 201:
                print("Error reading row " + str(counter) + " with data " + str(row))

if __name__ == "__main__":
    ###Get the CLI Arguments
    CLIARGS = parse_arguments()    
    ###Run Code
    go(CLIARGS)
