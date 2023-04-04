# pa-import-address-obj.py
This script imports Address Objects into a Prisma Access Cloud Manager Folder based on an input CSVFile

# Prisma SASE script description
---------------------------------------
```
This script imports Address Objects into a Prisma Access Cloud Manager Folder based on an input CSVFile
usage: pa-import-address-obj.py [-h] [--token "MYTOKEN"]
                               [--authtokenfile "MYTOKENFILE.TXT"] --csvfile
                               csvfile
```
# Prisma SASE script
---------------------------------------
```
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
```
