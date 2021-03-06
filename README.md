<img src='/images/logo.png' width=210px height=65px>
<i><p style='font-size:10'>Offline GSTR-1 Utility with Invoice Management</p></i>

<img src='/images/homepage.png' width=339px, height=347px>

##### For support email at support@bhuvannarula.cf

##### The program might seem to hang sometimes, don't worry, it is working, give it some time

##### For demo (and if you want), if you run program, your data will be Backed Up to my server (no one will touch it). To change the server, read instructions below.

# What is this Utility?
This is an offline utility in which user can manage <u>various companies at a time</u>, entering their <u>sales invoices</u> which are then <u>automatically summarised for uploading to GST website</u>

# How is it different from GSTR1 Offline Utility provided by GST Network?

- ## Cross-Platform Compatibility
	- Compatible with all platforms that support Python
	- Recommended for Python >= 3.6 (tested successfully on 3.8)
- Easy to use, only necessary options are present
- <u>User can select GSTIN from list of already entered GSTIN through drop-down</u>, and Party Name will automatically be fetched on lost focus.
- Data stored locally in form of .CSV file (for offline browsing and easy access), as well as on <u>cloud storage in mysql database</u> (for backup and restore purpose).
- Generates <u>.JSON file</u> which can be directly uploaded to GST Website.

# How to set up?

- ### 1) Setting up Databases
	- Create a database on your server
	- Update the credentials of your database in '.env' file in 'serverScript/' folder
	- Run the 'initialiseServerDatabase.py' locally, which will remotely create tables required in your database
- ### 2) Setting up Server Script
	- Now, change the 'HOSTNAME' in '.env' file to 'localhost'
	- Upload '.env' & 'serverBackupScript.py' to your server. Both files should be in same directory.
	- Make sure '.env' extension is added to hotlink protection in your server configuration, and '.py' extension to cgi scripts list
- ### 3) Setting up Client Program
	- Replace value of 'path_to_server_script' in 'offlineGST.py' script with the path of the script uploaded (eg: 'https://domain.com/demo/serverBackupScript.py')
	- Now run program and it should work now.


# How does it work?
The program has two parts:
- ### User-End:
    - It is the front-end GUI which interfaces with user, and the local processing which creates the appropriate directories and stores data locally

	- User enters invoices, and data is summarised and appropriately stores it in CSV File

	- If user selects export option, JSON file is created and stored locally in ‘export’ folder with company name
	and GSTIN

	- If backup is selected, user is authenticated, data is encoded and sent to server

	- If restore is selected, user is authenticated, and restore command is sent to server. Upon receiving data from server, the data is decoded and added to the corresponding months.
- ### Server-End:
	- It handles the backup back-end for application.

	- A table is present which contains the credentials  (userid, pass, table name) for authenticating user

    - A table is present which contains the details of ongoing sessions of uploading data

	- A single table is created for every username registered.

	- Server has a python script running which receives data, authenticates it, decodes it, finds the table and updates/adds the data to the MYSQL table using MYSQL queries and mysql-connector module for python.

	- If the server receives Restore command, the user is first authenticated, and if successful, the data for the requested months is extracted from the MYSQL database, and sent back to the user application.

## Extra Features included in Utility:
- If adding many bills in one go, user can select ‘Add Another Invoice’ in pop-up after adding an invoice, and the new form will contain date of previous invoice and auto-incremented invoice number (increments ‘A001’ to ‘A002’)

- While entering GSTIN number of Party in New Invoice Form, if data connection is available, the Party Name is auto-fetched and updated in the Party Name Input Box

- User can select GSTIN from filtered results of past GSTINs through dropdown. As user enters part of GSTIN, GSTINs from past matching the partial GSTIN entered are shown in dropdown.

- While deleting invoices, you can give multiple invoice numbers separated by comma (‘,’) to delete multiple invoices.

- In Backup option, the user can select his own UserID and Pass for authenticating, and user can select ‘Remember Me’ to save his credentials on his device locally (incase the program folder gets deleted, the saved credentials are deleted too!)

## Following modules are required 
(includes both built-in and available through pip)
### Client Side:
- tkinter
- os
- re
- functools
- shutil
- urllib
- json
- csv
- random
- hashlib
- math
- pickle
- urllib3

### Server side:
- requests
- hashlib
- cgi
- cgitb
- python-dotenv
- mysql-connector