import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import ttk
import os
import re
from functools import partial
from shutil import rmtree
from urllib import request
import json
import csv
from datetime import datetime, timedelta

from hashlib import sha256
from math import ceil
from urllib.request import quote
from re import fullmatch
import pickle
from urllib3 import PoolManager

'''
offlineGST

Return Utility with Sale and Purchase Invoicing

Author : Bhuvan Narula
Website : bhuvannarula.cf
Version : v4
'''

'''
Global Variables (User should change only these if necessary):
    path_to_server_script : str
        String containing link to the Server Script.
        User can use their custom server by changing this link.
        By default, my server is used
    auto_update : bool
        True if user wants to automatically update the code
        False if user wants to manually update code from GitHub
    auto_update_extensions : bool
        Same as auto_update, just for the Extensions
        Note: setting auto_update to False will NOT override this
    enableExtensions : bool
        True if extensions are to be enabled
        False if not
'''
path_to_server_script = 'https://bhuvannarula.cf/offlinegst/cgi-bin/serverBackupScript.py'
auto_update = True
auto_update_extensions = True
enableExtensions = True

'''
Next 4 lines
Checks if extensions are enabled, and imports the extensions.
Extensions are present in 'extras/' directory
importExtensionsFound : bool
    Used to check if 'importExtensions' module has been imported.
'''
if os.path.isfile(os.getcwd() + '/extras/importExtensions.py'):
    from extras import importExtensions
    importExtensionsFound = True
else:
    importExtensionsFound = False

def get_companyDirectory():
    '''
    Checks the directory 'companies/' and returns 
    names of folders present i.e. Companies present
    
    returns : list of strings
    '''
    if not os.path.isdir(os.getcwd()+'/companies'):
        os.mkdir(os.getcwd()+'/companies')
    companyDirectory1 = list(os.listdir(os.getcwd()+'/companies/'))
    companyDirectory = list(
        item for item in companyDirectory1 if item[0] != '.')
    return companyDirectory

# Color of background of 'offlineGST' logo
headingcolor1 = 'LightBlue'

# Root Window of tkinter in which everything will be placed
toplevel_1 = tk.Tk(screenName='offlineGST',
                   baseName='offlineGST', className='offlineGST')

# Disabling resizing of window
toplevel_1.resizable(height=0, width=0)

# Main Frame of program
frame_0 = tk.Frame(toplevel_1)

# Scaling window according to user's screen size
'''
toplevel_1.winfo_screenheight() returns height of screen in pixels
toplevel_1.winfo_screenmmheight() returns height of screen in mm
141 mm x 141 mm was the size of 400x400 px window on the display program was designed.
'''
screendim = (toplevel_1.winfo_screenheight()/toplevel_1.winfo_screenmmheight())*141

# setting frame dimensions
frame_0.configure(height=screendim, width=screendim)

# following code provides ability to install new extensions
if enableExtensions:
    # create 'extras/' directory
    if not os.path.isdir(os.getcwd() + '/extras'):
        os.mkdir(os.getcwd() + '/extras')
    def ExtensionInstaller():
        '''
        Asks for the name of extension and installs the extension (if found)
        
        Extensions are modules that contains code meant for a specific need
            (hence, it is required by only that person for which extension was made)
        
        Currently available extension(s) can be found at
            https://github.com/bhuvannarula/offlineGST-Extensions/
        '''
        # Ask for Extension Name
        excode = simpledialog.askstring('New Extension', 'Enter Extension Name')
        if excode:
            # create browser-like instance
            browser3 = PoolManager()
            extURL = 'https://raw.githubusercontent.com/bhuvannarula/offlineGST-Extensions/master/' + excode + '.py'
            # open link for extension
            newext = browser3.urlopen('GET', extURL).data.decode('utf-8')
            # if link is correct, the entire code is printed in browser, and 'import' word is present in code
            if 'import' not in newext:
                messagebox.showerror('Error','No such extension exists!')
            else:
                scriptfile = open(os.getcwd() + '/extras/' + excode.split('-')[0] + '.py', 'w')
                scriptfile.write(newext)
                scriptfile.close()
                # show that update was installed
                messagebox.showinfo('Success', 'Extension Installed.')
                # close the program, so that user restarts it.
                toplevel_1.destroy()

# to make sure checking update is only when software launched, not again anytime homescreen opens
checked_for_update = False 

def check_for_update():
    '''
    Updates the code files by fetching new files from GitHub and comparing them
    '''
    # use global variable 'checked_for_update'
    global checked_for_update
    if not checked_for_update:
        # The first time code checks for updates
        checked_for_update = True
    else:
        # Any other time code checks for updates
        return False
    exten_updated = False
    if auto_update_extensions and enableExtensions:
        if importExtensionsFound:
            resp = importExtensions.ExtensionUpdater()
            # resp = True if any extension was updated, else False
            exten_updated = resp
    if not auto_update and not exten_updated:
        # If auto_update disabled, and no extension was updated
        return False
    elif not auto_update:
        # If auto_update disabled but an extension was updated
        # Shows a pop-up that update was installed, and closes the tkinter window (so that software is restarted)
        messagebox.showinfo(
            'Updated!', 'New update has been installed.\nPlease Restart Utility.')
        toplevel_1.destroy()
        return True
    try:
        browser2 = PoolManager()
        # open GitHub link for main code
        respupdate = browser2.urlopen(
            'GET', 'https://raw.githubusercontent.com/bhuvannarula/offlineGST/master/offlineGST.py').data.decode('utf-8')
        scriptfilein = open(os.getcwd()+'/offlineGST.py', 'r+')
        # Read the code present in local machine
        scriptfileindata = scriptfilein.read()
        if scriptfileindata != respupdate:
            # if code on local machine is not same as that on GitHub, local code is overwritten.
            scriptfilein.seek(0)
            scriptfilein.truncate()
            scriptfilein.write(respupdate)
            scriptfilein.close()
            # Show pop-up that update was installed, and close tkinter window
            messagebox.showinfo(
                'Updated!', 'New update has been installed.\nPlease Restart Utility.')
            toplevel_1.destroy()
            return True
        else:
            scriptfilein.close()
            return False
    except:
        # In case of no network or any similar error
        return False

# Dictionary containing State Name against State Code
stcode = {'35': '35-Andaman and Nicobar Islands', '37': '37-Andhra Pradesh', '12': '12-Arunachal Pradesh', '18': '18-Assam', '10': '10-Bihar', '04': '04-Chandigarh', '22': '22-Chattisgarh', '26': '26-Dadra and Nagar Haveli', '25': '25-Daman and Diu', '07': '07-Delhi', '30': '30-Goa', '24': '24-Gujarat', '06': '06-Haryana', '02': '02-Himachal Pradesh', '01': '01-Jammu and Kashmir', '20': '20-Jharkhand', '29': '29-Karnataka', '32': '32-Kerala',
            '31': '31-Lakshadweep Islands', '23': '23-Madhya Pradesh', '27': '27-Maharashtra', '14': '14-Manipur', '17': '17-Meghalaya', '15': '15-Mizoram', '13': '13-Nagaland', '21': '21-Odisha', '34': '34-Pondicherry', '03': '03-Punjab', '08': '08-Rajasthan', '11': '11-Sikkim', '33': '33-Tamil Nadu', '36': '36-Telangana', '16': '16-Tripura', '09': '09-Uttar Pradesh', '05': '05-Uttarakhand', '19': '19-West Bengal', '38': '38-Ladakh'}
def get_placeofsupply(statecode):
    '''
    Returns State Name corresponding to the State Code given
    
    statecode : str
    len(statecode) = 2
    '''
    return stcode[statecode]

def is_GSTIN(GSTIN):
    '''
    Checks if the GSTIN is correct by matching it to general pattern of GSTIN
    
    GSTIN : str
    Pattern of GSTIN : [0-9]{2}[A-Z]{4}[0-9A-Z][0-9]{4}[A-Z]{1}[0-9A-Z]{3}
    '''
    if re.fullmatch('[0-9]{2}[A-Z]{4}[0-9A-Z][0-9]{4}[A-Z]{1}[0-9A-Z]{3}', GSTIN):
        return True
    else:
        return False

def check_GSTIN(GSTIN):
    '''
    Checks if GSTIN is correct, and returns Trade Name of the Party with corresponding GSTIN

    GSTIN : str
    '''
    '''
    offlineGST software uses ClearTax API to fetch Party Name corresponding to the GSTIN entered.
    This might SEEM illegal, but ClearTax has implimented a public GSTIN search tool, 
        available at https://cleartax.in/s/gst-number-search
    which uses the same API, and how the API is used can be found by right-clicking the page and
    inspecting the page. A JavaScript Code is present, and the code i have written is just the
    Python way of doing what that JS code is doing.
    The API is provided by GST Network, and is available only to large corporate firms, hence I
    cannot use the API directly. 
    This software was created as a helping tool, to be used at very low scale (only for my father),
    and the frequency of fetching is quite less. Hence this use of their API can be termed illegal
    ONLY in case this leads to excessive use of their server (a case of DDoS Attack) which is neither
    my intention nor the software is capable of performing.
    '''
    # GSTIN pattern matching to reduce API use
    if not is_GSTIN(GSTIN):
        return False
    # creating browser instance
    brows = PoolManager()
    # Opening this URL returns a JSON response containing data corresponding to the GSTIN
    webopener = brows.urlopen('GET',
        'https://cleartax.in/f/compliance-report/{}/'.format(GSTIN))
    response_gstin_tradename = json.loads(webopener.data)
    try:
        # Following value can be fetched only if GSTIN was correct and response was correctly received
        response_gstin_tradename = response_gstin_tradename['taxpayerInfo']['tradeNam']
    except:
        # In case of wrong GSTIN, the above value cannot be fetched, hence error will be generated
        # or in case there is no internet connectivity
        return False
    if response_gstin_tradename == 'null':
        # Just in case the value is able to be fetched but is 'null', depends on error handling of their server
        return False
    else:
        return response_gstin_tradename


def back_to_homescreen(currentFrame):
    '''
    Removes(forgets) current frame, and Adds(places) the HomeScreen
    
    currentFrame : tkinter.Frame
    '''
    currentFrame.place_forget()
    screen1()


def back_to_menu(currentFrame=None, sale = True):
    '''
    Removes(forgets) current frame (if any), and Adds(places) the MenuScreen
    '''
    if currentFrame:
        currentFrame.place_forget()
    screen2(sale=sale)

# functions responsible for backup and restore start here -->

