#!/usr/bin/python3.7

from requests.compat import unquote
from hashlib import sha256
import cgi
import cgitb
from dotenv import dotenv_values
import mysql.connector as conn

'''
Following files and folders are present in same directory as this file:

- .env

Following tables will be created in the working database:
masterminds
current_sessions
spcookies
one table for each username registered
'''
print('Content-type: text/html\n')

ENVV = dotenv_values()

connection = conn.connect(
    host=ENVV['HOSTNAME'],
    user=ENVV['USERNAME'],
    passwd=ENVV['PASSWORD'],
    database=ENVV['DATABASE']
)

mCursor = connection.cursor()

dataReceived = cgi.FieldStorage()


def generate_hash(string, length):
    enc_name = sha256(str(string).encode('ascii')).hexdigest()[:length]
    return enc_name


def create_newuser_table(tableName, cursored):
    cursored.execute('''
                    CREATE TABLE {} (
                        work_company_gstin CHAR(15) NOT NULL,
                        filing_period CHAR(6) NOT NULL,
                        inv_no VARCHAR(10) NOT NULL,
                        GSTIN VARCHAR(15) NOT NULL,
                        inv_date CHAR(10) NOT NULL,
                        inv_rate VARCHAR(2) NOT NULL,
                        inv_taxbl VARCHAR(10) NOT NULL,
                        PRIMARY KEY(inv_no,inv_rate)
                    )
                    '''.format(tableName))
    return list(i for i in cursored)


if str(dataReceived.getvalue('Identification')) == 'True':
    def check_user_cred():
        try:
            user_chk = str(dataReceived.getvalue('mastermindname'))
            pass_chk = str(dataReceived.getvalue('wizardspell'))
            work_company_gstin = str(dataReceived.getvalue('hobbit'))
            filing_period = str(dataReceived.getvalue('book'))
            packets_req = str(dataReceived.getvalue('scrolls'))
            if user_chk == '' or len(pass_chk) != 64 or filing_period == '' or packets_req == '':
                print('Failed!')
                raise UserWarning('User Authentication Failed!')
        except:
            print('Failed!')
            raise UserWarning('User Authentication Failed!')
        mCursor.execute(
            "SELECT * FROM masterminds WHERE username='{}' AND password='{}';".format(user_chk, pass_chk))
        resp = list(i for i in mCursor)
        if len(resp) != 1:
            print('Failed!')
            raise UserWarning('User Authentication Failed!')
        else:
            table_work_name = resp[0][2]
            mCursor.execute("SELECT CURRENT_TIMESTAMP();")
            # on the server im working, datetime module was unavailable, and timestamp was required for random authen_key
            mresp = str(list(i[0] for i in mCursor)[0])
            authen_key = generate_hash(user_chk+mresp, 16)
            mCursor.execute(
                "SELECT * FROM current_sessions WHERE work_table='{}';".format(table_work_name))
            resp2 = list(i for i in mCursor)
            if len(resp2) != 0:
                temp2 = str(tuple(list(i[0] for i in resp2)))
                if len(resp2) == 1:
                    # for tuple of len = 1 to convert (a,) to (a)
                    temp2 = temp2.replace("',)", "')")
                mCursor.execute(
                    "DELETE FROM current_sessions WHERE session_id IN {}".format(temp2))
            mCursor.execute("INSERT INTO current_sessions VALUES {}".format(str(
                (authen_key, work_company_gstin, table_work_name, filing_period, packets_req, '0'))))
            connection.commit()
            print(authen_key)
    check_user_cred()

