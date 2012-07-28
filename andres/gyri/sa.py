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
def get_Adoc_title(soup2):
    global Adoc_title
    if soup2.title > -1:
        Adoc_title = soup2.title.renderContents()
    else:
        Adoc_title = "NONE"
    Adoc_title = replace_characters(Adoc_title)
    if Adoc_title == "":
        Adoc_title = "NONE"
    
#tags keywords topics     
def get_Akeywords(soup2):
    global Akeywords
    if soup2.find("meta", {"name" : "keywords"})['content'] > -1:
        Akeywords = soup2.find("meta", {"name" : "keywords"})['content']
        Akeywords = replace_characters(Akeywords)
    else:
        Akeywords = "NONE"
    
#article header
def get_Atitle(soup2):
    global Atitle
    if soup2.find("div", {"id" : "articleTop"}) > -1:
        top = soup2.find("div", {"id" : "articleTop"})
        if top.h1 > -1:
            for tag in top.h1.findAll('a'):
                tag.replaceWith(tag.renderContents())
            Atitle = top.h1.renderContents()
    elif soup2.h1 > -1:
        for tag in soup2.h1.findAll('a'):
                tag.replaceWith(tag.renderContents())
        Atitle = soup2.h1.renderContents()
    else:
        Atitle = "NONE"
    Atitle = replace_characters(Atitle)
    if Atitle == "":
        Atitle = "NONE"
    if Atitle != "NONE":
        Atitle = tag_sentence(Atitle)
        Atitle = sentence_split(Atitle)

#image caption        
def get_AimgText(soup2):
    global Aimg_text
    if soup2.find("div", {"class" : "description"}) > -1:
        Aimg_text = soup2.find("div", {"class" : "description"})
        Aimg_text.span.replaceWith(Aimg_text.span.renderContents())
        Aimg_text = Aimg_text.renderContents().strip()
        Aimg_text = replace_characters(Aimg_text)
    else:
        Aimg_text = "NONE"
    if Aimg_text == "":
        Aimg_text = "NONE"
    if Aimg_text != "NONE":
        Aimg_text = tag_sentence(Aimg_text)
        Aimg_text = sentence_split(Aimg_text)

#lead text      
#regular articles: <p class="leadText ">  
#football: <div class="leadText ">  
def get_Aintro(soup2):
    global Aintro
    if soup2.find("p", {"class" : "leadText "}) > -1:
        Aintro = soup2.find("p", {"class" : "leadText "})
    elif soup2.find("div", {"class" : "leadText"}) > -1:
        Aintro  = soup2.find("div", {"class" : "leadText"})
    else:
        Aintro = "NONE"
    if Aintro != "NONE":
        if Aintro.find("a"):
            for tag in Aintro.findAll('a'):
                tag.replaceWith(tag.renderContents())
        if Aintro.find('p') > -1:
            for tag in Aintro.findAll('p'):
                tag.replaceWith(tag.renderContents())
        Aintro = Aintro.renderContents().strip()
        Aintro = replace_characters(Aintro)
    if Aintro == "":
        Aintro = "NONE"
    if Aintro != "NONE":
        Aintro = tag_sentence(Aintro)
        Aintro = sentence_split(Aintro)


#article text and subheadings
#<div class="bodyText widget storyContent bodyText" data-widget-id="1717620">
def get_Atext(soup2):
    global Atext
    if soup2.find("div", {"class" : re.compile("bodyText ")}) > -1:
        Atext = soup2.find("div", {"class" : re.compile("bodyText ")})
    elif soup2.find("div", {"id" : "articleBody"}):
        Atext = soup2.find("div", {"id" : "articleBody"})
    else:
        Atext = "NONE"
    if Atext != "NONE":
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
        for tag in Atext.findAll("u"):
            tag.extract()
        for tag in Atext.findAll('i'):
            for atag in tag.findAll('a'):
                atag.replaceWith(atag.renderContents())
            tag.replaceWith(tag.renderContents())
        for tag in Atext.findAll('blockquote'):
            tag.replaceWith(tag.renderContents())
        for tag in Atext.findAll('a'):
            tag.replaceWith(tag.renderContents())
        for tag in Atext.findAll('b'):
            for u in tag.findAll('u'):
                u.replaceWith(u.renderContents())
            tag.replaceWith(tag.renderContents())
        for tag in Atext.findAll('u'):
            tag.extract()
        for tag in Atext.findAll('h2'):
            tag.replaceWith(" "+tag_sentence(replace_characters(tag.renderContents().strip()))+" ")
        for tag in Atext.findAll('h3'):
            tag.replaceWith(" "+tag_sentence(replace_characters(tag.renderContents().strip()))+" ")
        for tag in Atext.findAll('h4'):
            tag.replaceWith(" "+tag_sentence(replace_characters(tag.renderContents().strip()))+" ")
        for tag in Atext.findAll('p'):
            tag.replaceWith(" "+tag_sentence(replace_characters(tag.renderContents().strip()))+" ")
        Atext = Atext.renderContents()
        Atext = replace_characters(Atext)
    if Atext == "":
        Atext = "NONE"
    if Atext != "NONE":
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




