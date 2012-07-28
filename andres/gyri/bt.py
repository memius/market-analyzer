#!/usr/bin/python
# coding: utf-8

#python modules
import sys
import os
import string
import BeautifulSoup
import re
import urllib
reload(sys)
sys.setdefaultencoding('utf-8')

#import nltk
#sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

#self-defined functions (defined in separate files)
from remove_path import remove_path
from replace_characters import replace_characters
from tag_sentence import tag_sentence


def sentence_split(e):
    #split tagged string into list of "<s>...</s>" elements
    e = e.split("</s>")
    #delete empty elements ("<s></s>") from the  list
    for i in xrange(len(e)):
        try:
            e[i] = e[i].strip()
            if e[i] == '':
                del e[i]
        except IndexError:
            pass
    #put back deleted end-tags 
    for i in xrange(len(e)):
        e[i] = e[i]+"</s>"
    return e

#-------------------
#GLOBAL PLACEHOLDERS
#-------------------

##open and read input file
soup = ""
from BeautifulSoup import BeautifulSoup
url = sys.argv[1] 
article = urllib.urlopen(url).read()
#vgarticle = vgarticle.decode('utf8')
try:
    soup = BeautifulSoup(article)
except TypeError:
        print "INPUT ERROR"    

##url
id = ""  #uniqe identifier inside url

url_elements = ""  #tags in url 

##article text
Adoc_title = ""
Akeywords = ""
Atitle = ""
AimgText = ""
Aintro = ""
Atext = ""
        
#document title
def get_Atitle(soup2):
    global Atitle
    Atitle = ""
    if soup2.find("h1", {"class" : "articleTitle "}) > -1:
        Atitle = soup2.h1
        for tag in Atitle.findAll("cite"):
            tag.replaceWith("<X>"+tag.renderContents()+"</X>")
        for tag in Atitle.findAll("blockquote"):
            tag.replaceWith(tag.renderContents())
        Atitle = Atitle.renderContents()
    elif soup2.find("div", {"id" : "articleTop"}) > -1:
        Atitle = soup2.find("div", {"id" : "articleTop"})
        for tag in Atitle.findAll("div", {"class" : "mediaContainer"}):
            tag.extract()
        for tag in Atitle.findAll("h2"):
            tag.replaceWith(tag.renderContents())
        for tag in Atitle.findAll("h1"):
            tag.replaceWith(tag.renderContents())
        Atitle = Atitle.renderContents()
    if Atitle != "":
        Atitle = replace_characters(Atitle)
    else:
        Atitle = "NONE"
    if Atitle != "NONE":
        Atitle = replace_characters(Atitle)
        if Atitle.find("<s>") != 1:
            Atitle = tag_sentence(Atitle)
        Atitle = sentence_split(Atitle)

#image caption         
def get_AimgText(soup2):
    global Aimg_text
    Aimg_text = ""
    if soup2.find("div", {"class" : "caption-inner"}) > -1: 
        Aimg_text = soup2.find("div", {"class" : "caption-inner"})
        for tag in Aimg_text.findAll("p", {"class" : "credits"}):
            for xtag in tag.findAll():
                xtag = xtag.replaceWith(xtag.renderContents())

##             if tag.renderContents().find("FOTO") > -1:
##                 tag.extract()
##             elif Aimg_text.find("h2") > -1:
##                 for tag in Aimg_text.findAll("h2"):
##                     tag = tag.replaceWith(tag.renderContents())
##             else:
##                tag = tag.replaceWith(tag.renderContents())
               
            tag = tag.replaceWith(tag.renderContents())
        Aimg_text = Aimg_text.renderContents()
    else:
        Aimg_text = "NONE"
    if Aimg_text != "NONE":
        Aimg_text = Aimg_text.replace("<h2></h2>", "")
        Aimg_text = Aimg_text.replace("<h2>", "<s>")
        Aimg_text = Aimg_text.replace("</h2>", "</s>")
        Aimg_text = replace_characters(Aimg_text)
        Aimg_text = tag_sentence(Aimg_text)
        Aimg_text = sentence_split(Aimg_text)