def backupMain(companyName, filingPeriod, hashed=False, username=None, password=None, rememberMe=False, 
               path_to_server_script=path_to_server_script, packet_length=None):
    '''
    Function responsible for Backup of the data of selected Company and selected Month
    to the server (Backup Feature)
    
    Note : Backup and Restore feature works only for 'Sale' invoices, 'Purchase' invoice are not backed up.
    
    companyName : string
    filingPeriod : string
    packet_length : None or int
    '''
    '''
    hashed = False if user enters password
    hashed = True if pre-saved password is fetched (pre-saved pass is already hashed)
    
    The hashing password part essentially just makes the code complex, but fixes password length to 64 characters.
    This can be considered advantage or disadvantage depends on POV
    '''
    if not hashed:
        # if password not hashed, hash it
        password = sha256(password.encode('ascii')).hexdigest()
    else:
        # if password pre-saved, fetch it
        cookiesFileIN = open(os.getcwd()+'/.savedCred', 'rb')
        username, password = pickle.load(cookiesFileIN)
        cookiesFileIN.close()
    if rememberMe:
        # if user has selected to save password, save it to file
        # Note : password is already hashed at this point, hence no hashing again
        cookiesFileIN = open(os.getcwd()+'/.savedCred', 'wb')
        pickle.dump((username, password), cookiesFileIN)
        cookiesFileIN.close()

    # Fetches the GSTIN of the company selected for Backup and stores it in companyGSTIN
    with open(os.getcwd()+'/companies/{}/.COMPANY_GSTIN'.format(companyName), 'r') as companyGSTINfile:
        companyGSTIN = companyGSTINfile.read(15)

    def initialiseCSVdata():
        '''
        Reads all the data from CSV file of the selected month, reduces it to 
        necessary details, and returns a nested tuple
        '''
        # open the CSV file
        csvFileIN = open(os.getcwd(
        )+'/companies/{}/{}/GSTR1.csv'.format(companyName, filingPeriod), 'r', newline='')
        csvFileReader = csv.reader(csvFileIN)
        
        # skip the header
        next(csvFileReader)
        
        nestedTuple = tuple()
        for item in csvFileReader:
            '''
            Standard header is : ['GSTIN', 'Receiver Name', 'Invoice Number', 'Invoice Date', 'Invoice Value',
                     'Place Of Supply', 'Invoice Type', 'Rate', 'Taxable Amount', 'Cess Amount']
            
            GSTIN is 15 char long if it is a registered party
            GSTIN is 2 char long (just state code) if it is an unregistered party.
            so, Place of Supply can be derived from GSTIN column. Hence, not included
            '''
            # 0,2,3,7,8 are the bare minimum necessary columns
            item2 = item[2:3] + item[:1] + item[3:4] + item[7:9]
            nestedTuple += (tuple(item2),)
        return str(nestedTuple)

    # fetch data from CSV file
    rawCSVdata = initialiseCSVdata()
    
    # encodes or 'quotes' the data like the way it is done when HTML form is submitted and data is sent.
    csvDatatoUpload = quote(rawCSVdata, safe='')
    
    # calculate bytes of data to upload
    bytesToUpload = len(csvDatatoUpload)
    
    '''
    Data is sent in same way when HTML form is submitted.
    Initially, the idea was to send the data in 'packets' or parts,
    one at a time, because i thought whole at once would be too long 
    and would generate errors. (Data is sent as a URL, and it was 
    suggested on internet that length of URL be <= 1024 or so)
    Later, found that sending all at once did not throw error, hence
    code was modified such that support for splitting in packets
    remained, but now all data was sent at once. (was tried with
    length of string being about 5000 characters)
    (packet-mode can be enabled by setting value of 'packet_length'
        - This can be done only be done by editing code
        - packet_length = length of string to be sent as one packet
    ) 
    '''
    if not packet_length:
        # if packet_length is not specified (by default 'None')
        packet_length = bytesToUpload
        packets_count = 1
    else:
        # if packet_length is specified
        packets_count = ceil(bytesToUpload/packet_length)

    # creating a browser-type instance
    browser = PoolManager()
    
    # Data is sent to server like when a HTML form is submitted. These unique keys 
    # of data is just so that only the one who knows the correct can send data to
    # server (Just increases complexity) (user with custom-server can change them)
    firstRequest = browser.request('POST', path_to_server_script,
                                   fields={'Identification': 'True',
                                           'mastermindname': username,
                                           'wizardspell': password,
                                           'hobbit': companyGSTIN,
                                           'book': filingPeriod.replace('-', ''),
                                           'scrolls': packets_count}
                                   )
    
    # Server responds with a key (if authentication successful) else responds with error
    authen_key_resp = firstRequest.data[:-1].decode('utf-8')
    if not fullmatch('[0-9a-zA-Z]{16}', authen_key_resp):
        return [authen_key_resp]

    # If authenticated, data is sent according to packet_count value with the authen key received
    for curr_packet in range(packets_count):
        tempCSVbuffer = csvDatatoUpload[curr_packet * packet_length : 
                                        (curr_packet+1)*packet_length]
        packetsSend = browser.request('POST', path_to_server_script,
                                      fields={'ongoingmagic': 'True',
                                              'secretspell': str(authen_key_resp),
                                              'hobbitage': str(curr_packet+1),
                                              'folklores': str(tempCSVbuffer)}
                                      )
        # Server returns 'Received' everytime a packet is received
        # and returns 'Successful' when all packets are received
        if 'Received' not in str(packetsSend.data[:-1].decode('utf-8')):
            return ['Packet Lost! Backup Failed!']
        if 'Successful' in str(packetsSend.data[:-1].decode('utf-8')):
            return True


def registerNewUserCloud(username, password, path_to_server_script=path_to_server_script):
    '''
    Registers an user on the server
    
    All data (invoices) is stored on server corresponding to the username
    '''
    # creating browser-like instance
    browser = PoolManager()
    
    # hashing the password
    password = sha256(password.encode('ascii')).hexdigest()
    
    # sending request to server
    registerRequest = browser.request('POST', path_to_server_script,
                                      fields={'Learning': 'True',
                                              'mastermindname': username,
                                              'wizardspell': password}
                                      )
    # Check if registration was successful
    print(str(registerRequest.data))
    if 'Successful' in str(registerRequest.data[:-1].decode('utf-8')):
        return True
    else:
        return False


def restoreMain(companyName, filingPeriod, hashed=False, username=None, password=None, rememberMe=False, path_to_server_script=path_to_server_script, packet_length=800):
    '''
    Function responsible for restoring a backup from server.
    companyName : str
    filingPeriod : str
    
    rememberMe : bool ; True if credentials are to be saved, else False
    hashed : bool ; True if credentials are already stored else False
    '''
    # creating browser-like instance
    browser = PoolManager()
    
    # hashing and retrieving password
    if not hashed:
        password = sha256(password.encode('ascii')).hexdigest()
    else:
        cookiesFileIN = open(os.getcwd()+'/.savedCred', 'rb')
        username, password = pickle.load(cookiesFileIN)
        cookiesFileIN.close()
    
    # saving password if user selects to
    if rememberMe:
        cookiesFileIN = open(os.getcwd()+'/.savedCred', 'wb')
        pickle.dump((username, password), cookiesFileIN)
        cookiesFileIN.close()
    
    # retrieving company GSTIN
    companyGSTIN = open(
        os.getcwd()+'/companies/{}/.COMPANY_GSTIN'.format(companyName), 'r').read(15)
    
    # sending request to server
    restoreAuthen = browser.request('POST', path_to_server_script,
                                    fields={'getback': 'True',
                                            'mastermindname': username,
                                            'wizardspell': password,
                                            'hobbit': companyGSTIN,
                                            'book': filingPeriod.replace('-', ''),
                                            'scrolls': str(1)}
                                    )
    # Server either responds with all the data of the selected company and month present in 
    # database on server (success) or with error text containing 'Failed'
    authen_key_resp = restoreAuthen.data[:-1].decode('utf-8')
    if 'Failed' in authen_key_resp:
        return ['Authentication Failed']
    else:
        try:
            # dataRec should be a tuple 
            dataRec = eval(authen_key_resp)
            # original comment : second part of second condition is for blank data
            # later added note : on reviewing the code, could not find reason for writing the second condition,
            # but i remember earlier there were cases for which this was important
            if type(dataRec) != tuple or (len(dataRec) != 0 and type(dataRec[0]) != tuple):
                raise ValueError
        except:
            return ['Authentication Failed/ Data Corrupt!']
    # open the file in which data is to be written (* older data is over-written)
    fileOUT = open(os.getcwd(
    )+'/companies/{}/{}/GSTR1.csv'.format(companyName, filingPeriod), 'w', newline='')
    csvFinalWriter = csv.writer(fileOUT)
    headerRow = ['GSTIN', 'Receiver Name', 'Invoice Number', 'Invoice Date', 'Invoice Value',
                 'Place Of Supply', 'Invoice Type', 'Rate', 'Taxable Amount', 'Cess Amount']
    # add the header row
    csvFinalWriter.writerow(headerRow)
    # write remining data to CSV file
    tempdatadict = {}
    for item in dataRec:
        if item[2] not in tempdatadict:
            tempdatadict[item[2]] = float(item[4])
        else:
            tempdatadict[item[2]] += float(item[4])
    for item in dataRec:
        item2 = list(item)
        # derive Place of Supply from GSTIN column
        item2[4] = str(round(tempdatadict[item[2]], 2))
        item2[5] = get_placeofsupply(item2[5])
        csvFinalWriter.writerow(item2)
    fileOUT.close()
    return True


# backup and restore functions end here -->


def get_current_month_summary(sale=True):
    '''
    Function responsible for
        - Generating selected month summary (displayed on Menu Page)
        - Creating list 'pastInvoices' containing all invoice numbers of current month
        - Creating dict 'invoiceNumDateDict' containing invoice no. and corresp. date
    both pastInvoices and invoiceNumDateDict are global variables (used in other parts of code)
    
    sale : bool
        True if Sale Invoicing is selected for current month
        False if Purchase Invoicing is selected for cur. month
    '''
    # use the global variables
    global pastInvoices, invoiceNumDateDict
    # open the current month CSV file (sale or purchase depends on 'sale' variable)
    csvfileIn = open(
        os.getcwd()+'/companies/{}/{}/GSTR{}.csv'.format(cName, sMonth, '1' if sale else '2'), 'r', newline='')
    tempReader = csv.reader(csvfileIn)
    # skip the header
    next(tempReader)
    # declaring variables, scheme of 'data_summary' is: [Total Invoices, Total Taxbl Val, Total IGST, Total CGST/SGST]
    data_summary = ['', 0, 0, 0]
    pastInvoices = []
    # Count of [registered, unregistered] party invoices
    invCount = [0,0]
    
    invoiceNumDateDict = {}
    for item in tempReader:
        # Counting reg and unreg party invoices
        if item[2] not in pastInvoices:
            if len(item[0]) == 15:
                invCount[0] += 1
            elif len(item[0]) == 2:
                invCount[1] += 1
        # add invoice number to pastInvoices
        pastInvoices.append(item[2])
        # add invoice no. : date to dict
        invoiceNumDateDict[item[2]] = item[3]
        # add data to data_summary
        data_summary[1] += round(float(item[8]), 2)
        if item[0][:2] == companyGSTIN[:2]:
            # if Intra-State (CGST/SGST applicable)
            data_summary[3] += round(float(item[8])*float(item[7])/200, 2)
        else:
            # if Inter-State (IGST applicable)
            data_summary[2] += round(float(item[8])*float(item[7])/100, 2)
    # Just checking if everything is alright
    if sum(invCount) != len(set(pastInvoices)):
        print(sum(invCount), len(set(pastInvoices)))
        raise UserWarning('Something is very wrong')
    # add count of invoices
    data_summary[0] = 'B2B - {}, B2C - {}'.format(*invCount)
    # Round the values in data_summary to 2 decimal places
    for i in range(1,len(data_summary)):
        data_summary[i] = round(data_summary[i],2)
    # sorting pastInvoices is required only for 'Sale' Invoices
    if sale:
        # using patter matching to sort inv no. like A100 and A101 etc
        pastInvoices.sort(key=lambda var: int(float(
            re.search('([0-9]+)$', var).groups()[0])))
    return data_summary


