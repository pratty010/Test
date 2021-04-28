#!/usr/bin/env python3

"""
This program acts as the middleware for the Blockstream TestNet Private Cryptocurrency Network. 
One can use the generate_address function to genarate new random private keys and addresses
This function goes and check the transaction status for a user and create a file to be stored at back server with relevant information
"""

import requests
from requests_futures import sessions
import json
import pandas as pd
from pandas import DataFrame, Series
import numpy as np
from tabulate import tabulate
import os
from mail.proton_mail import mail_agent, send_mail
from database.fetch_transaction import get_transactions


def check_transaction(txid):
    """
    This function checks the transactional details by quering the BlockStream TestNet API
    
        @param: txid - list - This corresponds to the transaction ids to be queried
        @param: results - np array - The transactional details in certain array format
    """

    # Using the Future Session lib for doing parallel requests (HTTP - secured)
    session = sessions.FuturesSession(max_workers=len(txid))
    futures = [session.get(i).result() for i in txid]

    # using map() fn for fetching the required information about txids
    results = np.array(list(map(json_parser, futures)))
    
    return results


def query_transactions(new_transac):
    """
    This function queries check_transaction() function to fetch details for each new txids
        
        @param: new_transac - list - consist of all the transactions that have to queried to the API
        @param: data - dataframe obj -  The transactional details as Pandas dataframe
    """

    url = "https://blockstream.info/testnet/api/tx/"
    txids = [(url+txid) for txid in new_transac]

    out_trans = check_transaction(txids)

    # from np array to dataframe
    data = convert_df(out_trans)

    return data


def convert_df(table):
    """
    This function converts the np ndarray object to Pandas DataFrame
     
        @param: table - np array- The transaction history file 
        @param: ftab - dataframe obj -  The transaction history 
    """
    if table.ndim == 1:
        ftab =  DataFrame(np.array(table, ndmin=2),
        columns = ["Transaction_ID", "Fees", "Status", "Sender_Address", "Recipient_Address", "Amount_Transferred", "Final_Balance"])
    
    elif table.ndim == 2:
        ftab = DataFrame(table, 
        columns=["Transaction_ID", "Fees", "Status", "Sender_Address", "Recipient_Address", "Amount_Transferred", "Final_Balance"])
       
    return ftab


def specific_value(table, field, value):
    """
    This function takes in the pandas Dataframe(transactions history) and prints information for matching params
    
        @param: table - dataframe obj -  The transaction history 
        @param: field - str - The field whose data is being queried
        @param: value - str - The value that is being queried
    """

    tab = table.loc[table[field] == value]

    return tab

            
def to_outfile(table, file):
    """
    This function takes in the pandas Dataframe(transactions history) and create a output file in required format
    
        @param: table - dataframe obj -  The transaction history 
        @param: file - str -  Output Path location
    """

    if file.endswith('.txt'):
        f = open(file, "w")
        k = pretty_print(table)
        f.write(k)
        f.close()
        
    elif file.endswith('.csv'):
        table.to_csv(file, index = False)


def from_outfile(file):
    """
    This function takes a CSV file and convert the data in Pandas Datframe
    
        @param: table - dataframe obj -  The transaction history 
        @param: file - str -  Output Path location
    """

    if file.endswith('.csv'):
        if file == "./database/new_transactions.csv":
        # if file == "./files/pending.csv":
            rcrds = pd.read_csv(file)
        
        try:
            if (file == "./files/out.csv" or file == "./files/pending.csv"):
                rcrds = pd.read_csv(file)
        except:
            rcrds = DataFrame(columns = ['Transaction_ID', 'Fees', 'Status', "Sender_Address", "Recipient_Address", "Amount_Transferred", "Final_Balance"])
            to_outfile(rcrds, file)

    return rcrds


