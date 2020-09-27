import mysql.connector as mysql
from dotenv import dotenv_values

def initialise(cursored):
    cursored.execute('''CREATE TABLE masterminds (
        username VARCHAR(10) PRIMARY KEY,
        password CHAR(64) NOT NULL,
        datatable VARCHAR(16) NOT NULL);
        ''')

    cursored.execute('''
                    CREATE TABLE current_sessions (
                        session_id CHAR(16) PRIMARY KEY,
                        work_company_gstin CHAR(15) NOT NULL,
                        work_table VARCHAR(16) NOT NULL,
                        filing_period CHAR(7) NOT NULL,
                        packets_req INT(5) NOT NULL,
                        packets_rec INT(5) NOT NULL)
                    ''')

    cursored.execute('''
                    CREATE TABLE {} (
                        authen_key CHAR(16) PRIMARY KEY,
                        cookie TEXT NOT NULL
                    )
                    '''.format('spcookies'))

if __name__ == "__main__":
    ENVV = dotenv_values()
    connection = mysql.connect(
        host = ENVV['HOSTNAME'],
        user = ENVV['USERNAME'],
        passwd = ENVV['PASSWORD'],
        database = ENVV['DATABASE']
        )
    cursored = connection.cursor()
    initialise(cursored)