def addNewInvoice(modify=False, reset=False, sale=True):
    '''
    Function responsible for Adding and Modifying Invoice
    
    modify : bool or str
        False (default) if addNewInvoice is called to add an invoice
        string of invoice number to be modified if called to modify an invoice
    reset : bool
        False by default
        if True only new (incremented) inv no. and inv date are returned
            this is used to set values when an invoice is to be added just after
            an invoice is added without going back to menu screen. So, intead
            of placing the whole add Invoice page again (by calling complete
            addNewInvoice function), just the value entry boxes are emptied in 
            the previously placed addNewInvoice page, and new incremented 
            inv no. and same date is placed for ease of user.
    sale : bool
        True if it is a Sale Invoice that is to be added/modified
        False if it is a Purchase Invoice that is to be added/modified

    '''
    # Declaring variables in tkinter environment
    # These variables are dynamic, meaning :
    # changing them changes value in entry box it is linked to, and vice versa
    currInvNum = tk.StringVar()
    currInvDate = tk.StringVar()
    
    # following code is responsible for incrementing invoice no. and setting inv no. and date values
    if len(pastInvoices) != 0 and sale:
        # if previous invoices are present, and it is a sale invoice that is being added/modified
        pastInvoices.sort(key=lambda var: int(float(re.search('([0-9]+)$', var).groups()[0])))
        #-- Now the code responsible for incrementing invoice no. --
        '''
        search numeric part in last invoice
            eg: if inv no. is A10B00199
                temp11 will be '00199'
                temp11_2 will be '99'
                pastInvoices[-1][-len(temp11_2.groups()[0])-1] will be digit just before temp11_2 digits
                in this case, it is '1'
            NOTE : inv like A99 will be incremented to A100
        '''
        temp11 = re.search('[0]*([1-9]{1}[0-9]*)$',
                        pastInvoices[-1]).groups()[0]
        temp11_2 = fullmatch('([9]+)$', temp11)
        if temp11_2 and len(pastInvoices[-1]) == len(temp11_2.groups()[0]):
            # converts 999 to 1000
            currInvNum.set('1' + '0'*len(pastInvoices[-1]))
        elif temp11_2 and pastInvoices[-1][-len(temp11_2.groups()[0])-1] == '0':
            # if inv no. ends with 099 or similar, it is incremented to 100
            currInvNum.set(
                pastInvoices[-1][:-len(temp11_2.groups()[0])-1] + '1' + '0'*len(temp11_2.groups()[0]))
        else:
            # any other case of invoice no.
            currInvNum.set(
                pastInvoices[-1].split(temp11)[0]+str(int(temp11)+1))
        # set the same date as previous bill
        currInvDate.set(invoiceNumDateDict[pastInvoices[-1]])
        
    # declaring variables in tkinter environment
    partyGSTIN = tk.StringVar()
    partyName = tk.StringVar()

    taxable0val = tk.StringVar(value='0.00')
    taxable5val = tk.StringVar(value='0.00')
    taxable12val = tk.StringVar(value='0.00')
    taxable18val = tk.StringVar(value='0.00')
    taxable28val = tk.StringVar(value='0.00')
    #taxablecessval = tk.StringVar('0.00') # depriciated

    if reset == True:
        # the inv no. and inv date are returned
        return currInvNum.get(), currInvDate.get()

    # parent frame for addNewInvoice page
    frame_3 = tk.Frame(frame_0, height=screendim, width=screendim)
    
    # designing
    label_12 = tk.Label(frame_3)
    label_12.config(background='LightBlue',
                    font='{Helventica} 36 {}', text='offlineGST')
    label_12.pack(anchor='w', side='top')
    label_13 = tk.Label(frame_3)
    label_13.config(font='{Helventica} 13 {italic}', text='Add New Invoice: ({} Invoice)'.format('Sale' if sale else 'Purchase'))

    frame_16 = tk.Frame(frame_3)
    button_5 = tk.Button(frame_16)
    if modify:
        # if addNewInvoice function is called to modify an invoice
        
        # setting the heading
        label_13.config(text='Modify Old Invoice:')
        
        # opening the CSV file
        csvFileIn = open(
            os.getcwd()+'/companies/{}/{}/GSTR{}.csv'.format(cName, sMonth, '1' if sale else '2'), 'r+', newline='', )
        csvReaderData = list(csv.reader(csvFileIn))
        taxSeq = ['0', '5', '12', '18', '28']
        
        # variables to store old values of invoice to be modifed
        datalist_for_modify = []
        taxabledatalist_for_modify = ['0.00']*5
        final_csv_before_addmodify = []
        for item in csvReaderData:
            # searching for the invoice to be modified
            if item[2] == modify:
                # if any part of invoice is found 
                # Note : there are separate rows for different tax rates for same invoice in CSV file
                taxabledatalist_for_modify[taxSeq.index(item[7])] = item[8]
                datalist_for_modify = item[:4] # common values for all instances
                pastInvoices.remove(item[2])
            else:
                # Remaining rows are untouched and stored separately
                final_csv_before_addmodify.append(item)
        else:
            if datalist_for_modify != [] and modify in invoiceNumDateDict:
                # any invoice has been found, and invoice no. is in dict
                # condition after and will be True always, but still written just to be sure
                # called separately as there is only one occurence of invoice no. in dict
                del invoiceNumDateDict[modify]
        # set the old values into the entry boxes
        currInvNum.set(datalist_for_modify[2])
        currInvDate.set(datalist_for_modify[3])
        if len(datalist_for_modify[0]) == 2:
            # if unreg party invoice
            partyGSTIN.set(stcode[datalist_for_modify[0]])
        else:
            # if reg party invoice
            partyGSTIN.set(datalist_for_modify[0])
        # some more setting variables
        partyName.set(datalist_for_modify[1])
        taxable0val.set(taxabledatalist_for_modify[0])
        taxable5val.set(taxabledatalist_for_modify[1])
        taxable12val.set(taxabledatalist_for_modify[2])
        taxable18val.set(taxabledatalist_for_modify[3])
        taxable28val.set(taxabledatalist_for_modify[4])
        # disable the cancel button, as cancelling will lead to deleting of invoice
        button_5['state'] = 'disabled'
        
        # seek back to start, empty the file and write all rows except those being modified
        csvFileIn.seek(0)
        csvFileIn.truncate()
        csvWriter = csv.writer(csvFileIn)
        csvWriter.writerows(final_csv_before_addmodify)
        csvFileIn.close()
        # now onwards the modified bill is treated as adding a new invoice

    # designing
    label_13.pack(anchor='w', pady='10', side='top')
    frame_4 = tk.Frame(frame_3)
    label_16 = tk.Label(frame_4)
    label_16.config(text='Invoice Number:')
    label_16.pack(anchor='w', side='left')
    entry_5 = tk.Entry(frame_4)
    entry_5.config(textvariable=currInvNum, width = 18)
    entry_5.pack(anchor='w', side='left')
    
    def inc_num_fn():
        '''
        Function to increment invoice number.
        Same logic as of code before.
        This time, when called, functions to increment value already present in entry box
        '''
        if currInvNum.get() in ('None',None,''):
            return None
        temp11 = re.search('[0]*([1-9]{1}[0-9]*)$',
                        currInvNum.get()).groups()[0]
        temp11_2 = fullmatch('([9]+)$', temp11)
        '''
        if temp11_2 and len(temp11_2.groups()[0]) == len(currInvNum.get()):
            # TODO if invNum == '99', make it '100', 'A99' will not be converted to 'A100'
            pass
        '''
        # currently, both A99 and 99 will be incremented A100 and 100 resp.
        if temp11_2 and len(currInvNum.get()) == len(temp11_2.groups()[0]):
            # converts 999 to 1000
            currInvNum.set('1' + '0'*len(currInvNum.get()))
        elif temp11_2 and currInvNum.get()[-len(temp11_2.groups()[0])-1] == '0':
            currInvNum.set(
                currInvNum.get()[:-len(temp11_2.groups()[0])-1] + '1' + '0'*len(temp11_2.groups()[0]))
        else:
            currInvNum.set(
                currInvNum.get().split(temp11)[0]+str(int(temp11)+1))
    
    # designing
    # this is a small button '+' to increment the inv no., refer to design for more clarity
    inc_num_btn = tk.Button(frame_4, text='+', command = inc_num_fn)
    inc_num_btn.pack(anchor='w',side='left')
    
    frame_4.config(height='200', width='200')
    frame_4.pack(anchor='w', padx='10', side='top')
    frame_5 = tk.Frame(frame_3)
    label_18 = tk.Label(frame_5)
    label_18.config(text='Invoice Date (dd/mm/yyyy):')
    label_18.pack(anchor='w', side='left')
    entry_6 = tk.Entry(frame_5)
    entry_6.config(textvariable=currInvDate, width='10')
    entry_6.pack(anchor='w', side='left')

    
    def inc_date_fn():
        '''
        Functions to increment the date present in the entry box
        '''
        strInvDate = currInvDate.get()
        if strInvDate in ('None',None,''):
            # if entry box is empty, set date to 1st of selected month
            # sMonth is of form mm-yyyy
            currInvDate.set('01/'+sMonth.replace('-','/'))
        elif re.fullmatch('[0-9]{2}/[0-9]{2}/[0-9]{4}',strInvDate):
            # dd/mm/yyyy is represented as '%d/%m/%Y'
            # incrementing date using datetime module
            old_date = datetime.strptime(strInvDate, '%d/%m/%Y')
            old_date += timedelta(days = 1)
            new_date = old_date.strftime('%d/%m/%Y')
            currInvDate.set(new_date)
            entry_6.delete('0', 'end')
            entry_6.insert('0',new_date)
    
    # more designing
    # this is a small button '+' to increment the inv date, refer to design for more clarity
    inc_date_btn = tk.Button(frame_5, text='+',command=inc_date_fn)
    inc_date_btn.pack(anchor='w',side='left')
    
    frame_5.config(height='200', width='200')
    frame_5.pack(anchor='w', padx='10', side='top')
    frame_6 = tk.Frame(frame_3)
    label_19 = tk.Label(frame_6)
    label_19.config(text='Party GSTIN:')
    label_19.pack(anchor='w', side='left')
    entry_7 = ttk.Combobox(frame_6, width=15, textvariable=partyGSTIN)
    frame_7_8 = tk.Frame(frame_3)
    entry_8 = tk.Entry(frame_7_8)

    def autopartyname(event):
        '''
        Function that is triggered everytime GSTIN box loses focus
        Responsible for fetching Party Name from GSTIN using check_GSTIN function
        declared earlier
        '''
        # tempPASTGSTIN is a dict containing all previously entered {GSTIN : Party Name} pairs
        # this is to reduce the use of API, and allow this feature to work offline
        if event.widget == entry_7 and partyGSTIN.get().upper() in tempPASTGSTIN:
            # if GSTIN has been entered before, fetch party name from tempPASTGSTIN instead of API
            partyGSTIN.set(partyGSTIN.get().upper())
            partyName.set(tempPASTGSTIN[partyGSTIN.get()])
            entry_8.delete('0', 'end')
            entry_8.insert('0', tempPASTGSTIN[partyGSTIN.get()])
        elif event.widget == entry_7 and re.fullmatch('[0-9]{2}[A-Z]{4}[0-9A-Z][0-9]{4}[A-Z]{1}[0-9A-Z]{3}', partyGSTIN.get().upper()):
            # if GSTIN never entered before
            # first make it upper class
            partyGSTIN.set(partyGSTIN.get().upper())
            # then call the API function
            foundGSTIN = check_GSTIN(partyGSTIN.get())
            if foundGSTIN:
                # If a match is returned, set it
                partyName.set(foundGSTIN)
                # added this just to make sure entry box is updated
                entry_8.delete('0', 'end')
                entry_8.insert('0', foundGSTIN)

    def listGSTIN():
        '''
        Function that is triggered everytime drop down is opened
        Entry Box for GSTIN is a drop down, in which 
            Case-1 : If User is entering a GSTIN
                all GSTIN matching the text entered are shown. Text entered can be any part of GSTIN
            *Case-2 : If User is entering invoice for Unregistered Dealer
                User needs to enter Place of Supply (either state code or state name), and states
                matching the text will be shown in dropdown. User NEEDS to pick one from dropdown
                as the state name needs to be in proper formatting.
                Refer to 'How to Use the Program' in Documentation at
                    https://bhuvannarula.cf/offlinegst/documentation.pdf
        '''
        # First find GSTIN(s) matching the entered text
        temp111 = list(
            i for i in tempPASTGSTIN if re.search(partyGSTIN.get().upper(), i.upper() + ' ' + tempPASTGSTIN[i].upper()))
        if partyGSTIN.get() not in ('',None) and len(re.findall('[0-9]{2}', partyGSTIN.get())) <= 1:
            # checks in state names as well, second condition above filters cases when state names are checked
            temp112 = list(
            i for i in list(stcode.values()) if re.search(partyGSTIN.get().lower(), i.lower())
            )
            '''
            Old Way of doing
            if temp111 == [] and partyGSTIN.get() not in ('',None):
                # if no GSTIN were found, then check if user was entering state name/code
                temp111 = list(
                i for i in list(stcode.values()) if re.search(partyGSTIN.get().lower(), i.lower())   
            '''
            temp111.extend(temp112)
        entry_7['values'] =  temp111 # First Matched GSTIN, then state names.
    
    # designing
    
    # postcommand is triggered when dropdown is opened, hence triggering listGSTIN function
    entry_7.config(postcommand=listGSTIN)
    # binding so that autopartyname(event) is triggered on <FocusOut> (losing focus of entry_7)
    entry_7.bind('<FocusOut>', autopartyname)
    
    # designing
    entry_7.pack(anchor='w', side='top')
    frame_6.config(height='200', width='200')
    frame_6.pack(anchor='w', padx='10', side='top')
    label_20 = tk.Label(frame_7_8)
    label_20.config(text='Party Name:')
    label_20.pack(anchor='w', side='left')
    entry_8.config(textvariable=partyName)
    entry_8.pack(anchor='w', side='top')
    frame_7_8.config(height='200', width='200')
    frame_7_8.pack(anchor='w', padx='10', side='top')
    label_23 = tk.Label(frame_3)
    label_23.config(text='Taxable Value:')
    label_23.pack(anchor='w', padx='10', side='top')

    frame_10 = tk.Frame(frame_3)
    label_24 = tk.Label(frame_10)
    label_24.config(text='0% :')
    label_24.pack(anchor='w', side='left')
    entry_9 = tk.Entry(frame_10)

    entry_9.config(textvariable=taxable0val, width='10')
    entry_9.pack(anchor='w', side='left')
    label_33 = tk.Label(frame_10)
    label_33.config(text='5% :')
    label_33.pack(anchor='w', side='left')
    entry_15 = tk.Entry(frame_10)

    entry_15.config(textvariable=taxable5val, width='10')
    entry_15.pack(anchor='w', side='top')
    frame_10.config(height='200', width='200')
    frame_10.pack(anchor='w', padx='20', side='top')
    frame_12 = tk.Frame(frame_3)
    label_27 = tk.Label(frame_12)
    label_27.config(text='12% :')
    label_27.pack(anchor='w', side='left')
    entry_11 = tk.Entry(frame_12)

    entry_11.config(textvariable=taxable12val, width='10')
    entry_11.pack(anchor='w', side='left')
    label_34 = tk.Label(frame_12)
    label_34.config(text='18% :')
    label_34.pack(anchor='w', side='left')
    entry_16 = tk.Entry(frame_12)

    entry_16.config(textvariable=taxable18val, width='10')
    entry_16.pack(side='top')
    frame_12.config(height='200', width='200')
    frame_12.pack(anchor='w', padx='20', side='top')
    frame_14 = tk.Frame(frame_3)
    label_31 = tk.Label(frame_14)
    label_31.config(text='28% :')
    label_31.pack(anchor='w', side='left')
    entry_13 = tk.Entry(frame_14)

    entry_13.config(textvariable=taxable28val, width='10')
    entry_13.pack(anchor='w', side='left')
    btn_show_tax = tk.Button(frame_14,text='Show Tax Amounts')
    btn_show_tax.pack(anchor='w',side='left')
    
    def show_tax_amounts():
        '''
        Function that, when called, opens a popup showing the tax amounts of corresponding
        tax rates, and total invoice value (for purpose of rechecking by user)
        '''
        dataIn = [taxable5val.get(),taxable12val.get(),taxable18val.get(),taxable28val.get()]
        prct = [5,12,18,28]
        totall = 0
        # finding tax amounts and total invoice value
        msgg = "Tax Amounts:\n"
        for item in range(len(prct)):
            temp_principal = float(dataIn[item])
            msgg += '{}%'.format(prct[item]).ljust(4) + str(round(temp_principal*prct[item]/100,2)) + '\n'
            totall += round(temp_principal*(100+prct[item])/100,2)
        totall += round(float(taxable0val.get()),2)
        msgg += 'Total Invoice Value: ' + str(round(totall,2))
        messagebox.showinfo('Tax Summary',msgg)
    
    # button is configured to call function on clicking
    btn_show_tax.configure(command=show_tax_amounts)
    
    # cess feature depriciated, will be revived in future on demand
    '''
    label_35 = tk.Label(frame_14)
    label_35.config(text='Cess:')
    label_35.pack(anchor='w', side='left')
    entry_17 = tk.Entry(frame_14)
    entry_17.config(textvariable=taxablecessval, width='10')
    entry_17.pack(side='top')
    '''
    # designing
    frame_14.config(height='200', width='200')
    frame_14.pack(anchor='w', padx='20', side='top')
    #frame_16 = tk.Frame(frame_3)
    #button_5 = tk.Button(frame_16)
    button_5.config(text='Go Back', command=lambda: back_to_menu(frame_3, sale))
    button_5.pack(anchor='w', side='left')

    def showError(message):
        '''
        Function that, when called, shows a dialog box with error message passed to it
        Does NOT stop the program (which happens when actual error occurs)
        
        message : str
            the error message to be shown
        '''
        messagebox.showerror('Wrong Input!', message)

    def push_data_to_excel(invNum, invDate, partyGSTIN, partyName, taxamountlists):
        '''
        Function responsible for writing the invoice to the CSV file.
        
        invNum : str
        invDate : str
        partyGSTIN : str
        partyName : str
        taxamountlists : list
        '''
        # opening the CSV file in which data to be added
        csvFileIn = open(
            os.getcwd()+'/companies/{}/{}/GSTR{}.csv'.format(cName, sMonth, '1' if sale else '2'), 'a+', newline='')
        csvWriter = csv.writer(csvFileIn)
        taxSeq = ['0', '5', '12', '18', '28']
        # calculating total invoice value
        totalInvValue = round(sum(list(
            (100+float(taxSeq[i[0]]))*float(i[1])/100 for i in enumerate(taxamountlists))),2)
        
        # adding information about new invoice to required variables
        for taxItem in enumerate(taxamountlists):
            # add row to CSV only if tax amount for that tax rate has been entered
            if int(taxItem[1]) != 0:
                pastInvoices.append(invNum.get())
                invoiceNumDateDict[invNum.get()] = invDate.get()
                csvWriter.writerow([partyGSTIN.get(), partyName.get(), invNum.get(), invDate.get(
                ), totalInvValue, get_placeofsupply(partyGSTIN.get()[:2]), 'Regular', taxSeq[taxItem[0]], taxItem[1], '0.00'])
                if is_GSTIN(partyGSTIN.get()):
                    # if GSTIN has not been entered before, store it (will be available offline)
                    tempPASTGSTIN[partyGSTIN.get()] = partyName.get()

        '''
        .PAST_GSTINS is a pickled binary file in which the dictionary 'tempPASTGSTIN' is stored so that
        it can be fetch when program is ran in future
        '''
        # dumping the new tempPASTGSTIN dict to local file
        with open(os.getcwd()+'/companies/{}/.PAST_GSTINS'.format(cName), 'wb') as tempPASTGSTINfile:
            pickle.dump(tempPASTGSTIN, tempPASTGSTINfile)
        csvFileIn.close()
        return True

    def check_valid_newInvoice_input():
        '''
        Function that checks if all the data entered on addNewInvoice page is of correct format and complete
        
        Raises error in form of pop-up using showError function
        '''
        if is_GSTIN(partyGSTIN.get()):
            # if GSTIN is entered, make it upper case
            partyGSTIN.set(partyGSTIN.get().upper())
        
        # creating list of all taxable values
        ttaxvallist = list(round(float(ii.get()), 2) for ii in [
                           taxable0val, taxable5val, taxable12val, taxable18val, taxable28val])
        
        if currInvNum.get() in (None, ''):
            # if no invoice number is entered
            showError('No invoice number entered!')
            return False
        elif not re.fullmatch('[0-9]{2}/[0-9]{2}/[0-9]{4}', currInvDate.get()):
            # if date is not entered/is of wrong format
            showError('Wrong/Incomplete Date Entered! (should be: dd/mm/yyyy)')
            return False
        elif partyGSTIN.get() in list(stcode.values()): # and partyName.get() in ('', None):
            # if party is unregistered, set GSTIN to state code
            partyGSTIN.set(partyGSTIN.get()[:2])
            partyName.set('') # to make sure
        elif not re.fullmatch('[0-9]{2}[A-Z]{4}[0-9A-Z][0-9]{4}[A-Z]{1}[0-9A-Z]{3}', partyGSTIN.get()):
            # if GSTIN does not match the pattern
            showError('Wrong/Incomplete GSTIN Entered!')
            return False
        elif partyName.get() in (None, ''):
            # if no party name has been entered
            showError('No Party Name entered!')
            return False
        elif round(sum(ttaxvallist), 0) == 0:
            # if no taxable value has been entered
            showError('No Tax Values entered!')
            return False
        elif currInvNum.get() in pastInvoices:
            # if invoice number is already present (checks only in current month)
            showError('Bill adding failed. Bill is already present!')
            return False
        
        # now that everything seems ok, push the data to CSV file
        # True is returned when all data is processed succesfully
        resp = push_data_to_excel(
            currInvNum, currInvDate, partyGSTIN, partyName, ttaxvallist)
        if resp:
            # brings 'Cancel' button back to normal (was 'disabled' during modification)
            button_5['state'] = 'normal'
            # show message that bill was added, and ask if user wants to enter another bill
            moreCond = messagebox._show(
                'Success!', 'Bill has been added successfully. Do you want to enter another bill?', _icon='info', _type=messagebox.YESNO)
            if moreCond.lower() in ('yes', 'y'):
                # if user wants to add another bill
                # instead of placing whole page again, just reset the entry boxes
                entry_5.delete('0', 'end')
                entry_6.delete('0', 'end')
                entry_7.delete('0', 'end')
                entry_8.delete('0', 'end')
                entry_9.delete('0', 'end')
                entry_9.insert('0', '0.00')
                entry_15.delete('0', 'end')
                entry_15.insert('0', '0.00')
                entry_11.delete('0', 'end')
                entry_11.insert('0', '0.00')
                entry_16.delete('0', 'end')
                entry_16.insert('0', '0.00')
                entry_13.delete('0', 'end')
                entry_13.insert('0', '0.00')
                # getting new inv no. and date
                respNumDate = addNewInvoice(reset=True)
                entry_5.insert('0', respNumDate[0])
                entry_6.insert('0', respNumDate[1])
                if modify:
                    # change heading back to normal
                    label_13.config(text='Add New Invoice: ({} Invoice)'.format('Sale' if sale else 'Purchase'))
            else:
                # going back to menu screen
                back_to_menu(frame_3, sale=sale)
    
    # designing
    button_6 = tk.Button(frame_16)
    button_6.config(text='Proceed', command=check_valid_newInvoice_input)
    button_6.pack(padx='10', side='top')
    frame_16.config(height='200', width='200')
    frame_16.pack(anchor='w', padx='10', pady='10', side='top')
    frame_3.config(height=screendim, takefocus=True, width=screendim)
    frame_3.pack(side='top')
    frame_3.config(height=screendim, takefocus=True, width=screendim)
    frame_3.pack(side='top')
    frame_3.place(x=0, y=0)


