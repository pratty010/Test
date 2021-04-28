#!/usr/bin/env python3

"""
This program acts as the middleware for the Blockstream TestNet Private Cryptocurrency Network. 
One can use the generate_address function to genarate new random private keys and adressesses
This function goes and check the transaction status for a user and create a file to be stored at back server with relevant information
"""

from bit import PrivateKeyTestnet, network 
import requests
from requests_futures import sessions
import jsbeautifier
import json
from prettytable import PrettyTable
from pandas import DataFrame, Series
import numpy as np

# global user_priv_key
# known_priv_key = ['cMhi7YXQQTzaWLxRvcrAHXBhqKp3dn2ufhxJjKYq5bNLw6AWuxWW', 'cSES7oBGk4Cpf6eQrb8pzYWZxcYCSPhABK7uVELPbpfYwvW6rvSf', 'cSGAcDof9n4d7nES3dfmzMb3ipx5TY2HqpPcL6ERB2MAw5PGBNYn']

# global curr_unit

# global Final_file
# Final_file = PrettyTable()
# Final_file.field_names= ["Transaction ID", "Size", "Fees", "Status", "Sender's Add", "Reciever's Add", "Amount Transferred", "Final Balance"]


def get_address(key, form):
    """
    This function returns the addresses of known private keys in certain format
    
        KeyWord Arguments:
            key (PrivateKeyTeatsnet obj): the private address key object
            form (str): format of returned bitcoin address
        
        Return:
            addr (str): Bitcoin wallet address in the particular format

    """

    options = {
        'public' : key.address,
        'segwit' : key.segwit_address,
        'WIF'    : key.to_wif(),
        'hex'    : key.to_hex(),
        'int'    : key.to_int(),
        'bytes'  : key.to_bytes(),
        'PEM'    : key.to_pem()
    }

    addr = options[form]
    return addr


def generate_address(form):
    """
    This function returns the randomly generated private key and addresses in given format
    
        KeyWord Arguments:
            form (str): format of returned bitcoin address

        Return:
            new_key (PrivateKeyTeatsnet obj): randomly generated private address key object
            addr (str): Bitcoin wallet address corresponding to new_key in the particular format
    """
    
    new_key = PrivateKeyTestnet()

    options = {
        'public' : new_key.address,
        'segwit' : new_key.segwit_address,
        'WIF'    : new_key.to_wif(),
        'hex'    : new_key.to_hex(),
        'int'    : new_key.to_int(),
        'bytes'  : new_key.to_bytes(),
        'PEM'    : new_key.to_pem()
    }
    
    addr =  options[form]
    return new_key, addr


def show_balance(key, curr):
    """
    This function returns the balance in a particular wallet in terms of given currency unit
    
        KeyWord Arguments:
            key (PrivateKeyTeatsnet obj): private address key object
            curr (str): The currency unit for measuring wallet balance

         Return:
            bal (str): Wallet balance in required currency unit
    """
 
    bal = key.get_balance(curr)
    return bal


def show_transactions(key):
    """
    This function returns the list of past transactions for a particular wallet
    
        KeyWord Arguments:
            key (PrivateKeyTeatsnet obj): private address key object
        
        Return:
            trans (list): All the past transactions related to a particular Bitcoin address
    """

    trans = key.get_transactions()
    return trans


def show_unspents(key):
    """
    This function returns the list of unspent amounts (one can spend yet) for a particular wallet
    
        KeyWord Arguments:
            key (PrivateKeyTeatsnet obj): private address key object
        
        Return:
            unspent (list): List of all the unspent amounts of a Bitcoin Wallet
    """ 

    unspent = key.get_unspents()
    return unspent


def get_fees():
    """This function returns the transactional fee rate in satoshi/bytes"""
    
    return network.fees.DEFAULT_FEE_FAST, network.fees.DEFAULT_CACHE_TIME


def create_transaction(key, addr, value, curr):
    """
    This function creates a transcation for a given public address and given value and curr unit
    
        KeyWord Arguments:
            key (PrivateKeyTeatsnet obj): the private address key object
            addr (str): Recipient's Bitcoin wallet address 
            value (float): amount of currency units to be sent
            curr (str): The currency unit 

        Return:
            tx (str): The transaction hash for the transaction
    """

    tx = key.create_transaction([(addr, value, curr)])
    return tx


