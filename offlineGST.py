import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import os
import re
from functools import partial
from shutil import rmtree
from urllib import request
import json
import csv
from random import randrange

from hashlib import sha256
from math import ceil
from urllib.request import quote
from re import fullmatch
import pickle
from urllib3 import PoolManager

'''
v2 - changelog
csv will be used in place of openpyxl to improve compatibility and efficiency.


'''

# Enter the path to the serverBackupScript.py on your server
#path_to_server_script = 'enter_path_here'
path_to_server_script = 'https://developer.bhuvannarula.cf/offlinegst/cgi-bin/5b057c8c23a641e9.py'


def get_companyDirectory():
    if not os.path.isdir('companies'):
        os.mkdir('companies')
    companyDirectory1=list(os.listdir(os.getcwd()+'/companies/'))
    companyDirectory = list(item for item in companyDirectory1 if item[0] != '.')
    return companyDirectory

headingcolor1='LightBlue'
toplevel_1 = tk.Tk(screenName='offlineGST',baseName='offlineGST',className='offlineGST')
toplevel_1.resizable(height=0,width=0)
frame_0 = tk.Frame(toplevel_1,height=400,width=400)

def get_placeofsupply(statecode):
    stcode = {'35': '35-Andaman and Nicobar Islands', '37': '37-Andhra Pradesh', '12': '12-Arunachal Pradesh', '18': '18-Assam', '10': '10-Bihar', '04': '04-Chandigarh', '22': '22-Chattisgarh', '26': '26-Dadra and Nagar Haveli', '25': '25-Daman and Diu', '07': '07-Delhi', '30': '30-Goa', '24': '24-Gujarat', '06': '06-Haryana', '02': '02-Himachal Pradesh', '01': '01-Jammu and Kashmir', '20': '20-Jharkhand', '29': '29-Karnataka', '32': '32-Kerala', '31': '31-Lakshadweep Islands', '23': '23-Madhya Pradesh', '27': '27-Maharashtra', '14': '14-Manipur', '17': '17-Meghalaya', '15': '15-Mizoram', '13': '13-Nagaland', '21': '21-Odisha', '34': '34-Pondicherry', '03': '03-Punjab', '08': '08-Rajasthan', '11': '11-Sikkim', '33': '33-Tamil Nadu', '36': '36-Telangana', '16': '16-Tripura', '09': '09-Uttar Pradesh', '05': '05-Uttarakhand', '19': '19-West Bengal'}
    return stcode[statecode]

def check_GSTIN(GSTIN):
    if not re.fullmatch('[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[0-9A-Z]{3}',GSTIN):
        return False
    webopener = request.urlopen('https://cleartax.in/f/compliance-report/{}/'.format(GSTIN))
    #response_gstin_tradename = webopener.request('GET','https://cleartax.in/f/compliance-report/{}/'.format(GSTIN)).data
    response_gstin_tradename= json.loads(webopener.read())
    response_gstin_tradename = response_gstin_tradename['taxpayerInfo']['tradeNam']
    if response_gstin_tradename == 'null':
        return False
    else:
        return response_gstin_tradename

def back_to_homescreen(currentFrame):
    currentFrame.place_forget()
    screen1()
    #frame_1.place(x=50,y=50)

def back_to_menu(currentFrame=None):
    if currentFrame:
        currentFrame.place_forget()
    screen2()

# functions for backup and restore start here -->

def backupMain(companyName,filingPeriod,hashed=False,username=None,password=None,rememberMe=False,path_to_server_script=path_to_server_script,packet_length=800):
    if not hashed:
        password = sha256(password.encode('ascii')).hexdigest()
    else:
        cookiesFileIN = open('.savedCred','rb')
        username,password = pickle.load(cookiesFileIN)
        cookiesFileIN.close()
    if rememberMe:
        cookiesFileIN = open('.savedCred','wb')
        pickle.dump((username,password),cookiesFileIN)
        cookiesFileIN.close()
    
    companyGSTINfile = open('companies/{}/.COMPANY_GSTIN'.format(companyName),'r')
    companyGSTIN = companyGSTINfile.read(15)
    companyGSTINfile.close()   
    
    def initialiseCSVdata():
        csvFileIN = open('companies/{}/{}/gstr1.csv'.format(companyName,filingPeriod),'r',newline='')
        csvFileReader = csv.reader(csvFileIN)
        next(csvFileReader)
        nestedTuple = tuple()
        for item in csvFileReader:
            #0,2,3,7,8
            item2 = item[2:3] + item[:1] + item[3:4] + item[7:9]
            nestedTuple += (tuple(item2),)
        return str(nestedTuple)
    
    rawCSVdata = initialiseCSVdata()
    csvDatatoUpload = quote(rawCSVdata,safe='')
    bytesToUpload = len(csvDatatoUpload)
    packets_count = ceil(bytesToUpload/packet_length)
    
    browser = PoolManager()
    firstRequest = browser.request('POST',path_to_server_script,
                                   fields={'Identification':'True',
                                           'mastermindname':username,
                                           'wizardspell':password,
                                           'hobbit':companyGSTIN,
                                           'book':filingPeriod.replace('-',''),
                                           'scrolls':packets_count}
                                   )
    authen_key_resp = firstRequest.data[:-1].decode('utf-8')
    if not fullmatch('[0-9a-zA-Z]{16}',authen_key_resp):
        return [authen_key_resp]
    
    # Now, packets will be sent one-by-one
    # Packets are used as max length for url should be <= 1024 (general idea on internet)
    # each packet will contain authen_key, curr_packet_no, packet_data
    # len(packet_data) = 800
    
    for curr_packet in range(packets_count):
        tempCSVbuffer = csvDatatoUpload[curr_packet*packet_length:(curr_packet+1)*packet_length]
        packetsSend = browser.request('POST',path_to_server_script,
                                fields={'ongoingmagic':'True',
                                        'secretspell':str(authen_key_resp),
                                        'hobbitage':str(curr_packet+1),
                                        'folklores':str(tempCSVbuffer)}
                                    )
        print(str(packetsSend.data[:-1].decode('utf-8')))
        if 'Received' not in str(packetsSend.data[:-1].decode('utf-8')):
            return ['Packet Lost! Backup Failed!']
        if 'Successful' in str(packetsSend.data[:-1].decode('utf-8')):
            return True