def deleteInvoice(invNums, sale = True):
    '''
    Function responsible for deleting invoice(s)
    
    invNums : str
        string containing multiple invoice numbers to be deleted, separated by comma (',')
        eg: '1, 2, 3'
    '''
    confirmresp = messagebox._show('Warning!', 'Invoices with following Invoice Numbers will be deleted: \n{}\n Are you sure?'.format(
        invNums), _icon='warning', _type=messagebox.YESNO)
    if confirmresp.lower() not in ('yes', 'y'):
        return False
    invNums = (invNums.replace(' ', '')).split(',')
    notFound = []
    for item in invNums:
        if item not in pastInvoices:
            notFound.append(item)
    if notFound:
        messagebox.showerror(
            'Error!', 'Following invoices were not found: \n{}\nOther Invoices (if any) will be deleted.'.format(', '.join(notFound)))
    csvFileIn = open(
        os.getcwd()+'/companies/{}/{}/GSTR{}.csv'.format(cName, sMonth, '1' if sale else '2'), 'r+', newline='')
    csvReader = csv.reader(csvFileIn)
    csvReaderList = []
    for item in csvReader:
        if item[2] not in invNums:
            csvReaderList.append(item)
    csvFileIn.seek(0)
    csvFileIn.truncate()
    csvWriter = csv.writer(csvFileIn)
    csvWriter.writerows(csvReaderList)
    csvFileIn.close()
    messagebox.showinfo('Success!', 'Invoice(s) deleted successfully!')
    return True