def send_transaction(key, addr, value, curr):
    """
    This function creates and sends a transcation for a given public address and given value and unit
    
        KeyWord Arguments:
            key (PrivateKeyTeatsnet obj): the private address key object
            addr (str): Recipient's Bitcoin wallet address 
            value (float): amount of currency units to be sent
            curr (str): The currency unit 

        Return:
            tx (str): The transaction hash for the sent transaction
    """

    tx = key.send([(addr, value, curr)])
    return tx


def check_transaction(datatype, txid):
    """
    This function checks the transactional details by quering the BlockStream TestNet API
    
        KeyWord Arguments:
            datatype (str): This variable defines data type of txid (str or list)
            txid (str/list) -  This corresponds to the transaction ids to be queried
   
        Return:
            results (np array): The transactional details in certain array format
    """

    if datatype == 'str':
        url = "https://blockstream.info/testnet/api/tx/"
        req = requests.get(url+txid)
        results = np.array(list(json_parser(req)))
        
    elif datatype == 'arr':
        session = sessions.FuturesSession(max_workers=len(txid))
        futures = [session.get(i).result() for i in txid]
        results = np.array(list(map(json_parser, futures)))
    
    return results
    

def query_transactions(key):
    """
    This function first queries show_transactions function to get transactions history for an address. check_transaction function is used to fetch details for each txid

        KeyWord Arguments:
            key (PrivateKeyTeatsnet obj): private address key object
        
        Return:
        out_trans (np array): The transactional details in certain array format
    """

    past_txs = show_transactions(key)
    url = "https://blockstream.info/testnet/api/tx/"
    tx = [(url+txid) for txid in past_txs]

    out_trans = check_transaction("arr", tx)
    return out_trans


def specific_value(table, field, value):
    """
    This function takes in the pandas Dataframe(transactions history) and prints information for matching params
    
        KeyWord Arguments:
            table (Dataframe Obj): The transaction history file to go through
            field (int)- The field whose data is being queried
            value (str) - The value that is being queried
    """

    options = {
        1:  "Transaction_ID",
        2:  "Size", 
        3:  "Fees",
        4:  "Status",
        5:  "Sender_Address",
        6:  "Recipient_Address",
        7:  "Amount_Transferred",
        8:  "Final_Balance"
    }
    
    op = options[field] 
    tab = table.loc[table[op] == value]

    pretty_print(tab)


def convert_df(table):
    """
    This function converts the np ndarray object to Pandas DataFrame
    
        KeyWord Arguments:
            table (np ndarray obj): The transaction history file 

        Return:
            ftab (DataFrame obj): The transaction history
    """

    if table.ndim == 1:
        ftab =  DataFrame(np.array(table, ndmin=2), columns=["Transaction_ID", "Size", "Fees", "Status", "Sender_Address", "Recipient_Address", "Amount_Transferred", "Final_Balance"], index = None)
    
    elif table.ndim == 2:
        ftab = DataFrame(table, columns=["Transaction_ID", "Size", "Fees", "Status", "Sender_Address", "Recipient_Address", "Amount_Transferred", "Final_Balance"], index = None)
        DataFrame()
    return ftab


def to_outfile(table, form):
    """
    This function takes in the pandas Dataframe(transactions history) and create a output file in required format
    
        KeyWord Arguments:
            table (Dataframe obj): The transaction history file
            form (str): The extension format of outfile
    """

    if form == "string":
        f = open("out.txt", "w")
        f.write(table.to_string(index=True, justify="center"))
        
        
    elif form == "excel":
        table.to_excel('out.xlsx', engine='xlsxwriter') 

    else:

        f = open(("out."+form), "w")
        
        if form == "csv":
            f.write(table.to_csv())

        elif form == "dict":
            f.write(table.to_dict("index"))

        elif form == "json":
            res = table.to_json(orient="index")
            parsed = json.loads(res)
            k = json.dumps(parsed, indent=4) 
            f.write(k)

    f.close()


