#!/usr/bin/python

"""
Cron Husk Wrapper

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

human=False

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
            'Subject' : 'Cron Husk Wrapper Email With Default Subject', 
            }

    # merge kwargs and defaults
    options.update(kwargs)

    # Reform Body of message with all proper headers
    fullBody="From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s" % (options['FROM_ADDRESS'],
                                                              ", ".join(options['TO_ADDRESS']), 
                                                              options['Subject'],
                                                              options['Body'],)

    if human:
        print 'EMAIL DEBUG', options

    # Send email out localhost
    server = smtplib.SMTP('localhost')
    server.sendmail(options['FROM_ADDRESS'], 
                    options['TO_ADDRESS'], 
                    fullBody)
    server.quit()



# Helper callback to convert TO be a list
def toList_callback(option, opt, value, parser):
  setattr(parser.values, option.dest, value.split(','))


def main():
    # Check to see if we're running from commandline
    global human
    if sys.stdout.isatty(): human=True


    # TODO 
    # -- write optparsers
    # -- code logic
    # if warn or error in output -- email

    parser = optparse.OptionParser(usage="usage: %prog [options] \"command\"",
                          version="%prog 1.0")
    parser.add_option("-f", "--from",
                      action="store",
                      dest="FROM_ADDRESS",
                      default="Cron Husk Wrapper <husk@example.com>",
                      help="set email From address")
    parser.add_option("-t", "--to",
                      type='string',
                      action="callback",
                      callback=toList_callback,
                      dest="TO_ADDRESS",
                      default="husk@example.com,husk1@example.com",
                      help="command seperated list of email destinations")


    (options, args) = parser.parse_args()



    if len(args) != 1:
        parser.error("Command not specified")

    # TESTING
    output=runCommand(args[0])

    if human: 
        print 'DEBUG OPTIONS', options
        print 'DEBUG OUTPUT:', output


    # Check for Conditions warranting email
    if output['exitcode'] != 0:
        # Must convert options to a dictionary
        doptions=options.__dict__

        # Craft an email body
        doptions['Body']="""ERROR:\n%s""" % (
            output['stderror'])
        doptions['Body']="""ERROR:\n%s""" % (
            output['stderror'])


        sendEmail(**doptions )
        


# Boilerplate to allow for external import
if __name__ == "__main__":
    main()