#lead text       
def get_Aintro(soup2):
    global Aintro
    Aintro = ""
    if soup2.find("p", {"class" : "leadText "}) > -1:
        Aintro = soup2.find("p", {"class" : "leadText "})
##     #fotballstoff    
##     elif soup2.find("div", {"class" : "leadText"}) > -1: #e24.no
##         Aintro  = soup2.find("div", {"class" : "leadText"})
    if Aintro != "": 
##         for tag in Aintro("preform"):
##             tag.extract()
        for tag in Aintro("p"):
            tag.replaceWith(tag.renderContents())
        Aintro = Aintro.renderContents()
    else:
        Aintro = "NONE"
    if Aintro != "NONE":
        Aintro = replace_characters(Aintro)
        Aintro = tag_sentence(Aintro)
        Aintro = sentence_split(Aintro)


#article text and subheadings
def get_Atext(soup2):
    global Atext
    Atext = ""
    if soup2.find("div", {"class" : "bodyText"}) > -1:
        Atext = soup2.find("div", {"class" : "bodyText"})
    elif soup2.find("div", {"class" : "articleBody"}) > -1:
        Atext = soup2.find("div", {"class" : "articleBody"})
    elif soup2.find("div", {"id" : "articleBody"}) > -1:
        Atext = soup2.find("div", {"id" : "articleBody"})
    elif soup2.find("div", {"class" : "bodyText widget storyContent bodyText"}) > -1:
        Atext = soup2.find("div", {"class" : "bodyText widget storyContent bodyText"})
    else:
        Atext = "NONE"
    if Atext != "NONE":
        for tag in Atext.findAll("img"):
            tag.extract()
        for tag in Atext.findAll("script"):
            tag.extract()
        for tag in Atext.findAll("hr"):
            tag.extract()
        for tag in Atext.findAll("blockquote"):
            tag.extract()
        for tag in Atext.findAll("img"):
            tag.extract()
        for tag in Atext.findAll("ul"):
            tag.extract()
        for tag in Atext.findAll('h3'):
            tag.replaceWith(tag.renderContents())
        for tag in Atext.findAll('h2'):
            tag.replaceWith("<s>"+tag.renderContents().strip()+"</s>")
        for tag in Atext.findAll('span'):
            tag.replaceWith(tag.renderContents())
        ## for tag in Atext.findAll('i'):
##             for atag in tag.findAll('a'):
##                 atag.extract()
##             tag.replaceWith(tag_sentence(tag.renderContents()))
        for tag in Atext.findAll('i'):
            tag.extract()
        for tag in Atext.findAll('blockquote'):
            tag.replaceWith(tag.renderContents())
        for tag in Atext.findAll('a'):
            tag.replaceWith(tag.renderContents())
        for tag in Atext.findAll('b'):
            tag.replaceWith(tag.renderContents())
        for tag in Atext.findAll('em'):
            tag.replaceWith(tag.renderContents())
        for tag in Atext.findAll('strong'):
            tag.replaceWith(tag.renderContents())
        for tag in Atext.findAll('h4'):
            tag.replaceWith(tag.renderContents()) #!
        for tag in Atext.findAll('u'):
            tag.extract()
        for tag in Atext.findAll("div"):
            tag.extract()
        if not Atext.find("p"): #artikler uten p-elementer
            Atext = Atext.renderContents()
            Atext = Atext.replace("<s>", "TAG1")
            Atext = Atext.replace("</s>", "TAG2")
            Atext = tag_sentence(Atext)
            Atext = Atext.replace("<s>TAG1", "<s>")
            Atext = Atext.replace("TAG2", "</s>\n<s>")
            Atext = Atext.replace(" TAG1", "</s>\n<s>")
        else:
            for tag in Atext.findAll('p'):
                tag.replaceWith(" "+tag_sentence(replace_characters(tag.renderContents().strip()))+" ")
            Atext = Atext.renderContents()
    if Atext != "":
        Atext = replace_characters(Atext)
        Atext = sentence_split(Atext)

def assign_variables(soup):
    get_Atitle(soup)
    get_AimgText(soup)
    get_Aintro(soup)
    get_Atext(soup)

def print_text():
    print Atitle
    print AimgText
    print Aintro
    print Atext

assign_variables(soup)
print_text()