def registerNewUserCloud(username,password,path_to_server_script=path_to_server_script):
    browser = PoolManager()
    password = sha256(password.encode('ascii')).hexdigest()
    registerRequest = browser.request('POST',path_to_server_script,
                                   fields={'Learning':'True',
                                           'mastermindname':username,
                                           'wizardspell':password}
                                   )
    if 'Successful' in str(registerRequest.data[:-1].decode('utf-8')):
            return True
    else:
        return False

def restoreMain(companyName,filingPeriod,hashed=False,username=None,password=None,rememberMe=False,path_to_server_script=path_to_server_script,packet_length=800):
    browser = PoolManager()
    if not hashed:
        password = sha256(password.encode('ascii')).hexdigest()
    else:
        cookiesFileIN = open('.savedCred','rb')
        username,password = pickle.load(cookiesFileIN)
        cookiesFileIN.close()
    if rememberMe:
        cookiesFileIN = open('.savedCred','wb')
        pickle.dump((username,password),cookiesFileIN)
        cookiesFileIN.close()
    companyGSTIN = open('companies/{}/.COMPANY_GSTIN'.format(companyName),'r').read(15)
    restoreAuthen = browser.request('POST',path_to_server_script,
                                    fields={'getback':'True',
                                            'mastermindname':username,
                                            'wizardspell':password,
                                            'hobbit':companyGSTIN,
                                            'book':filingPeriod.replace('-',''),
                                            'scrolls':str(1)}
                                    )
    authen_key_resp = restoreAuthen.data[:-1].decode('utf-8')
    if 'Failed' in authen_key_resp:
        return ['Authentication Failed']
    else:  
        try:
            dataRec = eval(authen_key_resp)
            if type(dataRec) != tuple or (len(dataRec) != 0 and type(dataRec[0]) != tuple): # second part of second condition is for blank data
                raise ValueError
        except:
            return ['Authentication Failed/ Data Corrupt!']
    fileOUT = open('companies/{}/{}/gstr1.csv'.format(companyName,filingPeriod),'w',newline='')
    csvFinalWriter = csv.writer(fileOUT)
    headerRow = ['GSTIN','Receiver Name','Invoice Number','Invoice Date','Invoice Value','Place Of Supply','Invoice Type','Rate','Taxable Amount','Cess Amount']
    csvFinalWriter.writerow(headerRow)
    dataRec = list(dataRec)
    for item in dataRec:
        item2 = list(item)
        item2[5] = get_placeofsupply(item2[5])
        csvFinalWriter.writerow(item2)
    fileOUT.close()
    return True


# backup and restore functions end here -->



def get_current_month_summary():
    global pastInvoices,invoiceNumDateDict
    csvfileIn = open('companies/{}/{}/gstr1.csv'.format(cName,sMonth),'r',newline='')
    tempReader = csv.reader(csvfileIn)
    next(tempReader,None)
    data_summary = [0,0,0,0] #Total Invoices, Total Taxbl Val, Total Tax, Total Cess
    pastInvoices = []
    invoiceNumDateDict = {}
    for item in tempReader:
        pastInvoices.append(item[2])
        invoiceNumDateDict[item[2]] = item[3]
        data_summary[1]+=round(float(item[8]),2)
        data_summary[2]+=round(float(item[8])*float(item[7])/100,2)
        data_summary[3]+=round(float(item[9]),2)
    data_summary[0] = len(set(pastInvoices))
    return data_summary

