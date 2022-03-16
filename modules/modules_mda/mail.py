#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function
import oyaml as yaml
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os.path as op


class GMAIL(object):
    '''
    Class for sending mails with Gmail with smtp protocol.
    input:
        gmail_user : name of the Gmail account
        gmail_pwd  : password of the Gmail account
        to: destination of the mail (can be a list)
        subject: subject of the mail
        text: text to be sent
        attach: Attached document (can be a list)
    Usage:
        gm = GMAIL()
        gm.send(to = 'dupont@gmail.com', subject = 'dupond & dupont',
                        text = "hello", attach = 'images/chat.png')
    '''
    def __init__(self):
        with open('modules/settings/mail.yaml') as f_r:
            dic_mail = yaml.load(f_r, Loader=yaml.FullLoader)
        self.gmail_user = dic_mail['user']
        self.gmail_pwd = dic_mail['pwd']

    def make_attach(self, msg, one_attach):
        '''
        '''
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(one_attach, 'rb').read())
        encoders.encode_base64(part)
        name_attach = op.basename(one_attach)
        part.add_header('Content-Disposition',
                        f'attachment; filename = {name_attach}')
        msg.attach(part)

    def send(self, to, subject, text="", attach=None):
        '''
        '''
        if type(to) == list:
            for dest in to:
                print(f'sending a mail to {dest}')
                self.send_mail(dest, subject, text=text, attach=attach)
        else:
            self.send_mail(to, subject, text=text, attach=attach)

    def send_mail(self, to, subject, text="", attach=None):
        self.to = to
        self.subject = subject
        self.text = text
        self.attach = attach
        msg = MIMEMultipart()
        #################
        msg['From'] = self.gmail_user
        msg['To'] = self.to
        msg['Subject'] = self.subject
        #############
        if text != '':
            msg.attach(MIMEText(self.text))
        ###############
        if attach is not None:
            if type(attach) == list:
                print('list !!!')
                for att in attach:
                    self.make_attach(msg, att.strip())
            else:
                self.make_attach(msg, attach)
        ##############
        mailServer = smtplib.SMTP("smtp.gmail.com", 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(self.gmail_user, self.gmail_pwd)
        mailServer.sendmail(self.gmail_user, self.to, msg.as_string())
        mailServer.close()