def pretty_print(table):
    """This function prints the required history in Pretty Print on stdout"""

    fil = PrettyTable()
    fil.field_names =  ["Transaction ID", "Size", "Fees", "Status", "Sender's Address", "Recipient's Address", "Amount Transferred", "Final Balance"]
    
    inp = list(table.itertuples())
    list(map(lambda rows:fil.add_row(rows[1:]), inp))

    print(fil)


def json_parser(req):
    """
    This function is a JSON parser for the reply from the API
    Edit this, convert_df and pretty_print funtions for output table params
        
        KeyWord Arguments:
            req (json): the HTTP reply to a txid request to API

        Return:
            out(list): Output paramters for table
    """

    out_js = json.loads(req.text)

    fees = network.satoshi_to_currency(out_js['fee'], 'btc')
    status = out_js['status']['confirmed']
    size = out_js['size']
    txid = out_js['txid']
    rec_addr = out_js['vout'][0]['scriptpubkey_address']
    amt_trans=  network.satoshi_to_currency(out_js['vout'][0]['value'], 'btc')
    sen_addr = out_js['vout'][1]['scriptpubkey_address']
    final_bal =  network.satoshi_to_currency(out_js['vout'][1]['value'], 'btc')

    out = [txid, str(size) + " B", fees, status, sen_addr, rec_addr, amt_trans, final_bal]
    return out


def jscript_beauty(js_str):
    """This function beautifies the output recieved from transaction api"""

    res = jsbeautifier.beautify(js_str)
    return res


def main():

    
    Supported_Currency = {
    'satoshi'   :   'Satoshi',
    'ubtc'      :   'Microbitcoin',
    'mbtc'      :   'Millibitcoin',
    'btc'       :   'Bitcoin',
    'usd'       :   'United States Dollar',
    'eur'       :   'Eurozone Euro',
    'gbp'       :   'Pound Sterling',
    'jpy'       :   'Japanese Yen',
    'cny'       :   'Chinese Yuan',
    'cad'       :   'Canadian Dollar',
    'aud'       :   'Australian Dollar',
    'nzd'       :   'New Zealand Dollar',
    'rub'       :   'Russian Ruble',
    'brl'       :   'Brazilian Real',
    'chf'       :   'Swiss Franc',
    'sek'       :   'Swedish Krona',
    'dkk'       :   'Danish Krone',
    'isk'       :   'Icelandic Krona',
    'pln'       :   'Polish Zloty',
    'hkd'       :   'Hong Kong Dollar',
    'krw'       :   'South Korean Won',
    'sgd'       :   'Singapore Dollar',
    'thb'       :   'Thai Baht',
    'twd'       :   'New Taiwan Dollar',
    'clp'       :   'Chilean Peso'
}


    key_obj2 = PrivateKeyTestnet('cSES7oBGk4Cpf6eQrb8pzYWZxcYCSPhABK7uVELPbpfYwvW6rvSf')
    key_obj1 = PrivateKeyTestnet('cMhi7YXQQTzaWLxRvcrAHXBhqKp3dn2ufhxJjKYq5bNLw6AWuxWW')
    addr1 = get_address(key_obj1, 'public')
    addr2 = get_address(key_obj2, 'public')
    bal1 = show_balance(key_obj1,'btc')
    bal2 = show_balance(key_obj2,'btc')
    print(addr1, bal1)
    print(addr2, bal2)


    # tx = send_transaction(key_obj1, 'min6ee7P8rvcz3exk7KEWKksTaatoYokGL', 0.0001, 'btc' )
   
    # tx_no = "603adc3aa4e0e95dd1c7df515601905506c059f923adedd3c4d5ee82beddc11e"
    
    # tx = check_transaction('str' , tx_no)
    # ftab = query_transactions(key_obj1)

    # ftab1 = convert_df(ftab)
    
    # to_outfile(ftab1, "csv")
    
    
    # specific_value(ftab1, 6, "mqVGkkAhBoBcsktaSRxHQSfNugQVq8oxNv")


    # if(len(sys.argv) != 2):
    #     print("Improper syntax")
    #     print("Please Input as: python3 script.py <private-key>")

if __name__ == "__main__":
    main()
    
    