def addNewInvoice(modify=False,reset=False):
    currInvNum = tk.StringVar()
    currInvDate = tk.StringVar()
    if len(pastInvoices) != 0:
        temp11 = re.search('([1-9]{1}[0-9]*)$',pastInvoices[-1]).groups()[0]
        currInvNum.set(pastInvoices[-1].split(temp11)[0]+str(int(temp11)+1))
        #currInvNum.set(pastInvoices[-1][:-1]+str(int(pastInvoices[-1][-1])+1))
        currInvDate.set(invoiceNumDateDict[pastInvoices[-1]])
    partyGSTIN = tk.StringVar()
    partyName = tk.StringVar()
    
    taxable0val = tk.StringVar(value='0.00')
    taxable5val = tk.StringVar(value='0.00')
    taxable12val = tk.StringVar(value='0.00')
    taxable18val = tk.StringVar(value='0.00')
    taxable28val = tk.StringVar(value='0.00')
    #taxablecessval = tk.StringVar('0.00')

    if reset == True:
        return currInvNum.get(),currInvDate.get()
    
    frame_3 = tk.Frame(frame_0,height=400,width=400)
    label_12 = tk.Label(frame_3)
    label_12.config(background='LightBlue', font='{Helventica} 36 {}', text='offlineGST')
    label_12.pack(anchor='w', side='top')
    label_13 = tk.Label(frame_3)
    label_13.config(font='{Helventica} 13 {italic}', text='Add New Invoice:')

    frame_16 = tk.Frame(frame_3)
    button_5 = tk.Button(frame_16)
    if modify:
        label_13.config(text='Modify Old Invoice:')
        csvFileIn = open('companies/{}/{}/gstr1.csv'.format(cName,sMonth),'r+',newline='')
        csvReaderData = list(csv.reader(csvFileIn))
        taxSeq = ['0','5','12','18','28']
        csvFileIn.seek(0)
        datalist_for_modify = []
        taxabledatalist_for_modify = ['0.00']*5
        final_csv_before_addmodify = []
        for item in csvReaderData:
            if item[2] == modify:
                taxabledatalist_for_modify[taxSeq.index(item[7])] = item[8]
                datalist_for_modify = item[:4]
            else:
                final_csv_before_addmodify.append(item)
        currInvNum.set(datalist_for_modify[2])
        currInvDate.set(datalist_for_modify[3])
        partyGSTIN.set(datalist_for_modify[0])
        partyName.set(datalist_for_modify[1])
        taxable0val.set(taxabledatalist_for_modify[0])
        taxable5val.set(taxabledatalist_for_modify[1])
        taxable12val.set(taxabledatalist_for_modify[2])
        taxable18val.set(taxabledatalist_for_modify[3])
        taxable28val.set(taxabledatalist_for_modify[4])
        button_5['state']='disabled'
        csvFileIn.truncate()
        csvWriter = csv.writer(csvFileIn)
        csvWriter.writerows(final_csv_before_addmodify)
        
    label_13.pack(anchor='w', pady='10', side='top')
    frame_4 = tk.Frame(frame_3)
    label_16 = tk.Label(frame_4)
    label_16.config(text='Invoice Number:')
    label_16.pack(anchor='w', side='left')
    entry_5 = tk.Entry(frame_4)
    
    entry_5.config(textvariable=currInvNum)
    _text_ = currInvNum.get()
    entry_5.delete('0', 'end')
    entry_5.insert('0', _text_)
    entry_5.pack(anchor='w', side='top')
    frame_4.config(height='200', width='200')
    frame_4.pack(anchor='w', padx='10', side='top')
    frame_5 = tk.Frame(frame_3)
    label_18 = tk.Label(frame_5)
    label_18.config(text='Invoice Date (dd/mm/yyyy):')
    label_18.pack(anchor='w', side='left')
    entry_6 = tk.Entry(frame_5)
    
    entry_6.config(textvariable=currInvDate, width='10')
    entry_6.pack(anchor='w', side='top')
    frame_5.config(height='200', width='200')
    frame_5.pack(anchor='w', padx='10', side='top')
    frame_6 = tk.Frame(frame_3)
    label_19 = tk.Label(frame_6)
    label_19.config(text='Party GSTIN:')
    label_19.pack(anchor='w', side='left')
    entry_7 = tk.Entry(frame_6)
    frame_7_8 = tk.Frame(frame_3)
    entry_8 = tk.Entry(frame_7_8)
    def autopartyname(event):
        if event.widget==entry_7 and re.fullmatch('[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[0-9A-Z]{3}',partyGSTIN.get()):
            foundGSTIN = check_GSTIN(partyGSTIN.get())
            if foundGSTIN:
                partyName.set(foundGSTIN)
                entry_8.insert('0',foundGSTIN)
    entry_7.config(textvariable=partyGSTIN, width='15')
    entry_7.bind('<FocusOut>',autopartyname)
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
    #cess feature depriciated, will be revived in future on demand
    '''
    label_35 = tk.Label(frame_14)
    label_35.config(text='Cess:')
    label_35.pack(anchor='w', side='left')
    entry_17 = tk.Entry(frame_14)
    entry_17.config(textvariable=taxablecessval, width='10')
    entry_17.pack(side='top')
    '''
    frame_14.config(height='200', width='200')
    frame_14.pack(anchor='w', padx='20', side='top')
    #frame_16 = tk.Frame(frame_3)
    #button_5 = tk.Button(frame_16)
    button_5.config(text='Go Back',command=lambda : back_to_menu(frame_3))
    button_5.pack(anchor='w', side='left')
    def showError(message):
        messagebox.showerror('Wrong Input!',message)

    def push_data_to_excel(invNum,invDate,partyGSTIN,partyName,taxamountlists):
        csvFileIn = open('companies/{}/{}/gstr1.csv'.format(cName,sMonth),'a+',newline='')
        csvWriter = csv.writer(csvFileIn)
        taxSeq = ['0','5','12','18','28']
        totalInvValue = sum(list((100+float(taxSeq[i[0]]))*float(i[1])/100 for i in enumerate(taxamountlists)))
        for taxItem in enumerate(taxamountlists):
            if taxItem[1] != 0:
                pastInvoices.append(invNum.get())
                invoiceNumDateDict[invNum.get()] = invDate.get()
                csvWriter.writerow([partyGSTIN.get(),partyName.get(),invNum.get(),invDate.get(),totalInvValue,get_placeofsupply(partyGSTIN.get()[:2]),'Regular',taxSeq[taxItem[0]],taxItem[1],'0.00'])
        csvFileIn.flush()
        csvFileIn.close()
        return True
    
    def check_valid_newInvoice_input():
        ttaxvallist = list(round(float(ii.get()),2) for ii in [taxable0val,taxable5val,taxable12val,taxable18val,taxable28val])
        if currInvNum.get() in (None,''):
            showError('No invoice number entered!')
            return False
        elif not re.fullmatch('[0-9]{2}/[0-9]{2}/[0-9]{4}',currInvDate.get()):
            showError('Wrong/Incomplete Date Entered!')
            return False
        elif len(partyGSTIN.get()) == 2 and partyName.get() in ('',None):
            pass
        elif not re.fullmatch('[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[0-9A-Z]{3}',partyGSTIN.get()):
            showError('Wrong/Incomplete GSTIN Entered!')
            return False
        elif partyName.get() in (None,''):
            showError('No Party Name entered!')
            return False
        elif round(sum(ttaxvallist),0) == 0:
            showError('No Tax Values entered!')
            return False
        elif currInvNum.get() in pastInvoices:
            showError('Bill adding failed. Bill is already present!')
            return False
        resp = push_data_to_excel(currInvNum,currInvDate,partyGSTIN,partyName,ttaxvallist)
        if resp:
            button_5['state']='normal'
            moreCond = messagebox._show('Success!','Bill has been added successfully. Do you want to enter another bill?',_icon='info',_type=messagebox.YESNO)
            if moreCond.lower() in ('yes','y'):
                entry_5.delete('0','end')
                entry_6.delete('0','end')
                entry_7.delete('0','end')
                entry_8.delete('0','end')
                entry_9.delete('0','end')
                entry_9.insert('0','0.00')
                entry_15.delete('0','end')
                entry_15.insert('0','0.00')
                entry_11.delete('0','end')
                entry_11.insert('0','0.00')
                entry_16.delete('0','end')
                entry_16.insert('0','0.00')
                entry_13.delete('0','end')
                entry_13.insert('0','0.00')
                respNumDate = addNewInvoice(reset=True)
                entry_5.insert('0',respNumDate[0])
                entry_6.insert('0',respNumDate[1])
            else:
                back_to_menu(frame_3)
    button_6 = tk.Button(frame_16)
    button_6.config(text='Proceed',command=check_valid_newInvoice_input)
    button_6.pack(padx='10', side='top')
    frame_16.config(height='200', width='200')
    frame_16.pack(anchor='w', padx='10', pady='10', side='top')
    frame_3.config(height='400', takefocus=True, width='400')
    frame_3.pack(side='top')
    frame_3.config(height='400', takefocus=True, width='400')
    frame_3.pack(side='top')
    frame_3.place(x=0,y=0)

