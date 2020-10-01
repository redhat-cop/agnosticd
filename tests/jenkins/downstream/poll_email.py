#!/usr/bin/env python
import getpass
import imaplib
import email
import re
import os
import sys
import argparse
from time import sleep

credentials = os.environ['credentials']
username = credentials.split(':')[0]
password = credentials.split(':')[1]

#ArgumentParser
parser = argparse.ArgumentParser()

parser.add_argument('--filter',
                    type=str,
                    dest='filter',
                    help='The string to filter email Subject.')

parser.add_argument('--guid',
                    type=str,
                    dest='guid',
                    help='The guid to filter email Subject.',
                    required=True)

parser.add_argument('--server',
                    type=str,
                    dest='server',
                    help='The imap_server to connect to.',
                    required=False)

parser.add_argument('--timeout',
                    dest='timeout',
                    default=20,
                    type=int,
                    help='Number of minutes to wait for the email to arrive.')
args = parser.parse_args()

guid = args.guid
if args.server is not None:
    imap_server = args.server
else:
    try:
        imap_server = os.environ['IMAP_SERVER']
    except:
        imap_server = os.environ['imap_server']


def connect():
    max_retries = 10
    retries=0
    while retries < max_retries:
        try:
            M = imaplib.IMAP4_SSL(imap_server)
            M.login(username, password)
            return M
        except imaplib.IMAP4.error as err:
            print("IMAP4 error: {0}".format(err))
            print("[%d / %d] retrying to login.. wait %d sec" % (retries, max_retries, 2**retries))
            sleep(2**retries)
            retries += 1

def disconnect(M):
    try:
        M.close()
        M.logout()
    except:
        pass

def wait_email(pattern, time_window):
    M = connect()
    max_retries = time_window * 2
    while max_retries > 0:
        try:
            M.select('INBOX')
            # Add _COMPLETED here because gmail do not follow RFC and matches words, not substrings
            typ, data = M.search(None, '(UNSEEN (OR HEADER Subject "%s" HEADER Subject "%s_COMPLETED"))' % (guid, guid))
            for num in data[0].split():
                typ, data = M.fetch(num, '(RFC822)')
                email_message = email.message_from_string(data[0][1])
                subject = email_message['Subject'].replace("\r\n","")
                sys.stdout.flush()
                if guid in subject:
                    if 'has failed' in subject:
                        # CF failed
                        disconnect(M)
                        print("ERROR failed mail received for guid=%s: %s" % (guid, subject))
                        exit(2)
                    elif 'has updated' in subject:
                        print("OK update mail received for guid=%s: %s" % (guid, subject))
                    elif pattern in subject:
                        # first mail received
                        print("OK mail received for guid=%s: %s" % (guid, subject))

                        return data[0][1]
                else:
                    # failsafe, should not happen
                    # don't mark mail as read
                    M.uid('STORE', num, '-FLAGS', '(\Seen)')

        except imaplib.IMAP4.error as err:
            print("IMAP4 error: {0}".format(err))
            print("reconnecting")
            # reconnect
            disconnect(M)
            M = connect()

        max_retries = max_retries - 1
        sleep(30)

    print("ERROR '%s' email not received" % (pattern))
    exit(2)

print(
    wait_email(
        args.filter,
        args.timeout))