def exportInvoices():
    '''
    Function responsible for exporting data from CSV file to JSON file to upload to GST Portal
    
    Generates a JSON file with name 'export-json-{Company Name}-{Selected Month}-GSTR1-{QTR/MON}.json'
    in the directory 'export/' in the current folder
    '''
    def summarizeCSV(selMonth):
        '''
        Function responsible for reading data from CSV file of month passed as argument, and 
        segregates the data into B2B and B2CS Invoices
        '''
        # Opening the CSV file
        try:
            csvFileIn = open(
                os.getcwd()+'/companies/{}/{}/GSTR1.csv'.format(cName, selMonth), newline='')
        except:
            # if month does not exist
            return '', selMonth
        csvFileReader = list(csv.reader(csvFileIn))
        csvFileReader = csvFileReader[1:]
        b2bdata = []
        b2cs = {}
        taxRate = ['0', '5', '12', '18', '28']
        # segregating data
        for item in csvFileReader:
            if is_GSTIN(item[0]):
                b2bdata.append(item)
            else:
                if item[0] not in b2cs:
                    b2cs[item[0]] = [0, 0, 0, 0, 0]
                b2cs[item[0]][taxRate.index(item[7])] += round(float(item[8]), 2)
        csvFileIn.close()
        if len(b2bdata) == 0 and len(b2cs) == 0:
            # If no data present in month
            return '', selMonth
        return b2bdata, b2cs

    # ask user if filing frequency for GSTR1 is Quarterly or Monthly
    respFreq = messagebox.askyesno('Export as JSON', '{}\n{} - Quarterly or Monthly?\nQuarterly - Select Yes\nMonthly - Select No'.format(cName, sMonth))
    
    #initialising JSON data
    finalJSON = {}
    finalJSON['gstin'] = companyGSTIN
    finalJSON['fp'] = sMonth.replace('-', '')
    
    # creating message to ask for extra docs
    if respFreq and int(float(sMonth[:2]))%3 == 0:
        msgforextradocs = 'Enter count of docs (credit/debit notes, etc.)\nissued other than sale invoices entered here\nin this Quarter ending {} (0 for None)'.format(sMonth)
    elif not respFreq:
        msgforextradocs = 'Enter count of docs (credit/debit notes, etc.)\nissued other than sale invoices entered here\nfor current month {} (0 for None)'.format(sMonth)
    
    # difficult to explain part, it just enters details of documents into JSON
    if (respFreq and int(float(sMonth[:2]))%3 == 0) or (not respFreq):
        # if quarter-end or monthly
        extradocs = simpledialog.askstring('Export as JSON', msgforextradocs)
        if extradocs in ('', None):
            extradocs = 0
    
    if ((respFreq and int(float(sMonth[:2]))%3 == 0) or (not respFreq)) and int(extradocs) >= 0:
        # if quarter-end or monthly and int(extradocs) >= 0
        if (not respFreq):
            # if monthly
            currmondata = get_current_month_summary(sale=True) # updates pastInvoices variable
            global pastInvoices
            pastInvoices.sort(reverse=False, key=lambda varr : int(float(re.search('([0-9]+)$',varr).groups()[0])))
        
        elif int(float(sMonth[:2]))%3 == 0:
            # if month end
            def make_it_double(strnum):
                strnum = str(strnum)
                if len(strnum) == 2:
                    return str(strnum)
                elif len(strnum) == 1:
                    return '0' + strnum
            
            # checkMonths is list containing all 3 months of quarter (if quarterly)
            checkMonths = list(make_it_double(int(float(sMonth[:2])) - i)+str(sMonth[2:]) for i in range(3))
            
            totb2b, totb2cs = [], {}
            monthNotFound = []
            for iMonth in checkMonths:
                tempb2b, tempb2cs = summarizeCSV(iMonth)
                if tempb2b == '':
                    monthNotFound.append(tempb2cs)
                    continue
                totb2b.extend(tempb2b)
                for item in tempb2cs:
                    if item in totb2cs:
                        for irate in range(5):
                            totb2cs[item][irate] += float(tempb2cs[item][irate])
                    else:
                        totb2cs[item] = tempb2cs[item]
            if monthNotFound:
                respCont = messagebox.askyesno('Data not complete', 
                    'Following months have no data\navailable in software.\nDo you still want to proceed?\n{}'.format(', '.join(monthNotFound)),
                    icon = messagebox.WARNING)
                if not respCont:
                    return True
            
            totb2b = list(i[2] for i in totb2b)
            totb2b.sort(reverse=False, key=lambda varr : int(float(re.search('([0-9]+)$',varr).groups()[0])))
            pastInvoices = list(set(totb2b))
            b2cs = dict(totb2cs)
        
        totalInvIssued = len(pastInvoices)    
        invEndPoints = pastInvoices[0], pastInvoices[-1]
        
        respFinalCall = messagebox.askyesno('Docs Count','Invoices of selected {} start from\n{} and end on {}, Is this correct?'.format(
                            'month' if not respFreq else 'quarter', *invEndPoints))
        if not respFinalCall:
            invEndPoints = (simpledialog.askstring('Count Correction','Enter Starting Invoice No.\n(Do not cancel)'), 
                        simpledialog.askstring('Count Correction','Enter Ending Invoice No.\n(Do not cancel)'))
        
        invEndCounts = re.search('([0-9]+)$', invEndPoints[0]).groups()[0], re.search('([0-9]+)$', invEndPoints[1]).groups()[0]
        totalInvCounted = int(invEndCounts[1]) - int(invEndCounts[0]) + 1
        
        doc_issue = {
            "doc_det": [
        {
            "doc_num": 1,
            "docs": [
            {
                "num": 1,
                "from": str(pastInvoices[0]),
                "to": str(pastInvoices[-1]),
                "totnum": totalInvCounted + int(extradocs),
                "cancel": totalInvCounted - totalInvIssued,
                "net_issue": totalInvIssued + int(extradocs)
            }
            ]
        }]}
        finalJSON['doc_issue'] = doc_issue
        extramsgexport = '''\n
Export Summary:
    Sale Invoices (other than cancelled) : {}
    Docs Issued (including cancelled): {}
    Docs Cancelled : {}
    Net Docs Issued : {}'''.format(totalInvIssued, 
                                    totalInvCounted + int(extradocs), 
                                    totalInvCounted - totalInvIssued, 
                                    totalInvIssued + int(extradocs))
            
    elif ((respFreq and int(float(sMonth[:2]))%3 == 0) or (not respFreq)) and extradocs == '-1':
        extramsgexport = ''
        pass
        
    elif ((respFreq and int(float(sMonth[:2]))%3 == 0) or (not respFreq)) and extradocs == '-2':
        if (respFreq and int(float(sMonth[:2]))%3 == 0) or (not respFreq):
            currmondata = get_current_month_summary(sale=True)
            pastInvoices.sort(reverse=False, key=lambda varr : int(float(re.search('([0-9]+)$',varr).groups()[0])))
            invEndPoints = pastInvoices[0], pastInvoices[-1]
            
            respFinalCall = messagebox.askyesno('Docs Count','Invoices of selected {} start from\n{} and end on {}, Is this correct?'.format(
                                'month' if not respFreq else 'quarter', *invEndPoints))
            if not respFinalCall:
                invEndPoints = (simpledialog.askstring('Count Correction','Enter Starting Invoice No.\n(Do not cancel)'), 
                            simpledialog.askstring('Count Correction','Enter Ending Invoice No.\n(Do not cancel)'))
            
            invEndCounts = re.search('([0-9]+)$', invEndPoints[0]).groups()[0], re.search('([0-9]+)$', invEndPoints[1]).groups()[0]
            totalInvIssued = int(currmondata[0])
            totalInvCounted = int(invEndCounts[1]) - int(invEndCounts[0]) + 1
            
            doc_issue = {
                "doc_det": [
            {
                "doc_num": 1,
                "docs": [
                {
                    "num": 1,
                    "from": str(pastInvoices[0]),
                    "to": str(pastInvoices[-1]),
                    "totnum": totalInvCounted,
                    "cancel": 0,
                    "net_issue": totalInvCounted
                }
                ]
            }]}
            finalJSON['doc_issue'] = doc_issue
            extramsgexport = '''\n
    Export Summary:
        Sale Invoices (other than cancelled) : {}
        Docs Issued (including cancelled): {}
        Docs Cancelled : {}
        Net Docs Issued : {}'''.format(totalInvIssued, 
                                        totalInvCounted, 
                                        0, 
                                        totalInvCounted)
    else:
        extramsgexport = ''
        pass
        
        
    #summarising GSTR1 CSV data
    try:
        # for quarterly return, b2cs has already been generated
        if b2cs:
            pass
    except:
        b2bdata, b2cs = summarizeCSV(sMonth)
    else:
        b2bdata = summarizeCSV(sMonth)[0]
    
    # creating 'export/' directory
    try:
        os.mkdir(os.getcwd()+'/export')
    except:
        None

    # b2b data to json starts here
    b2bfinaldata = {}

    for i in b2bdata:
        if i[0] not in b2bfinaldata:
            b2bfinaldata[i[0]] = {i[2]: [i[3], {i[7]:i[8]}]}
        else:
            if i[2] not in b2bfinaldata[i[0]]:
                b2bfinaldata[i[0]][i[2]] = [i[3], {i[7]:i[8]}]
            else:
                b2bfinaldata[i[0]][i[2]][1][i[7]] = i[8]

    b2bObject = []

    for gstin in b2bfinaldata:
        b2bObject.append({})
        b2bObject[-1]['ctin'] = gstin
        b2bObject[-1]['inv'] = []
        for invNum in b2bfinaldata[gstin]:
            tempBill = {}
            tempBill['inum'] = str(invNum)
            tempBill['idt'] = b2bfinaldata[gstin][invNum][0].replace('/', '-')
            tempBill['pos'] = gstin[:2]
            tempBill['rchrg'] = 'N'
            tempBill['inv_typ'] = 'R'
            tempSumTotal = 0
            tempBill['itms'] = []
            for i in range(len(b2bfinaldata[gstin][invNum][1])):
                tempBill['itms'].append({})
                tempBill['itms'][-1]['num'] = i+1
                tempBill['itms'][-1]['itm_det'] = {}
                tempBill['itms'][-1]['itm_det']['rt'] = int(float(
                    list(b2bfinaldata[gstin][invNum][1].keys())[i]))
                tempBill['itms'][-1]['itm_det']['txval'] = round(float(
                    b2bfinaldata[gstin][invNum][1][list(b2bfinaldata[gstin][invNum][1].keys())[i]]), 2)
                temptaxamount = [0, 0, 0]
                if gstin[:2] == companyGSTIN[:2]:
                    temptaxamount[1] = round(float(list(b2bfinaldata[gstin][invNum][1].keys())[i]) * round(float(
                        b2bfinaldata[gstin][invNum][1][list(b2bfinaldata[gstin][invNum][1].keys())[i]]), 2) / 200, 2)
                    temptaxamount[2] = round(temptaxamount[1], 2)
                else:
                    temptaxamount[0] = round(float(list(b2bfinaldata[gstin][invNum][1].keys())[i]) * round(float(
                        b2bfinaldata[gstin][invNum][1][list(b2bfinaldata[gstin][invNum][1].keys())[i]]), 2) / 100, 2)
                tempBill['itms'][-1]['itm_det']['iamt'] = round(temptaxamount[0],2)
                tempBill['itms'][-1]['itm_det']['camt'] = round(temptaxamount[1],2)
                tempBill['itms'][-1]['itm_det']['csamt'] = 0
                tempBill['itms'][-1]['itm_det']['samt'] = round(temptaxamount[2],2)
                tempSumTotal += sum(temptaxamount) + round(float(
                    b2bfinaldata[gstin][invNum][1][list(b2bfinaldata[gstin][invNum][1].keys())[i]]), 2)
            tempBill['val'] = round(tempSumTotal, 2)
            b2bObject[-1]['inv'].append(tempBill)

    # b2b to json ends here
    if b2bObject != []:
        finalJSON['b2b'] = b2bObject
    
    # b2cs to json starts here
    if respFreq and int(float(sMonth[:2]))%3 == 0:
        Qcond = -2
    elif respFreq:
        Qcond = 1
    elif not respFreq:
        Qcond = 0
        
    masterb2cs = []
    for i in range(Qcond,1,1):
        newMonth = sMonth[0] + str(int(sMonth[1]) + i) + sMonth[2:]
        tempdat = summarizeCSV(newMonth)
        if tempdat[0] == '':
            continue
        b2cs = tempdat[-1]
        b2csfinaldata = []
        rateList = [0, 5, 12, 18, 28]
        for i in b2cs:
            for j in range(len(b2cs[i])):
                if i == companyGSTIN[:2]:
                    if int(b2cs[i][j]) == 0:
                        continue
                    temprecord = {}
                    temprecord['sply_ty'] = 'INTRA'
                    temprecord['txval'] = round(b2cs[i][j],2)
                    temprecord['typ'] = 'OE'
                    temprecord['pos'] = i
                    temprecord['rt'] = rateList[j]
                    temprecord['iamt'] = 0
                    temprecord['camt'] = round(b2cs[i][j]*rateList[j]/200,2)
                    temprecord['samt'] = round(temprecord['camt'],2)
                    temprecord['csamt'] = 0
                else:
                    if int(b2cs[i][j]) == 0:
                        continue
                    temprecord = {}
                    temprecord['sply_ty'] = 'INTER'
                    temprecord['txval'] = round(b2cs[i][j],2)
                    temprecord['typ'] = 'OE'
                    temprecord['pos'] = i
                    temprecord['rt'] = rateList[j]
                    temprecord['iamt'] = round(b2cs[i][j]*rateList[j]/100,2)
                    temprecord['camt'] = 0
                    temprecord['samt'] = 0
                    temprecord['csamt'] = 0
                b2csfinaldata.append(temprecord)
        masterb2cs.append(b2csfinaldata)

    def getPOSrate(datadict):
        return datadict['pos'], datadict['rt']
    def addtwodata(datadict1, datadict2):
        for kk in ['txval','iamt','camt','samt','csamt']:
            datadict1[kk] = round(datadict1[kk] + datadict2[kk], 2)
        return datadict1
    
    if masterb2cs:
        b2csfinaldata = masterb2cs[0]
        masterb2cssum1 = list(getPOSrate(i) for i in masterb2cs[0])
        if len(masterb2cs) == 3:
            for i in range(1,3):
                for item in masterb2cs[i]:
                    if getPOSrate(item) in masterb2cssum1:
                        b2csfinaldata[masterb2cssum1.index(getPOSrate(item))] = addtwodata(item, b2csfinaldata[masterb2cssum1.index(getPOSrate(item))])
                    else:
                        b2csfinaldata.append(item)
                        masterb2cssum1.append(getPOSrate(item))
    else:
        b2csfinaldata = []
    # b2cs to json ends here
    if b2csfinaldata != []:
        finalJSON['b2cs'] = b2csfinaldata

    finalJSON['hash'] = 'hash'
    finalJSON['version'] = 'GST1.00'

    # dump the finalJSON dict into JSON file
    JSONfile = open(
        os.getcwd()+'/export/export-json-{}-{}-GSTR1-{}.json'.format(
            cName, sMonth, 'QTR' if respFreq else 'MON'), 'w')
    json.dump(finalJSON, JSONfile)
    JSONfile.close()

    # show msg to user that export was successful, along with 'extramsgexport' string
    messagebox.showinfo(
                    'Success!', '''The invoices have been exported successfully, and JSON file is now present in "export" folder.{}'''.format(extramsgexport))
    return True