def deleteInvoice(invNums):
    confirmresp = messagebox._show('Warning!','Invoices with following Invoice Numbers will be deleted: \n{}\n Are you sure?'.format(invNums),_icon='warning',_type=messagebox.YESNO)
    if confirmresp.lower() not in ('yes','y'):
        return False
    invNums=(invNums.replace(' ','')).split(',')
    csvFileIn = open('companies/{}/{}/gstr1.csv'.format(cName,sMonth),'r+',newline='')
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
    messagebox.showinfo('Success!','Invoice(s) deleted successfully!')
    return True

def exportInvoices():
    csvFileIn = open('companies/{}/{}/gstr1.csv'.format(cName,sMonth),newline='')
    csvFileReader = list(csv.reader(csvFileIn))
    csvFileReader = csvFileReader[1:]
    b2bdata = []
    b2btaxable = [0,0,0] # taxable, cgst, igst
    b2cs = {}
    taxRate = ['0','5','12','18','28']

    for item in csvFileReader:
        if len(item[0]) != 2:
            b2bdata.append(item)
            b2btaxable[0]+=round(float(item[8]),2)
            if companyGSTIN[:2] == item[0][:2]:
                b2btaxable[1] += round(float(item[8])*float(item[7])/200,2)
            else:
                b2btaxable[2] += round(float(item[8])*float(item[7])/100,2)
        else:
            if item[0] not in b2cs:
                b2cs[item[0]] = [0,0,0,0,0]
            b2cs[item[0]][taxRate.index(item[7])] += round(float(item[8]),2)

    try:
        os.mkdir(os.getcwd()+'/export')
    except:
        None


    ### b2b data to json starts here
    b2bfinaldata = {}

    for i in b2bdata:
        if i[0] not in b2bfinaldata:
            b2bfinaldata[i[0]] = {i[2]:[i[3],{i[7]:i[8]}]}
        else:
            if i[2] not in b2bfinaldata[i[0]]:
                b2bfinaldata[i[0]][i[2]] = [i[3],{i[7]:i[8]}]
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
            tempBill['idt'] = b2bfinaldata[gstin][invNum][0].replace('/','-')
            tempBill['pos'] = gstin[:2]
            tempBill['rchrg'] = 'N'
            tempBill['inv_typ'] = 'R'
            tempSumTotal = 0
            tempBill['itms'] = []
            for i in range(len(b2bfinaldata[gstin][invNum][1])):
                tempBill['itms'].append({})
                tempBill['itms'][-1]['num'] = i+1
                tempBill['itms'][-1]['itm_det'] = {}
                tempBill['itms'][-1]['itm_det']['rt'] = int(list(b2bfinaldata[gstin][invNum][1].keys())[i])
                tempBill['itms'][-1]['itm_det']['txval'] = round(float(b2bfinaldata[gstin][invNum][1][list(b2bfinaldata[gstin][invNum][1].keys())[i]]),2)
                temptaxamount = [0,0,0]
                if gstin[:2] == companyGSTIN[:2]:
                    temptaxamount[1] = round(float(list(b2bfinaldata[gstin][invNum][1].keys())[i]) * round(float(b2bfinaldata[gstin][invNum][1][list(b2bfinaldata[gstin][invNum][1].keys())[i]]),2) / 200,2)
                    temptaxamount[2] = round(temptaxamount[1],2)
                else:
                    temptaxamount[0] = round(float(list(b2bfinaldata[gstin][invNum][1].keys())[i]) * round(float(b2bfinaldata[gstin][invNum][1][list(b2bfinaldata[gstin][invNum][1].keys())[i]]),2) / 100,2)
                tempBill['itms'][-1]['itm_det']['iamt'] = temptaxamount[0]
                tempBill['itms'][-1]['itm_det']['camt'] = temptaxamount[1]
                tempBill['itms'][-1]['itm_det']['csamt'] = 0
                tempBill['itms'][-1]['itm_det']['samt'] = temptaxamount[2]
                tempSumTotal+= sum(temptaxamount) + round(float(b2bfinaldata[gstin][invNum][1][list(b2bfinaldata[gstin][invNum][1].keys())[i]]),2)
            tempBill['val'] = round(tempSumTotal,2)
            b2bObject[-1]['inv'].append(tempBill)

    ### b2b to json ends here


    #print(str(b2bObject))

    ### b2cs to json starts here
    b2csfinaldata = []
    rateList = [0,5,12,18,28]
    for i in b2cs:
        for j in range(len(b2cs[i])):
            if i == companyGSTIN[:2]:
                if int(b2cs[i][j]) == 0:
                    continue
                temprecord = {}
                temprecord['sply_ty'] = 'INTRA'
                temprecord['txval'] = b2cs[i][j]
                temprecord['typ'] = 'OE'
                temprecord['pos'] = i
                temprecord['rt'] = rateList[j]
                temprecord['iamt'] = 0
                temprecord['camt'] = b2cs[i][j]*rateList[j]/200
                temprecord['samt'] = temprecord['camt']
                temprecord['csamt'] = 0
            else:
                if int(b2cs[i][j]) == 0:
                    continue
                temprecord = {}
                temprecord['sply_ty'] = 'INTER'
                temprecord['txval'] = b2cs[i][j]
                temprecord['typ'] = 'OE'
                temprecord['pos'] = i
                temprecord['rt'] = rateList[j]
                temprecord['iamt'] = b2cs[i][j]*rateList[j]/100
                temprecord['camt'] = 0
                temprecord['samt'] = temprecord['camt']
                temprecord['csamt'] = 0
            b2csfinaldata.append(temprecord)

    ###b2cs to json ends here
    finalJSON = {}
    finalJSON['gstin'] = companyGSTIN
    finalJSON['fp'] = sMonth.replace('-','')
    if b2bObject != []:
        finalJSON['b2b'] = b2bObject
    if b2csfinaldata != []:
        finalJSON['b2cs'] = b2csfinaldata
    finalJSON['hash'] = 'hash'
    finalJSON['version'] = 'GST1.00'
    
    randomIdentifier = randrange(10000,100000)
    JSONfile = open('export/export-json-{}-{}-{}.json'.format(cName,sMonth,randomIdentifier),'w')
    json.dump(finalJSON,JSONfile)
    JSONfile.close()
    return True
    