elif str(dataReceived.getvalue('ongoingmagic')) == 'True':
    def receive_packet():
        try:
            authen_key = str(dataReceived.getvalue('secretspell'))
            curr_packet_count = str(dataReceived.getvalue('hobbitage'))
            rawData = str(dataReceived.getvalue('folklores'))
            if len(authen_key) != 16 or curr_packet_count == '' or rawData == '':
                raise ValueError
            # will be decoded when evaluating, else if %27 breaks into % & 27, it doesn't gets evaluated
            decodedData = rawData
        except:
            print('Failed')
            raise UserWarning('Packet Receiving Failed!')

        mCursor.execute(
            "SELECT * FROM current_sessions WHERE session_id='{}';".format(authen_key))
        resp = list(i for i in mCursor)
        # resp[0][5] = packets_rec
        if len(resp) != 1 or int(resp[0][5]) != int(curr_packet_count)-1 or resp[0][4] == resp[0][5]:
            print('Failed!')
            raise UserWarning('Invalid Packet!')

        mCursor.execute(
            "SELECT * FROM spcookies WHERE authen_key='{}'".format(authen_key))
        resp5 = list(i for i in mCursor)
        if len(resp5) != 1:
            mCursor.execute("INSERT INTO spcookies VALUES ('{}','{}')".format(
                authen_key, decodedData))
        else:
            mCursor.execute("UPDATE spcookies SET cookie=CONCAT(cookie,'{}') WHERE authen_key='{}'".format(
                decodedData, authen_key))
        connection.commit()
        print('Received')
        mCursor.execute("UPDATE current_sessions SET packets_rec='{}' WHERE session_id='{}';".format(
            str(curr_packet_count), authen_key))
        connection.commit()
        return ((int(curr_packet_count) == int(resp[0][4])), authen_key)
    respSentPacket, authen_key = receive_packet()
    if respSentPacket:
        mCursor.execute(
            "SELECT * FROM current_sessions WHERE session_id='{}';".format(authen_key))
        resp3 = list(i for i in mCursor)
        work_company_gstin = resp3[0][1]
        work_table = resp3[0][2]
        filing_period = resp3[0][3]
        try:
            mCursor.execute(
                "SELECT * FROM spcookies WHERE authen_key='{}'".format(authen_key))
            temp1 = list(i for i in mCursor)
            temp2 = eval(unquote(temp1[0][1]))
            datatoEnter = list()
            for item in temp2:
                datatoEnter.append((work_company_gstin, filing_period)+item)
            datatoEnter = tuple(datatoEnter)
            if type(datatoEnter) != tuple:
                raise ValueError
        except Exception as ee:
            print('Data Corrputed! Try again!')
            raise UserWarning('Data Corrputed! Try again!')
        mCursor.execute("SELECT * FROM {} WHERE work_company_gstin='{}' AND filing_period = '{}';".format(
            work_table, work_company_gstin, filing_period))
        resp4 = list(i for i in mCursor)
        if len(resp4) != 0:
            mCursor.execute("DELETE FROM {} WHERE work_company_gstin='{}' AND filing_period='{}';".format(
                work_table, work_company_gstin, filing_period))
        mCursor.execute('INSERT INTO {} VALUES {};'.format(
            work_table, str(datatoEnter).replace("',)", "')")[1:-1]))
        mCursor.execute(
            "DELETE FROM spcookies WHERE authen_key='{}'".format(authen_key))
        connection.commit()
        print('Successful!')
elif str(dataReceived.getvalue('Learning')) == 'True':
    def register_user():
        try:
            new_user_name = str(dataReceived.getvalue('mastermindname'))
            new_user_pass = str(dataReceived.getvalue('wizardspell'))
            if new_user_name == '' or len(new_user_pass) != 64:
                raise ValueError
        except:
            print('Failed!')
            raise UserWarning('Incomplete Query!')
        new_user_table = generate_hash(new_user_name+new_user_pass, 64)
        mCursor.execute("INSERT INTO masterminds VALUES('{}','{}','{}');".format(
            new_user_name, new_user_pass, new_user_table))
        resppregist = list(i for i in mCursor)
        if resppregist != []:
            print('Failed')
            raise UserWarning('Unable to register new username')
        connection.commit()
        create_newuser_table(new_user_table, mCursor)
        connection.commit()
        print('Successful!')
    register_user()

elif str(dataReceived.getvalue('getback')) == 'True':
    try:
        username = str(dataReceived.getvalue('mastermindname'))
        password = str(dataReceived.getvalue('wizardspell'))
        companyGSTIN = str(dataReceived.getvalue('hobbit'))
        filingPeriod = str(dataReceived.getvalue('book'))
        packet_count = str(dataReceived.getvalue('scrolls'))
        if username == '' or len(password) != 64 or companyGSTIN == '' or filingPeriod == '' or packet_count != '1':
            print('Failed!')
            raise UserWarning('Wrong Credentials for restore')
    except:
        print('Failed!')
        raise UserWarning('Wrong Credentials for restore')
    else:
        mCursor.execute(
            "SELECT * FROM masterminds WHERE username='{}' AND password='{}';".format(username, password))
        resp = list(i for i in mCursor)
        if len(resp) != 1:
            print('Failed!')
            raise UserWarning('User Authentication Failed!')
        else:
            table_work_name = resp[0][2]
            mCursor.execute("SELECT GSTIN,'',inv_no,inv_date,CAST(ROUND(CAST(inv_taxbl AS UNSIGNED)*(100+CAST(inv_rate AS UNSIGNED))/100,2) AS CHAR),SUBSTRING(GSTIN,1,2),'Regular',inv_rate,inv_taxbl,'0.00'  FROM {} WHERE work_company_gstin='{}' AND filing_period='{}';".format(table_work_name, companyGSTIN, filingPeriod))
            resp22 = list(i for i in mCursor)
            print(str(tuple(resp22)))

connection.close()