def summaryPurchase():
    '''
    Function responsible for reading data from CSV files of Purchase, and showing sum total of Purchase Input
    (For filling ITC data in GSTR3B Return)
    '''
    def summarizeCSV(selMonth):
        '''
        Function that returns summary of Purchase data of month passed
        (similar to one used in exportInvoices() function)
        '''
        try:
            csvFileIn = open(
                os.getcwd()+'/companies/{}/{}/GSTR2.csv'.format(cName, selMonth), newline='')
        except FileNotFoundError:
            return False
        csvFileReader = list(csv.reader(csvFileIn))
        csvFileReader = csvFileReader[1:]
        # totalITC is of form [taxable value, igst, cgst, cess]
        totalITC = [0, 0, 0, 0]
        '''
        Just for reference:
        
        headerRow = ['GSTIN', 'Receiver Name', 'Invoice Number', 'Invoice Date', 'Invoice Value',
                    'Place Of Supply', 'Invoice Type', 'Rate', 'Taxable Amount', 'Cess Amount']
        '''
        for item in csvFileReader:
            totalITC[0] += float(item[8])
            if item[0][:2] == companyGSTIN[:2]:
                totalITC[2] += int(item[7])*float(item[8])/200
            else:
                totalITC[1] += int(item[7])*float(item[8])/100
            totalITC[3] += float(item[9])
            
        csvFileIn.close()
        if int(sum(totalITC)) == 0:
            return False
        else:
            return totalITC
    
    # asking the user if GSTR3B frequency is Monthly or Quarterly
    respFreq = messagebox.askyesno('Purchase Summary for GSTR3B', '{}\n{} - Quarterly or Monthly?\nQuarterly - Select Yes\nMonthly - Select No'.format(cName, sMonth))

    def make_it_double(strnum):
        '''
        Converts single digit month to double digit
        
        strnum : int or str
        returns str, len(str) = 2
        '''
        strnum = str(strnum)
        if len(strnum) == 2:
            return str(strnum)
        elif len(strnum) == 1:
            return '0' + strnum
    
    # if quarterly and month-end
    if respFreq and int(sMonth[:2]) %3 == 0:
        checkMonths = list(make_it_double(int(float(sMonth[:2])) - i)+str(sMonth[2:]) for i in range(3))
    else:
        checkMonths = [sMonth]
    # tot_itc is of form [taxable value, igst, cgst, sgst, cess]
    tot_itc = [0, 0, 0, 0]
    
    for item in checkMonths:
        tempitc = summarizeCSV(item)
        if not tempitc:
            # if GSTR2 file is empty / does not exist
            messagebox.showwarning('Data not complete', 'Purchase not available / NIL for {} in software.'.format(item))
        else:
            tot_itc = list((tot_itc[i] + tempitc[i]) for i in range(len(tot_itc)))
    
    tot_itc = list(round(i, 2) for i in tot_itc)

    # create summary message
    extramsgpursum = '''Purchase Summary (does NOT include data of months that were not found):
        Total Taxable Amount : {}
        Total IGST: {}
        Total CGST : {}
        Total SGST : {}
        Total Cess : {}'''.format(*tot_itc[:3], tot_itc[2], tot_itc[3])
    
    # show the message
    messagebox.showinfo(
        'Purchase Summary', extramsgpursum
    )
    return True
    
    