def action_perform(todoAction):
    if todoAction == 'Add New Invoice':
        addNewInvoice()
    elif todoAction == 'Delete Invoice(s)':
        invNums = simpledialog.askstring('Delete Invoice(s)','Enter Invoice Numbers of Invoices to be deleted, separated by "," like 100,200,300')
        deleteInvoice(invNums)
        back_to_menu()
    elif todoAction == 'Modify Invoice':
        while True:
            invNumModify = simpledialog.askstring('Modify Invoice','Enter Invoice Number of Invoice to be modified:')
            if invNumModify not in pastInvoices:
                invNumModify = simpledialog.askstring('Not Found!','Invoice Number entered is not present. Please enter correct number.')
            else:
                break
        addNewInvoice(modify=invNumModify)
    elif todoAction == 'Export Invoices':
        resp1 = messagebox._show('Are you sure?','The invoices will be exported. Are you sure you want to continue?',_icon='info',_type=messagebox.YESNO)
        if resp1.lower() in ('yes','y'):
            resp2 = exportInvoices()
            if resp2:
                messagebox.showinfo('Success!','The invoices have been exported successfully, and JSON file is now present in "export" folder. ')
                back_to_menu()
    elif todoAction == 'Backup Invoices':
        messagebox._show('Caution','The invoices of selected period will be uploaded to cloud.',_icon='info',_type=messagebox.OK)
        if True:
            if not os.path.isfile('.savedCred'):
                respRegister = messagebox.askyesno('Login/Register','Do you want to login or register?\n(Click Yes to Login, Click No to Register)')
                
                if not respRegister:
                    kr = False
                    while True:
                        credd_user = simpledialog.askstring('Register','Enter Username (max_length=20, only alphabet & numbers accepted):')
                        if credd_user == None:
                            kr = True
                            break
                        if len(credd_user) >= 20 or len(re.fullmatch('[0-9a-zA-Z]+',credd_user).group()) != len(credd_user):
                            messagebox.showerror('Invalid!','Invalid Username! (max_length=20,\nonly alphabet & numbers\naccepted)')
                            continue
                        credd_pass = simpledialog.askstring('Register','Enter Password:')
                        if credd_pass == None:
                            kr = True
                            break
                        break          
                    if kr:
                        back_to_menu()
                    respregisternew = registerNewUserCloud(credd_user,credd_pass)
                    if respregisternew:
                        messagebox.showinfo('Success!','New User registered successfully!')
                    else:
                        messagebox.showerror('Failed!','New User Registeration failed!')
                        back_to_menu()
                else:
                    kk = False
                    while True:
                        credd_user = simpledialog.askstring('Login','Enter Username (max_length=20, only alphabet & numbers accepted):')
                        if credd_user == None:
                            kk = True
                            break
                        if len(credd_user) >= 20 or len(re.fullmatch('[0-9a-zA-Z]+',credd_user).group()) != len(credd_user):
                            messagebox.showerror('Invalid!','Invalid Username! (max_length=20,\nonly alphabet & numbers\naccepted)')
                            continue
                        credd_pass = simpledialog.askstring('Login','Enter Password:')
                        if credd_pass == None:
                            kk = True
                            break
                        credd_save = messagebox.askyesno('Remember Me!','Do you want to save your credentials?')
                        break
                    if kk:
                        back_to_menu()
                    else:
                        messagebox._show('Processing','Invoices are being uploaded\nto cloud. Press OK',_icon='info',_type=messagebox.OK)
                        respbkup = backupMain(cName,sMonth,username=credd_user,password=credd_pass,rememberMe=credd_save)
                        if type(respbkup) == list:
                            messagebox._show('Error',respbkup[0],_icon='error',_type=messagebox.OK)
                            back_to_menu()
                        elif type(respbkup) == bool and respbkup == True:
                            messagebox.showinfo('Success','Data was successfully uploaded to cloud and will be available to restore.')
                            back_to_menu()
            else:
                messagebox._show('Processing','Invoices are being uploaded\nto cloud. Press OK',_icon='info',_type=messagebox.OK)
                respbkup = backupMain(cName,sMonth,hashed=True)
                if type(respbkup) == list:
                    messagebox._show('Error',respbkup[0],_icon='error',_type=messagebox.OK)
                    back_to_menu()
                elif type(respbkup) == bool and respbkup == True:
                    messagebox.showinfo('Success','Data was successfully uploaded to cloud and will be available to restore.')
                    back_to_menu()
    elif todoAction == 'Restore Invoices':
        messagebox._show('Caution','The invoices of selected period will be restored from cloud.',_icon='info',_type=messagebox.OK)
        if True:
            if not os.path.isfile('.savedCred'):
                respRegister = messagebox.askyesno('Login/Register','Do you want to login or register?\n(Click Yes to Login, Click No to Register)')
                
                if not respRegister:
                    kr = False
                    while True:
                        credd_user = simpledialog.askstring('Register','Enter Username (max_length=20, only alphabet & numbers accepted):')
                        if credd_user == None:
                            kr = True
                            break
                        if len(credd_user) >= 20 or len(re.fullmatch('[0-9a-zA-Z]+',credd_user).group()) != len(credd_user):
                            messagebox.showerror('Invalid!','Invalid Username! (max_length=20,\nonly alphabet & numbers\naccepted)')
                            continue
                        credd_pass = simpledialog.askstring('Register','Enter Password:')
                        if credd_pass == None:
                            kr = True
                            break
                        break          
                    if kr:
                        back_to_menu()
                    respregisternew = registerNewUserCloud(credd_user,credd_pass)
                    if respregisternew:
                        messagebox.showinfo('Success!','New User registered successfully!')
                    else:
                        messagebox.showerror('Failed!','New User Registeration failed!')
                        back_to_menu()
                else:
                    kk = False
                    while True:
                        credd_user = simpledialog.askstring('Login','Enter Username (max_length=20, only alphabet & numbers accepted):')
                        if credd_user == None:
                            kk = True
                            break
                        if len(credd_user) >= 20 or len(re.fullmatch('[0-9a-zA-Z]+',credd_user).group()) != len(credd_user):
                            messagebox.showerror('Invalid!','Invalid Username! (max_length=20,\nonly alphabet & numbers\naccepted)')
                            continue
                        credd_pass = simpledialog.askstring('Login','Enter Password:')
                        if credd_pass == None:
                            kk = True
                            break
                        credd_save = messagebox.askyesno('Remember Me!','Do you want to save your credentials?')
                        break
                    if kk:
                        back_to_menu()
                    else:
                        messagebox._show('Processing','Invoices are being downloaded\nfrom cloud. Press OK',_icon='info',_type=messagebox.OK)
                        respbkup = restoreMain(cName,sMonth,username=credd_user,password=credd_pass,rememberMe=credd_save)
                        if type(respbkup) == list:
                            messagebox._show('Error',respbkup[0],_icon='error',_type=messagebox.OK)
                            back_to_menu()
                        elif type(respbkup) == bool and respbkup == True:
                            messagebox.showinfo('Success','Data was successfully downloaded from cloud and is available in offline utility.')
                            back_to_menu()
            else:
                messagebox._show('Processing','Invoices are being downloaded\nfrom cloud. Press OK',_icon='info',_type=messagebox.OK)
                respbkup = restoreMain(cName,sMonth,hashed=True)
                if type(respbkup) == list:
                    messagebox._show('Error',respbkup[0],_icon='error',_type=messagebox.OK)
                    back_to_menu()
                elif type(respbkup) == bool and respbkup == True:
                    messagebox.showinfo('Success','Data was successfully downloaded from cloud and is available in offline utility.')
                    back_to_menu()        