def get_maillist(table):
    """
    This function performs three function:
        1. Checks for pending transactions in start and stores the same in a CSV file at the end
        2. Checks for transactional Bitcoin exchange for reequesd item
        3. Create maillist and table for succesful transactions.

        @param: table - dataframe obj -  The transaction history 
        @param: mail_list - list - returns the lsit of (e-mail address, item)
        @param: success_trans - dataframe obj - table for successful transactions

    """
    # the different prices for products in Bitcoin
    items = [0.001, 0.003, 0.004, 0.0015]
    mail = []

    # Loading pending transactions and appending to current table for check
    pending_old = from_outfile("./files/pending.csv")

    if not pending_old.empty:
        table = table.append(pending_old, ignore_index = True)
        pending_old.drop(pending_old.index, inplace = True)

    # getting the txids to query and fetch inforamtion
    new_txid = table["Transaction_ID"].tolist()
    trans_query = query_transactions(new_txid)

    # Seperating the transactions according to status
    success_trans = specific_value(trans_query, 'Status', 'True')
    pending_trans = specific_value(trans_query, 'Status', 'False')
    
    # The price match condition (paid amt >= item price) and creating the table and mailist accordingly
    for i, j in success_trans.iterrows():
        amt_paid = float(j['Amount_Transferred'])
        item_price = items[table[table.Transaction_ID == j['Transaction_ID']].Item.item()]

        if amt_paid >= item_price:
            email = table[table.Transaction_ID == j['Transaction_ID']].Email.item()
            item_n = table[table.Transaction_ID == j['Transaction_ID']].Item.item()
            mail.append([email, item_n])
            success_trans._set_value(i, 'Status', 'Complete')
        else:
            # If the price is not paid, no mail is sent and status is changed
            success_trans._set_value(i, 'Status', 'Incomplete')

    # To update file for pending transactions
    if not pending_trans.empty:
        fl = pending_trans["Transaction_ID"].tolist()
        pending_transc_series = table.Transaction_ID.isin(fl)
        pending_old = table[pending_transc_series]
             
    to_outfile(pending_old, "./files/pending.csv")
    
    return mail, success_trans


def pretty_print(table):
    """This function prints the required history in Pretty Print on stdout using tabulate lib"""

    headers = ["Transaction ID", "Fees", "Status", "Sender's Address", "Recipient's Address", "Amt Transferred", "Final Balance"]
    out_table = tabulate(table, headers= headers, showindex= False, tablefmt= 'pretty', numalign= 'center', stralign= 'center')
    
    return out_table


def json_parser(req):
    """
    This function is a JSON parser for the reply from the API.

        @param: req - JSON onj - the HTTP reply to a txid request to API
        @param: out - list - Output paramters for table
    """  

    out_js = json.loads(req.text)

    txid = out_js['txid']
    fees = (out_js['fee'] * 0.00000001)
    status = out_js['status']['confirmed']
    rec_addr = out_js['vout'][0]['scriptpubkey_address']
    sen_addr = out_js['vout'][1]['scriptpubkey_address']
    amt_trans=  (out_js['vout'][0]['value'] * 0.00000001)
    final_bal = (out_js['vout'][1]['value'] * 0.00000001)
    
    out = [txid, fees, status, sen_addr, rec_addr, amt_trans, final_bal]
    return out


def conv_dtype(table):
    """
    This function assigns proper datatype to the cells of the Dataframe

        @param: table - dataframe obj -  The transaction history 
    """

    # To keep track of the table size
    cols = len(table.columns)

    convert_dict = {'Item': int }
    convert_dict_1 = {
        'Fees': float,
        'Status': object,
        'Amount_Transferred': float,
        'Final_Balance': float
    }

    # Different datatypes assignment according to table in question
    if cols >= 4:
        formats = {'Final_Balance': '{0:.8f}', 'Fees': '{0:.8f}', 'Amount_Transferred': '{0:.5f}'}
        table = table.astype(convert_dict_1)
    else:
        table = table.astype(convert_dict)

    # assigning formatting
    for col, f in formats.items():
            table[col] = table[col].map(lambda x: f.format(x))

    return table


def main():

    # files variable declaration
    # transac_file = "./database/new_transactions.csv"
    output_csv_file = "./files/out.csv"
    output_txt_file = "./files/out.txt"

    new_transac_data = get_transactions()
    # new_transac_data = from_outfile(transac_file)
    out_dataframe = from_outfile(output_csv_file)

    # Exit if no new trasactions
    if new_transac_data.empty:
        exit()

    out_dataframe = conv_dtype(out_dataframe)

    # fetching maillist for the current session and table for successful transactions
    mail_list, out_trans = get_maillist(new_transac_data)
    out_trans = conv_dtype(out_trans)

    # update to original table
    out_dataframe = out_dataframe.append(out_trans, ignore_index = True)

    # Storing new updated table
    to_outfile(out_dataframe, output_csv_file)
    to_outfile(out_dataframe, output_txt_file )

    # If valid emails to send mail to
    item_dict = {
        0 : "./"
    }
    if len(mail_list) > 0:
        send_mail(mail_list)


if __name__ == "__main__":
    main()