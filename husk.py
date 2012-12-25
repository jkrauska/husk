#!/usr/bin/python

"""
Simple wrapper for cron scripts to make cron emails more user friendly.

Problem to solve:
- Random cron emails that aren't mail-reader friendly
     eg.
     From: root@host.foo.net (Cron Daemon)
     To: sysadmin@foo.net
     Subject: Cron <root@host> /root/bin/randomscript.py
- Rewriting mail sending code in every minor utility program I write

Features:
- Email output from script when certain conditions are met
- customizeable FROM email headers
- customizeable TO email headers
- customizeable SUBJECTS

"""

import sys # for detecting if you're in cron or not
import optparse # argparse is preferred for 2.7 on, but optparse is used for backward compatability
import subprocess # running commands
import shlex  # supposedly good for escaping command lines
import smtplib # for sending email -- just using localhost, but could use a valid SMTP relay


# subprocess wrapper 
# FIXME: Haven't ever found an elegant way to merge STDIN and STDOUT while also keeping isolated copies
def runCommand(cmd):
    try:
        p=subprocess.Popen(shlex.split(cmd), 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
        STDout, STDerr=p.communicate()
        exitcode=p.returncode
    except Exception as e: 
        # Catach command not found or other parsing problems
        STDout='HUSK ERROR: Could not run command: ' + cmd + "\n" + str(e)
        STDerr=STDout
        exitcode=2
        
    return({'stdout' : STDout, 
            'stderror' : STDerr,
            'exitcode' : exitcode,})

# Email sending
def sendEmail( **kwargs ):
    # Set defaults
    options = {
            'From'    : 'Husk Cron Wrapper <husk@example.com>',
            'To'      : ['jkrauska@gmail.com'],
            'Subject' : 'Husk Cron Wrapper Email With Unconfigured Subject', 
            'Body'    : 'Sample email from Husk Cron Wrapper.',
            }

    # merge kwargs and defaults
    options.update(kwargs)

    # Reform Body of message with all proper headers
    fullBody="From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s" % (options['From'],
                                                              ", ".join(options['To']), 
                                                              options['Subject'],
                                                              options['Body'],)

    print 'SendEmail DEBUG', options

    # Send email out localhost
    server = smtplib.SMTP('localhost')
    server.sendmail(options['From'], options['To'], fullBody)
    server.quit()




def main():
    # Check to see if we're running from commandline
    if sys.stdout.isatty(): human=True


    # TODO 
    # -- write optparsers
    # -- code logic
    # if exitcode != 1 -- email
    # if warn or error in output -- email

    # TESTING
    print '-'*80
    print runCommand('ls')
    print '-'*80
    print runCommand('ls /too')

    print '-'*80
    print runCommand('laasds /too')


# Boilerplate to allow for external import
if __name__ == "__main__":
    main()