def screen2():
    global frame_7
    frame_7 = tk.Frame(frame_0,height=400,width=400)
    label_7 = tk.Label(frame_7)
    label_7.config(cursor='arrow', font='{Helventica} 36 {}', text='offlineGST',bg=headingcolor1)
    label_7.pack(anchor='w', padx=5, side='top')
    label_10 = tk.Label(frame_7)
    label_10.config(justify='right', text='Company: {}\nGSTIN: {}'.format(cName,companyGSTIN))
    label_10.pack(anchor='e', side='top')
    label_1_2 = tk.Label(frame_7)
    label_1_2.config(text='Month: {}'.format(sMonth))
    label_1_2.pack(anchor='e', side='top')
    widthframe_1_2 = tk.Frame(frame_7,width=400)
    widthframe_1_2.pack(side='top')
    label_7b = tk.Label(frame_7)
    label_7b.config(cursor='arrow', font='{Helventica} 20 {bold}', text='Summary:')
    label_7b.pack(anchor='w',side='top')
    label_11 = tk.Label(frame_7)
    label_11.config(takefocus=False, justify='left',text='Total Invoices: {}\nTotal Taxable Value: {}\nTotal Tax Amount: {}\nTotal Cess Amount: {}'.format(*get_current_month_summary()))
    label_11.pack(anchor='w', padx=10, side='top')
    
    widthframe_1_2 = tk.Frame(frame_7,width=400,height=20)
    widthframe_1_2.pack(side='top')
    label_12 = tk.Label(frame_7)
    label_12.config(cursor='arrow', font='{Helventica} 16 {bold}', text='What do you want to do?:')
    label_12.pack(anchor='w',side='top')
    validActions = [
        'Add New Invoice',
        'Modify Invoice',
        'Delete Invoice(s)',
        'Export Invoices',
        'Backup Invoices',
        'Restore Invoices'
    ]
    action_to_perform= tk.StringVar(value='-Select Action-')
    menubutton_12 = tk.OptionMenu(frame_7,action_to_perform,action_to_perform.get(),*validActions)
    menubutton_12.pack(padx=10,pady=5,anchor='w',side='top')
    def initialise_addInvoice(action_to_perform):
        if action_to_perform.get() == '-Select Action-':
            messagebox.showerror('Action Error!','No Action selected, please select one to proceed.')
        else:
            frame_7.place_forget()
            action_perform(action_to_perform.get())
    button_5 = tk.Button(frame_7,command=lambda:back_to_homescreen(frame_7),text='Go Back')
    button_5.pack(padx=10,side='left',anchor='w')
    buttom_5pre = tk.Button(frame_7)
    buttom_5pre.config(command=lambda:initialise_addInvoice(action_to_perform),text='Proceed')
    buttom_5pre.pack(padx=10,side='top',anchor='w')

    frame_7.config(height='400', width='400')
    frame_7.place(x=0,y=0)

