#!/usr/bin/python
# coding: utf-8

import sys, os 
# import subprocess not allowed in gae

#from subprocess import call

# reload(sys) #these two lines crash something
# sys.setdefaultencoding('utf-8')



#starter crm-programmet classifier.crm med et innkommende eller predefinert streng-argument

#put this into any file that causes a 'UnicodeEncodeError' or similar:
#!/usr/bin/env python
# -*- coding: UTF-8 -*-

def classify(news):
    print 'news in crm.classify:',news,'END news\n'

    #writing to a file not allowed in gae. use db instead, like you do now.
    # # puts the news in a file called 'news.txt', to be read by crm programs. this avoids nested quote problems:
    # textfile = open('/home/tmh/workspace/market_analyzer/news.txt','w') # 'w' overwrites
    # textfile.write(news) 
    # textfile.close

    command = '"""' + 'crm /home/tmh/workspace/market_analyzer/classify.crm ' + news + '"""'
    # print '3: command in logic.classify: ',command, 'END command'
    conclusion = subprocess.check_call(command)
    # print conclusion
    if conclusion == 256:
        conclusion = 'news_buy'
    elif conclusion == 512:
        conclusion = 'news_sell'
    else:
        conclusion = 'news_hold'
    print 'news conclusion: ',conclusion
    return conclusion

#classify("Statoil's shares are legion")

def learn(news,decision):
    textfile = open('/home/tmh/workspace/market_analyzer/news.txt','w')
    textfile.write(news) 
    textfile.close

    command = 'crm /home/tmh/workspace/market_analyzer/learn.crm '
    command += '"'
    command += '/home/tmh/workspace/market_analyzer/news.txt'
    command += '-_-_-'
    command += decision
    command += '"'
    print 'command in learn: ',command, 'END command'
    os.system(command)


#classify("this is some short text about nothing in particular.")
#learn("this is some short text about nothing in particular.",'buy')
