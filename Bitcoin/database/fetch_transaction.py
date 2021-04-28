#!/usr/bin/env python3


import mysql.connector as sql
import pandas as pd

def get_transactions():
    """This function fetches all the transactional SQL data stored in the MiddleApp Sever Database"""

    # Hardcoded Database Connection Variables. Change these accordingly.
    hostname = "pr-customerdb-mysql.mysql.database.azure.com"
    username = "userisme@pr-customerdb-mysql"
    password = "07XTf1s4mU07XTf1s4mU"
    db_name = "transactions"
    table_name = "transactions"

    # Establishing connection to the Middle App database
    db_connection = sql.connect(host= hostname, database= db_name, user= username, password= password)
    db_cursor = db_connection.cursor()

    
    
    try:
        # Reading all the data present in the database
        db_cursor.execute("SELECT * FROM "+ table_name)
        table_rows = db_cursor.fetchall()

        # Converting SQL to Pandas datframe for easier accessibility and exporting it to CSV file
        df = pd.DataFrame(table_rows, 
        columns= ["ID", "Transaction_ID",  "Email", "Item"])

        # Clearing up the databse for newer transactions
        db_cursor.execute("DELETE FROM transactions")
        db_connection.commit()
        db_connection.close()

    except:
        # Creating empty dataframe alternatively
        df = pd.DataFrame(columns= ["ID", "Transaction_ID",  "Email", "Item"])

    df = df.drop(columns=["ID"])
    
    out_file(df)
    return df
    
def out_file(table):
    """
    This function takes in the pandas Dataframe(transactions history) and create a output file for Bitcoin script to query
    
        @param: table - Dataframe Object - The object for Item requests
    """

    f = open(r"./new_transactions.csv", "w")
    f.write(table.to_csv())
    f.close()



