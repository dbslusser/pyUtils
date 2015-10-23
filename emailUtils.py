#! /usr/bin/python

"""
Description:
    Sends an email via smtp; adds domain to address if not present.

Author:
    David Slusser
"""
__revision__ = "0.0.1"

import re
import os
import smtplib
from email.MIMEMultipart import MIMEMultipart  
from email.MIMEBase import MIMEBase  
from email.MIMEText import MIMEText  
from email.Utils import formatdate  
from email import Encoders


def addDomain(address_list):
    """ adds '@myDomain' to email address if no domain is provided """
    for i in address_list:
        if not re.search('\S+@\S+.\S+', i):
            address_list.pop(address_list.index(i))
            address_list.append(i.strip() + '@myDomain.com')
    return address_list


def mail(to, txt=None, html=None, sender=None, 
         cc=None, bcc=None, sub=None, attach=None):
    """
    Description:
        Sends an email to the provided recipients.
    
    Parameters:
        txt    - email message (plain text)
        html   - email message (html formatted)
        sender - email address of sender
        to     - list of emails address(es) to send message to
        cc     - list of emails address(es) to cc message to 
        bcc    - list of emails address(es) to bcc message to
        sub    - email subject
        attach - email attachement

    Returns:
        0 if successful
        1 if failed
    """
    if not sender:
        sender = 'mailAutomation'
    if not sub:
        sub = " lab automated email"

    if type(to).__name__ == "str":
        to = [to]
    to = addDomain(to)
    if cc:
        cc = addDomain(cc)
    if bcc:
        bcc = addDomain(bcc)
    
    try:
        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = ','.join(to)
        message['Date'] = formatdate(localtime=True)
        message['Subject'] = sub
        if cc: 
            message['Cc'] = ','.join(cc)
        if bcc: 
            message['Bcc'] = ','.join(bcc)
        if html:
            message.attach(MIMEText(html, 'html'))
        if txt:
            message.attach(MIMEText(txt, 'plain'))
        
        if attach:
            for f in attach.split(','):
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(open(f, 'rb').read())
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition',
                                'attachment; filename="%s"' \
                                % os.path.basename(f))
                message.attach(part)
        
        sendto = to 
        if cc:
            sendto += cc
        if bcc:
            sendto += bcc
        if cc:
            sendto += cc
        if bcc:
            sendto += bcc
        server = smtplib.SMTP('localhost')
        server.sendmail(sender, sendto, message.as_string())
        server.quit()
        return 0
    except Exception:
        return 1


