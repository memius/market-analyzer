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
    if soup2.find("div", {"id" : "head"}) > -1:
        head = soup2.find("div", {"id" : "head"}) 
        if head.h1 > -1:
            for tag in head.h1.findAll('a'):
                tag.extract()
            for tag in head.h1.findAll('em'):
                tag.extract()
        Atitle = head.h1.renderContents()
        Atitle = re.sub('\015', '', Atitle)
    else:
        Atitle = "NONE"
    if Atitle != "NONE":
        Atitle = replace_characters(Atitle)
        Atitle = tag_sentence(Atitle)
        Atitle = sentence_split(Atitle)

#image caption         
def get_AimgText(soup2):
    global Aimg_text
    if soup2.find("div", {"id" : "image"}) > -1:
        img = soup2.find("div", {"id" : "image"})
        for tag in img.findAll("script"):
            tag.extract()
        for tag in img.findAll("div", {"id" : "video"}):
            tag.extract()
        for tag in img.findAll("em"):
            tag.replaceWith(tag.renderContents())
        for tag in img.findAll("img"):
            tag.extract()
        for tag in img.findAll("h5"):
            tag.replaceWith(tag.renderContents())
        Aimg_text = img.renderContents().strip()
    else:
        Aimg_text = "NONE"
    if Aimg_text != "NONE":        
        Aimg_text = replace_characters(Aimg_text)
        Aimg_text = tag_sentence(Aimg_text)
        Aimg_text = sentence_split(Aimg_text)

#lead text  
def get_Aintro(soup2):
    global Aintro
    if soup2.find("div", {"id" : "leadtext"}) > -1:
        leadtext = soup2.find("div", {"id" : "leadtext"})
        for tag in leadtext.findAll("h3"):
            tag.replaceWith(tag.renderContents())
        Aintro = leadtext.renderContents()
    else:
        Aintro = "NONE"
    if Aintro != "NONE":
        Aintro = replace_characters(Aintro)
        Aintro = tag_sentence(Aintro)
        Aintro = sentence_split(Aintro)


#article text and subheadings
def get_Atext(soup2):
    global Atext
    if soup2.find("div", {"id" : "bodytext"}) > -1:
        Atext = soup2.find("div", {"id" : "bodytext"})
        for tag in Atext.findAll("div"):
            tag.extract()
        for tag in Atext.findAll("blockquote"):
            tag.extract()
        for tag in Atext.findAll("iframe"):
            tag.extract()
        for tag in Atext.findAll("img"):
            tag.extract()
        for tag in Atext.findAll("ul"):
            tag.extract()
        for tag in Atext.findAll("script"):
            tag.extract()
        for tag in Atext.findAll('h3'):
            tag.replaceWith(tag.renderContents())
        for tag in Atext.findAll('i'):
            tag.replaceWith(tag.renderContents())
        for tag in Atext.findAll('blockquote'):
            tag.replaceWith(tag.renderContents())
        for tag in Atext.findAll('a'):
            tag.replaceWith(tag.renderContents())
        for tag in Atext.findAll('b'):
            tag.replaceWith(tag.renderContents())
        for tag in Atext.findAll('u'):
            tag.extract()
        for tag in Atext.findAll('h2'):
            tag.replaceWith(" "+tag_sentence(replace_characters(tag.renderContents().strip()))+" ")
        for tag in Atext.findAll('p'):
            tag.replaceWith(" "+tag_sentence(replace_characters(tag.renderContents().strip()))+" ")
        Atext = Atext.renderContents()
    else:
        Atext = "NONE"
    if Atext != "NONE":
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