def initialiseCompany(cName,sMonth):
    global companyGSTIN
    if not os.path.isdir(os.getcwd()+'/companies'):
        messagebox.showerror('No Companies Created!')
        return False
    if not os.path.isdir(os.getcwd()+'/companies/'+cName):
        messagebox.showerror('Company not present!')
        return False
    if not os.path.isdir(os.getcwd()+'/companies/{}/{}'.format(cName,sMonth)):
        os.mkdir(os.getcwd()+'/companies/{}/{}'.format(cName,sMonth))
    if not os.path.isfile('companies/{}/{}/gstr1.csv'.format(cName,sMonth)):
        tempCSVFileIn = open('companies/{}/{}/gstr1.csv'.format(cName,sMonth),'w',newline='')
        tempWriter = csv.writer(tempCSVFileIn)
        headerRow = ['GSTIN','Receiver Name','Invoice Number','Invoice Date','Invoice Value','Place Of Supply','Invoice Type','Rate','Taxable Amount','Cess Amount']
        tempWriter.writerow(headerRow)
        tempCSVFileIn.close()
    companyGSTIN = open('companies/{}/.COMPANY_GSTIN'.format(cName),'r',newline='').read().strip()
    return True

def createCompDir(cName,cGSTIN):
    cGSTIN = cGSTIN.get().upper()
    if cName.get() == '':
        messagebox.showerror('No Name','No Company Name provided!')
        return None
    if not re.fullmatch('[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[0-9A-Z]{3}',cGSTIN):
        messagebox.showerror('Invalid GSTIN','The GSTIN Entered is invalid/incomplete!')
        return None
    if not os.path.isdir(os.getcwd()+'/companies'):
        os.mkdir(os.getcwd()+'/companies')
    if os.path.isdir(os.getcwd()+'/companies/'+cName.get()):
        #messagebox.showinfo('Company Exists!','Company already exists! Do you wish to continue? (old data will be gone)',messagebox.YESNO)
        resp2 = messagebox._show(title='Company Exists!',message='Company already exists! Do you wish to continue? (old data will be gone)',_type=messagebox.YESNO,_icon='question')
        if resp2.lower() in ('yes','y'):
            rmtree(os.getcwd()+'/companies/'+cName.get())
        else:
            return None
    os.mkdir(os.getcwd()+'/companies/'+cName.get())
    fileGSTIN = open(os.getcwd()+'/companies/'+cName.get()+'/.COMPANY_GSTIN','w',newline='')
    fileGSTIN.write(cGSTIN)
    fileGSTIN.close()
    messagebox.showinfo('Success!','New Company successfully created!')
    back_to_homescreen(frame_1_2)
    