def action_perform(todoAction, sale = True):
    '''
    Function that calls function according to the option selected in Menu Screen - passed to this
    function through todoAction
    
    todoAction : str
        string containing action that needs to be performed
    '''
    if todoAction == 'Add New Invoice':
        addNewInvoice(sale=sale)
        
    elif todoAction == 'Delete Invoice(s)':
        # ask user the invoice nums to be deleted
        invNums = simpledialog.askstring(
            'Delete Invoice(s)', 'Enter Invoice Numbers of Invoices\n to be deleted, separated by ","\n like 100,200,300')
        if not invNums in ('', None, 'None'):
            # call the function
            deleteInvoice(invNums, sale=sale)
        back_to_menu(sale=sale)
        
    elif todoAction == 'Modify Invoice':
        # loop works until an invoice number is found which is previously present
        while True:
            invNumModify = simpledialog.askstring(
                'Modify Invoice', 'Enter Invoice Number of Invoice to be modified:')
            if invNumModify == None:
                # if user does not wants to continue (blank response)
                break
            elif invNumModify not in pastInvoices:
                # inform user that entered inv no. was not found
                invNumModify = simpledialog.askstring(
                    'Not Found!', 'Invoice Number entered is not present. Please enter correct number.')
            else:
                break
        if invNumModify == None:
            # if user does not wants to continue (blank response)
            back_to_menu(sale=sale)
        else:
            # call the function
            addNewInvoice(modify=invNumModify, sale=sale)
            
    elif todoAction == 'Export Invoices':
        if sale:
            # confirm if user wants to continue
            resp1 = messagebox._show(
                'Are you sure?', 'The invoices will be exported. Are you sure you want to continue?', _icon='info', _type=messagebox.YESNO)
            if resp1.lower() in ('yes', 'y'):
                # call the function
                resp2 = exportInvoices()
                if resp2:
                    # if exported successfully
                    back_to_menu(sale=sale)
                # if not, program hangs and user needs to restart
            else:
                back_to_menu(sale=sale)
        else:
            # in case of Purchase Invoices
            resp2 = summaryPurchase()
            back_to_menu(sale=sale)
    elif todoAction == 'Backup Invoices':
        # Confirm from user if they want to continue
        messagebox._show('Caution', 'The invoices of selected period will be uploaded to cloud.',
                         _icon='info', _type=messagebox.OK)
        if True: # was meant for something but not used
            # credentials are locally stored in .savedCred file. So, if it does not exist
            if not os.path.isfile('.savedCred'):
                # ask user for login or register
                respRegister = messagebox.askyesno(
                    'Login/Register', 'Do you want to login or register?\n(Click Yes to Login, Click No to Register)')

                if not respRegister:
                    # if register is selected
                    kr = False
                    while True:
                        # ask username
                        credd_user = simpledialog.askstring(
                            'Register', 'Enter Username (max_length=20, only alphabet & numbers accepted):')
                        if credd_user == None:
                            # if user doesn't enter anything, stop it
                            kr = True
                            break
                        # check username
                        if len(credd_user) >= 20 or len(re.fullmatch('[0-9a-zA-Z]+', credd_user).group()) != len(credd_user):
                            messagebox.showerror(
                                'Invalid!', 'Invalid Username! (max_length=20,\nonly alphabet & numbers\naccepted)')
                            continue
                        # ask password
                        credd_pass = simpledialog.askstring(
                            'Register', 'Enter Password:')
                        if credd_pass == None:
                            # if user doesn't enter anything, stop it
                            kr = True
                            break
                        break
                    if kr:
                        back_to_menu(sale=sale)
                    # send request to server
                    respregisternew = registerNewUserCloud(
                        credd_user, credd_pass)
                    if respregisternew:
                        messagebox.showinfo(
                            'Success!', 'New User registered successfully! Now choose Login during backup!')
                    else:
                        messagebox.showerror(
                            'Failed!', 'New User Registeration failed!')
                    # go back to menu
                    back_to_menu(sale=sale)
                else:
                    # if login
                    kk = False
                    while True:
                        credd_user = simpledialog.askstring(
                            'Login', 'Enter Username (max_length=20, only alphabet & numbers accepted):')
                        if credd_user == None:
                            kk = True
                            break
                        if len(credd_user) >= 20 or len(re.fullmatch('[0-9a-zA-Z]+', credd_user).group()) != len(credd_user):
                            messagebox.showerror(
                                'Invalid!', 'Invalid Username! (max_length=20,\nonly alphabet & numbers\naccepted)')
                            continue
                        credd_pass = simpledialog.askstring(
                            'Login', 'Enter Password:')
                        if credd_pass == None:
                            kk = True
                            break
                        credd_save = messagebox.askyesno(
                            'Remember Me!', 'Do you want to save your credentials?')
                        break
                    if kk:
                        back_to_menu(sale=sale)
                    else:
                        # if successfully logged in, send data to server
                        # tell user invoices are being uploaded
                        messagebox._show(
                            'Processing', 'Invoices are being uploaded\nto cloud. Press OK', _icon='info', _type=messagebox.OK)
                        
                        # send request to server
                        respbkup = backupMain(
                            cName, sMonth, username=credd_user, password=credd_pass, rememberMe=credd_save)
                        if type(respbkup) == list:
                            messagebox._show(
                                'Error', respbkup[0], _icon='error', _type=messagebox.OK)
                            back_to_menu(sale=sale)
                        elif type(respbkup) == bool and respbkup == True:
                            messagebox.showinfo(
                                'Success', 'Data was successfully uploaded to cloud and is available to restore.')
                            back_to_menu(sale=sale)
            else:
                # if credentials are saved locally
                messagebox._show(
                    'Processing', 'Invoices are being uploaded\nto cloud. Press OK', _icon='info', _type=messagebox.OK)
                
                # send request to server
                respbkup = backupMain(cName, sMonth, hashed=True)
                if type(respbkup) == list:
                    messagebox._show(
                        'Error', respbkup[0], _icon='error', _type=messagebox.OK)
                    back_to_menu(sale=sale)
                elif type(respbkup) == bool and respbkup == True:
                    messagebox.showinfo(
                        'Success', 'Data was successfully uploaded to cloud and is available to restore.')
                    back_to_menu(sale=sale)
                    
    elif todoAction == 'Restore Invoices':
        # tell user data will be restored
        messagebox._show('Caution', 'The invoices of selected period will be restored from cloud.',
                         _icon='info', _type=messagebox.OK)
        if True: # was meant for something but not used
            if not os.path.isfile(os.getcwd()+'/.savedCred'):
                respRegister = messagebox.askyesno(
                    'Login/Register', 'Do you want to login or register?\n(Click Yes to Login, Click No to Register)')

                if not respRegister:
                    kr = False
                    while True:
                        credd_user = simpledialog.askstring(
                            'Register', 'Enter Username (max_length=20, only alphabet & numbers accepted):')
                        if credd_user == None:
                            kr = True
                            break
                        if len(credd_user) >= 20 or len(re.fullmatch('[0-9a-zA-Z]+', credd_user).group()) != len(credd_user):
                            messagebox.showerror(
                                'Invalid!', 'Invalid Username! (max_length=20,\nonly alphabet & numbers\naccepted)')
                            continue
                        credd_pass = simpledialog.askstring(
                            'Register', 'Enter Password:')
                        if credd_pass == None:
                            kr = True
                            break
                        break
                    if kr:
                        back_to_menu(sale=sale)
                    respregisternew = registerNewUserCloud(
                        credd_user, credd_pass)
                    if respregisternew:
                        messagebox.showinfo(
                            'Success!', 'New User registered successfully!')
                    else:
                        messagebox.showerror(
                            'Failed!', 'New User Registeration failed!')
                        back_to_menu(sale=sale)
                else:
                    kk = False
                    while True:
                        credd_user = simpledialog.askstring(
                            'Login', 'Enter Username (max_length=20, only alphabet & numbers accepted):')
                        if credd_user == None:
                            kk = True
                            break
                        if len(credd_user) >= 20 or len(re.fullmatch('[0-9a-zA-Z]+', credd_user).group()) != len(credd_user):
                            messagebox.showerror(
                                'Invalid!', 'Invalid Username! (max_length=20,\nonly alphabet & numbers\naccepted)')
                            continue
                        credd_pass = simpledialog.askstring(
                            'Login', 'Enter Password:')
                        if credd_pass == None:
                            kk = True
                            break
                        credd_save = messagebox.askyesno(
                            'Remember Me!', 'Do you want to save your credentials?')
                        break
                    if kk:
                        back_to_menu(sale=sale)
                    else:
                        messagebox._show(
                            'Processing', 'Invoices are being downloaded\nfrom cloud. Press OK', _icon='info', _type=messagebox.OK)
                        respbkup = restoreMain(
                            cName, sMonth, username=credd_user, password=credd_pass, rememberMe=credd_save)
                        if type(respbkup) == list:
                            messagebox._show(
                                'Error', respbkup[0], _icon='error', _type=messagebox.OK)
                            back_to_menu(sale=sale)
                        elif type(respbkup) == bool and respbkup == True:
                            messagebox.showinfo(
                                'Success', 'Data was successfully downloaded from cloud and is available in offline utility.')
                            back_to_menu(sale=sale)
            else:
                messagebox._show(
                    'Processing', 'Invoices are being downloaded\nfrom cloud. Press OK', _icon='info', _type=messagebox.OK)
                respbkup = restoreMain(cName, sMonth, hashed=True)
                if type(respbkup) == list:
                    messagebox._show(
                        'Error', respbkup[0], _icon='error', _type=messagebox.OK)
                    back_to_menu(sale=sale)
                elif type(respbkup) == bool and respbkup == True:
                    messagebox.showinfo(
                        'Success', 'Data was successfully downloaded from cloud and is available in offline utility.')
                    back_to_menu(sale=sale)
    elif todoAction == 'Import Invoices':
        importExtensions.ExtensionExecuter(companyGSTIN, cName, sMonth, sale)
        back_to_menu(sale=sale)

def screen2(sale = True):
    '''
    Function responsible for placing the Menu Screen (screen2) (screen after company is selected)
    
    sale : bool
        True if Sale Invoicing is selected
        False if Purchase Invoicing is selected
    '''
    # make frame_7 global
    global frame_7
    
    # designing
    frame_7 = tk.Frame(frame_0, height=screendim, width=screendim)
    label_7 = tk.Label(frame_7)
    label_7.config(
        cursor='arrow', font='{Helventica} 36 {}', text='offlineGST', bg=headingcolor1)
    label_7.pack(anchor='w', padx=5, side='top')
    label_10 = tk.Label(frame_7)
    label_10.config(justify='right',
                    text='Company: {}\nGSTIN: {}'.format(cName, companyGSTIN))
    label_10.pack(anchor='e', side='top')
    label_1_2 = tk.Label(frame_7)
    label_1_2.config(text='Month: {}'.format(sMonth))
    label_1_2.pack(anchor='e', side='top')
    widthframe_1_2 = tk.Frame(frame_7, width=screendim)
    widthframe_1_2.pack(side='top')
    label_7b = tk.Label(frame_7)
    label_7b.config(
        cursor='arrow', font='{Helventica} 20 {bold}', text='Summary: ({})'.format('Sale' if sale else 'Purchase'))
    label_7b.pack(anchor='w', side='top')
    label_11 = tk.Label(frame_7)
    label_11.config(takefocus=False, justify='left',
                    text='Total Invoices: {}\nTotal Taxable Value: {}\nTotal IGST Amount: {}\nTotal CGST/SGST Amount: {}'.format(*get_current_month_summary(sale=sale)))
    label_11.pack(anchor='w', padx=10, side='top')

    widthframe_1_2 = tk.Frame(frame_7, width=screendim, height=20)
    widthframe_1_2.pack(side='top')
    label_12 = tk.Label(frame_7)
    label_12.config(
        cursor='arrow', font='{Helventica} 16 {bold}', text='What do you want to do?:')
    label_12.pack(anchor='w', side='top')
    validActions = [
        'Add New Invoice',
        'Modify Invoice',
        'Delete Invoice(s)',
        'Export Invoices',
        'Backup Invoices',
        'Restore Invoices'
    ]
    # if Import Extensions are present, call them
    if importExtensionsFound:
        # 'importExtensions' works as an extension that adds an import method (not present normally)
        companyGSTINhashed = sha256(companyGSTIN.encode()).hexdigest()
        # ExtensionManager is called, which returns True if extension is meant for the company selected
        extFound = importExtensions.ExtensionManager(companyGSTINhashed)
        if extFound:
            # add the import option
            validActions.append('Import Invoices')
    
    # designing
    action_to_perform = tk.StringVar(value='-Select Action-')
    menubutton_12 = tk.OptionMenu(
        frame_7, action_to_perform, action_to_perform.get(), *validActions)
    menubutton_12.pack(padx=10, pady=5, anchor='w', side='top')

    def initialise_addInvoice(action_to_perform):
        '''
        Function that makes sure an action is selected from drop-down on the Menu Screen (screen2)
        '''
        if action_to_perform.get() == '-Select Action-':
            messagebox.showerror(
                'Action Error!', 'No Action selected, please select one to proceed.')
        else:
            frame_7.place_forget()
            action_perform(action_to_perform.get(), sale)
            
    # designing
    button_5 = tk.Button(
        frame_7, command=lambda: back_to_homescreen(frame_7), text='Go Back')
    button_5.pack(padx=10, side='left', anchor='w')
    buttom_5pre = tk.Button(frame_7)
    buttom_5pre.config(command=lambda: initialise_addInvoice(
        action_to_perform), text='Proceed')
    buttom_5pre.pack(padx=10, side='top', anchor='w')

    frame_7.config(height=screendim, width=screendim)
    frame_7.place(x=0, y=0)


