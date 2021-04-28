#!/usr/bin/env python3

import protonmail
from time import sleep

def send_mail(mail_list):
    """
    This function return matching information from DataFrame(transactions history)
    
        @param: mail_list - list - The field whose data is being queried
    """

    try:
        # Creating the Proton Mail client and login attempt
        client = protonmail.core.ProtonmailClient()
        client.login('polyroad@protonmail.com', '07XTf1s4mU07XTf1s4mU')  # Hardoded credentials

        # Mailing list with email-->item
        mail_agent(client, mail_list)

        # Destroying the created mail client
        client.destroy()

    except Exception as e:
        print(e)

        # In case of login failure (external try block)
        send_mail(mail_list)

def mail_agent(client, mail_list):
    """
    This function sends requested item to the particular mail address
    
        @param: client - ProtonMail Object - The object with session information
        @param: mail_list - list - The field whose data is being queried
        @param: value - str - The value that is being queried
    """
    
    # loop throught the mail list
    while mail_list:
        try:
            # poping first element to mail to
            mail = mail_list.pop(0)
            # sending mail to the poped mail
            client.send_mail(["polyroad@protonmail.com", mail[0]], "Requested Item", "PFA") #, attachments = [mail[1]])
            # buffer for sending process
            sleep(7)
        except Exception as e:
            print('Mail Error for ' + mail[0])
            print(e)
            # In case of send mail error, restart from the particular
            mail_list.insert(0, mail)