def createCompany():
    global frame_1_2
    frame_1_2 = tk.Frame(frame_0,height=400,width=400)
    label_5_6 = tk.Label(frame_1_2)
    label_5_6.config(font='{Helventica} 36 {}', text='offlineGST',bg=headingcolor1)
    label_5_6.pack(anchor='w', side='top')
    label_7_8 = tk.Label(frame_1_2)
    label_7_8.config(font='{Helventica} 13 {italic}', text='Create New Company:')
    label_7_8.pack(anchor='w', side='top')
    label_9 = tk.Label(frame_1_2)
    label_9.config(text='Company Name: ')
    label_9.pack(anchor='w', padx='20', side='top')
    entry_1 = tk.Entry(frame_1_2)
    compName = tk.StringVar()
    entry_1.config(textvariable=compName)
    entry_1.pack(anchor='w', padx='40', side='top')
    label_10_11 = tk.Label(frame_1_2)
    label_10_11.config(text='Company GSTIN: ')
    label_10_11.pack(anchor='w', padx='20', side='top')
    entry_2_3 = tk.Entry(frame_1_2)
    compGSTIN = tk.StringVar()
    entry_2_3.config(textvariable=compGSTIN)
    entry_2_3.pack(anchor='w', padx='40', side='top')
    button_1_2 = tk.Button(frame_1_2)
    button_1_2.config(text='Continue',command=partial(createCompDir,compName,compGSTIN))
    button_1_2.pack(anchor='w',pady='10', side='top')
    button_3 = tk.Button(frame_1_2)
    button_3.config(text='Back',command=lambda:back_to_homescreen(frame_1_2))
    button_3.pack(anchor='w', side='top')
    frame_1_2.config(height='300', width='300')
    frame_1_2.place(x=70,y=70)

def screen1():
    global cName,sMonth
    def openMainMenu(companyName,selectedMonth):
        global cName,sMonth
        companyName,selectedMonth = companyName.get(),selectedMonth.get()
        if companyName == '-Select-' or not re.fullmatch('[0-9]{2}/[0-9]{4}',selectedMonth):
            messagebox.showerror('Error!','No Company/Month Selected!')
        else:
            cName,sMonth = str(companyName),'-'.join(str(selectedMonth).split('/'))
            #frame_1.place_forget()
            resp1 = initialiseCompany(cName,sMonth)
            if resp1:
                frame_1.place_forget()
                screen2()
    def createCompany0():
        frame_1.place_forget()
        createCompany()
    global frame_1
    frame_1 = tk.Frame(frame_0,height=300,width=300)
    label_1 = tk.Label(frame_1)
    label_1.config(font='{Helventica} 48 {}', text='offlineGST',bg=headingcolor1)
    label_1.pack(anchor='w', side='top')
    label_2 = tk.Label(frame_1)
    label_2.config(font='{Helventica} 12 {italic}', text='Welcome to GSTR-1 Offline Utility.')
    label_2.pack(anchor='w', side='top')
    label_3 = tk.Label(frame_1)
    label_3.config(text='Select Company: ')
    label_3.pack(anchor='w', side='top')
    optionVar = tk.StringVar(frame_1,'-Select-')
    menubutton_1 = tk.OptionMenu(frame_1,optionVar,'-Select-',*get_companyDirectory())
    menubutton_1.pack(anchor='w', padx='50', side='top')
    label_4 = tk.Label(frame_1)
    label_4.config(text='Enter Month (mm/yyyy): ')
    label_4.pack(anchor='w', side='top')
    entry_2 = tk.Entry(frame_1)
    selectedMonth = tk.StringVar('')
    entry_2.config(textvariable=selectedMonth)
    _text_ = ''
    entry_2.delete('0', 'end')
    entry_2.insert('0', _text_)
    entry_2.pack(anchor='w', padx='50', side='top')
    label_5 = tk.Label(frame_1)
    label_5.config(font='TkDefaultFont', text=' ')
    label_5.pack(padx='180', side='top')
    button_1 = tk.Button(frame_1)
    button_1.config(text='Continue')
    button_1.pack(anchor='w', side='top')
    button_1.configure(command=partial(openMainMenu,optionVar,selectedMonth))
    button_2 = tk.Button(frame_1)

    button_2.config(text='Create New Company',command=createCompany0)
    button_2.pack(anchor='w', side='top')
    label_6 = tk.Label(frame_1)
    label_6.config(text='\n')
    label_6.pack(side='top')
    frame_1.config(pady='10')
    frame_1.place(x=50,y=50)

screen1()

frame_0.pack()

toplevel_1.mainloop()