def initialiseCompany(cName, sMonth):
    '''
    Function that opens an company by:
        - creating appropriate directories
        - declaring value of global variable companyGSTIN
    '''
    # using global variable companyGSTIN
    global companyGSTIN
    
    # checking if 'companies/' directory is present
    if not os.path.isdir(os.getcwd()+'/companies'):
        messagebox.showerror('No Companies Created!')
        return False
    
    # checking if selected company is present
    if not os.path.isdir(os.getcwd()+'/companies/'+cName):
        messagebox.showerror('Company not present!')
        return False
    
    # if selected month not initialised previously, initialise it
    if not os.path.isdir(os.getcwd()+'/companies/{}/{}'.format(cName, sMonth)):
        os.mkdir(os.getcwd()+'/companies/{}/{}'.format(cName, sMonth))
    
    # if GSTR1 file not created previously, create it
    if not os.path.isfile(os.getcwd()+'/companies/{}/{}/GSTR1.csv'.format(cName, sMonth)):
        tempCSVFileIn = open(
            os.getcwd()+'/companies/{}/{}/GSTR1.csv'.format(cName, sMonth), 'w', newline='')
        tempWriter = csv.writer(tempCSVFileIn)
        headerRow = ['GSTIN', 'Receiver Name', 'Invoice Number', 'Invoice Date', 'Invoice Value',
                     'Place Of Supply', 'Invoice Type', 'Rate', 'Taxable Amount', 'Cess Amount']
        tempWriter.writerow(headerRow)
        tempCSVFileIn.close()
        
    # if GSTR2 file not created previously, create it
    if not os.path.isfile(os.getcwd()+'/companies/{}/{}/GSTR2.csv'.format(cName, sMonth)):
        tempCSVFileIn = open(
            os.getcwd()+'/companies/{}/{}/GSTR2.csv'.format(cName, sMonth), 'w', newline='')
        tempWriter = csv.writer(tempCSVFileIn)
        headerRow = ['GSTIN', 'Supplier Name', 'Invoice Number', 'Invoice Date', 'Invoice Value',
                     'Place Of Supply', 'Invoice Type', 'Rate', 'Taxable Amount', 'Cess Amount']
        tempWriter.writerow(headerRow)
        tempCSVFileIn.close() 
       
    # previously entered GSTINS are retrieved from .PAST_GSTINS file
    global tempPASTGSTIN
    if not os.path.isfile(os.getcwd()+'/companies/{}/.PAST_GSTINS'.format(cName)):
        # if file not present, create it
        tempPASTGSTINfile = open(
            os.getcwd()+'/companies/{}/.PAST_GSTINS'.format(cName), 'wb')
        pickle.dump({}, tempPASTGSTINfile)
        tempPASTGSTIN = {}
        tempPASTGSTINfile.close()
    else:
        # if file present, retrieve data from it
        tempPASTGSTINfile = open(
            os.getcwd()+'/companies/{}/.PAST_GSTINS'.format(cName), 'rb')
        tempPASTGSTIN = pickle.load(tempPASTGSTINfile)
        tempPASTGSTINfile.close()

    # Retrieve companyGSTIN stored in local file .COMPANY_GSTIN
    companyGSTIN = open(os.getcwd(
    )+'/companies/{}/.COMPANY_GSTIN'.format(cName), 'r', newline='').read().strip()
    return True


def createCompDir(cName, cGSTIN):
    '''
    Function that creates required directories and files for the new company being created
    
    cName : str
    cGSTIN : str
    '''
    # convert to upper case
    cGSTIN = cGSTIN.get().upper()
    
    # error handling
    if cName.get() == '':
        messagebox.showerror('No Name', 'No Company Name provided!')
        return None
    if not re.fullmatch('[0-9]{2}[A-Z]{4}[0-9A-Z][0-9]{4}[A-Z]{1}[0-9A-Z]{3}', cGSTIN):
        messagebox.showerror(
            'Invalid GSTIN', 'The GSTIN Entered is invalid/incomplete!')
        return None
    
    # creating directory 'companies/'
    if not os.path.isdir(os.getcwd()+'/companies'):
        os.mkdir(os.getcwd()+'/companies')
    
    # checking if company already exists
    if os.path.isdir(os.getcwd()+'/companies/'+cName.get()):
        #messagebox.showinfo('Company Exists!','Company already exists! Do you wish to continue? (old data will be gone)',messagebox.YESNO)
        resp2 = messagebox._show(
            title='Company Exists!', message='Company already exists! Do you wish to continue? (old data will be gone)', _type=messagebox.YESNO, _icon='question')
        if resp2.lower() in ('yes', 'y'):
            rmtree(os.getcwd()+'/companies/'+cName.get())
        else:
            return None
    
    # making directory 'companies/cName'
    os.mkdir(os.getcwd()+'/companies/'+cName.get())
    
    # creating .COMPANY_GSTIN file to store companyGSTIN
    fileGSTIN = open(os.getcwd()+'/companies/'+cName.get() +
                     '/.COMPANY_GSTIN', 'w', newline='')
    fileGSTIN.write(cGSTIN)
    fileGSTIN.close()
    
    # creating .PAST_GSTINS file for storing old GSTIN & Name pairs
    fileGSTINS = open(os.getcwd()+'/companies/' +
                      cName.get()+'/.PAST_GSTINS', 'wb')
    pickle.dump({}, fileGSTINS)
    fileGSTINS.close()
    
    # show message that company creation was successsful
    messagebox.showinfo('Success!', 'New Company successfully created!')
    
    # go back to Home Screen
    back_to_homescreen(frame_1_2)


def createCompany():
    '''
    Function responsible for placing Create Company Page, and related actions
    '''
    # making frame_1_2 global
    global frame_1_2
    
    # designing
    frame_1_2 = tk.Frame(frame_0, height=screendim, width=screendim)
    label_5_6 = tk.Label(frame_1_2)
    label_5_6.config(font='{Helventica} 36 {}',
                     text='offlineGST', bg=headingcolor1)
    label_5_6.pack(anchor='w', side='top')
    label_7_8 = tk.Label(frame_1_2)
    label_7_8.config(font='{Helventica} 13 {italic}',
                     text='Create New Company:')
    label_7_8.pack(anchor='w', side='top')

    compGSTIN, compName = tk.StringVar(),tk.StringVar()

    def auto_partyname(event):
        # Fetches company name from GSTIN using API
        resppp = check_GSTIN(compGSTIN.get())
        if resppp:
            compName.set(resppp)
    
    label_10_11 = tk.Label(frame_1_2)
    label_10_11.config(text='Company GSTIN: ')
    label_10_11.pack(anchor='w', padx='20', side='top')
    entry_2_3 = tk.Entry(frame_1_2)
    entry_2_3.config(textvariable=compGSTIN)
    entry_2_3.pack(anchor='w', padx='40', side='top')
    entry_2_3.bind('<FocusOut>',auto_partyname)
    
    label_9 = tk.Label(frame_1_2)
    label_9.config(text='Company Name: ')
    label_9.pack(anchor='w', padx='20', side='top')
    entry_1 = tk.Entry(frame_1_2)
    entry_1.config(textvariable=compName)
    entry_1.pack(anchor='w', padx='40', side='top')
    
    
    button_1_2 = tk.Button(frame_1_2)
    button_1_2.config(text='Continue', command=partial(
        createCompDir, compName, compGSTIN))
    button_1_2.pack(anchor='w', pady='10', side='top')
    button_3 = tk.Button(frame_1_2)
    button_3.config(text='Back', command=lambda: back_to_homescreen(frame_1_2))
    button_3.pack(anchor='w', side='top')
    frame_1_2.config(height='300', width='300')
    frame_1_2.place(x=70, y=70)


def screen1():
    '''
    Function responsible for placing the Home/ Starting Screen, and related actions
    '''
    # checking for updates
    if check_for_update():
        # do not proceed further if update was installed
        return None
    
    # making cName, sMonth global
    global cName, sMonth

    def openMainMenu(companyName, selectedMonth, salemode):
        '''
        Function responsible for calling the Menu Screen opening function
        
        companyName : str
        selectedMonth : 
        '''
        # using global cName, sMonth
        global cName, sMonth
        
        # set variable values
        companyName, selMonth, salemod = companyName.get(), str(selectedMonth.get()), salemode.get()
        
        # check if company is selected
        if companyName == '-Select-': # or not re.fullmatch('[0-9]{2}/[0-9]{4}', selectedMonth):
            messagebox.showerror('Error!', 'No Company Selected!')
        else:
            # checking the type of month entered
            presentyear = datetime.now().year
            if re.fullmatch('[1-9]',selMonth):
                # if month entered like m (single digit), make it 0m/YYYY (YYYY is ongoing year)
                selMonth = '0{}/{}'.format(selMonth, presentyear)
                selectedMonth.set(selMonth)
            elif re.fullmatch('[1-9]/[0-9]{2}',selMonth):
                # if entered like m/yy, make it 0m/20yy
                selMonth = '0' + selMonth
                selMonth = selMonth.split('/')
                selMonth[-1] = '/20' + selMonth[-1]
                selMonth = ''.join(selMonth)
                selectedMonth.set(selMonth)                
            elif re.fullmatch('[0-1][1-9]',selMonth):
                # if entered like mm, make it mm/YYYY
                selMonth = '{}/{}'.format(selMonth, presentyear)
                selectedMonth.set(selMonth)
            elif re.fullmatch('[0-1][1-9]/[0-9]{2}',selMonth):
                # if entered like mm/yy, make it mm/20yy
                selMonth = selMonth.split('/')
                selMonth[-1] = '/20' + selMonth[-1]
                selMonth = ''.join(selMonth)
                selectedMonth.set(selMonth)
            elif re.fullmatch('[0-9]{2}/[0-9]{4}', selMonth):
                # if entered like mm/yyyy, keep it that way
                selMonth = selMonth
                selectedMonth.set(selMonth)
            else:
                # if entered in any other way / blank month
                messagebox.showerror('Invalid Month Selected!')
                return None
            
            # declaring values of global variables cName, sMonth
            cName, sMonth = str(companyName), '-'.join(str(selMonth).split('/'))
            
            # calling function to initialise company
            resp1 = initialiseCompany(cName, sMonth)
            if resp1:
                # if successfully created,
                sale = True if salemod == 'Sale' else False
                frame_1.place_forget()
                screen2(sale)

    def createCompany0():
        '''
        Function that removes Home Screen, and calls createCompany function
        '''
        frame_1.place_forget()
        createCompany()
    
    # making frame_1 global
    global frame_1
    
    # designing
    frame_1 = tk.Frame(frame_0, height=300, width=300)
    label_1 = tk.Label(frame_1)
    label_1.config(font='{Helventica} 48 {}',
                   text='offlineGST', bg=headingcolor1)
    label_1.pack(anchor='w', side='top')
    label_2 = tk.Label(frame_1)
    label_2.config(font='{Helventica} 12 {italic}',
                   text='Welcome to GSTR-1 Offline Utility.')
    label_2.pack(anchor='w', side='top')
    label_3 = tk.Label(frame_1)
    label_3.config(text='Select Company: ')
    label_3.pack(anchor='w', side='top')
    optionVar = tk.StringVar(frame_1, '-Select-')
    menubutton_1 = tk.OptionMenu(
        frame_1, optionVar, '-Select-', *get_companyDirectory())
    menubutton_1.pack(anchor='w', padx='50', side='top')
    label_4 = tk.Label(frame_1)
    label_4.config(text='Enter Month: ')
    label_4.pack(anchor='w', side='top')
    entry_2 = tk.Entry(frame_1)
    selectedMonth = tk.StringVar('')
    entry_2.config(textvariable=selectedMonth)
    _text_ = ''
    entry_2.delete('0', 'end')
    entry_2.insert('0', _text_)
    entry_2.pack(anchor='w', padx='50', side='top')
    
    label_3sale = tk.Label(frame_1)
    label_3sale.config(text='Select Invoice Mode: ')
    label_3sale.pack(anchor='w', side='top')
    optionVarSale = tk.StringVar(frame_1, 'Sale')
    menubutton_1Sale = tk.OptionMenu(
        frame_1, optionVarSale, 'Sale', 'Purchase')
    menubutton_1Sale.pack(anchor='w', padx='50', side='top')
    
    label_5 = tk.Label(frame_1)
    label_5.config(font='TkDefaultFont', text=' ')
    label_5.pack(padx='180', side='top')
    button_1 = tk.Button(frame_1)
    button_1.config(text='Continue')
    button_1.pack(anchor='w', side='top')
    button_1.configure(command=partial(openMainMenu, optionVar, selectedMonth, optionVarSale))
    button_2 = tk.Button(frame_1)
    button_2.config(text='Create New Company', command=createCompany0)
    button_2.pack(anchor='w', side='top')
    if enableExtensions:
        # if extensions are enabled, following adds 'Add Extension' button
        button_3 = tk.Button(frame_1)
        button_3.config(text='Add Extension', command=ExtensionInstaller)
        button_3.pack(anchor='w', side='top')
        
    label_6 = tk.Label(frame_1)
    label_6.config(text='\n')
    label_6.pack(side='top')
    frame_1.config(pady='10')
    frame_1.place(x=50, y=30)

frame_0.pack()
screen1()
toplevel_1.mainloop()
# --> END OF CODE <-- #