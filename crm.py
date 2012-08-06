#!/usr/bin/python
# coding: utf-8

import sys, os

# reload(sys) #these two lines crash something
# sys.setdefaultencoding('utf-8')



#starter crm-programmet classifier.crm med et innkommende eller predefinert streng-argument

#put this into any file that causes a 'UnicodeEncodeError' or similar:
#!/usr/bin/env python
# -*- coding: UTF-8 -*-

def classify(news):
    print 'news in crm.classify:',news,'END news\n'
    # puts the news in a file called 'news.txt', to be read by crm programs. this avoids nested quote problems:
    textfile = os.open('/home/tmh/workspace/market_analyzer/news.txt',777)
    os.write(textfile,news) # completely overwrites previous text in the file
    os.close(textfile)

    # textfile-in function open() is apparently better:
    # text = open('/home/tmh/documents/projects/trading/teab/stocks/news.txt',w)
    # who knows what should happen here.
    
    command = 'crm /home/tmh/workspace/market_analyzer/classify.crm /home/tmh/workspace/market_analyzer/news.txt'
    # print '3: command in logic.classify: ',command, 'END command'
    conclusion = os.system(command)
    # print conclusion
    if conclusion == 256:
        conclusion = 'news_buy'
    elif conclusion == 512:
        conclusion = 'news_sell'
    else:
        conclusion = 'news_hold'
    print 'news conclusion: ',conclusion
    return conclusion

# classify("Statoil's shares are legion")

def learn(news,decision):
    textfile = os.open('/home/tmh/workspace/market_analyzer/news.txt',777)
    os.write(textfile,news) # completely overwrites previous text in the file
    os.close(textfile)

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
