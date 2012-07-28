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
        Adoc_title = replace_characters(Adoc_title)
        Adoc_title = Adoc_title.replace("fvn.no > ", "")
    else:
        Adoc_title = "NONE"
    
#tags keywords topics    
def get_Akeywords(soup2):
    global Akeywords
    if soup2.find("meta", {"name" : "keywords"})['content'] > -1:
        Akeywords = soup2.find("meta", {"name" : "keywords"})['content']
        Akeywords = replace_characters(Akeywords)
        print Akeywords
    else:
        Akeywords = "NONE"

#article header
def get_Atitle(soup2):
    global Atitle
    if soup2.find("div", {"id" : "articleTop"}) > -1: #fotball.fvn.no
         top = soup2.find("div", {"id" : "articleTop"})
         Atitle = top.h1.renderContents()
    elif soup2.h1 > -1:
        top = soup2.h1
        for tag in soup2.h1.findAll('span'):
                tag.replaceWith(tag.renderContents())
        Atitle = soup2.h1.renderContents()
    else:
        Atitle = "NONE"
    if Atitle != "NONE":
        Atitle = replace_characters(Atitle)
        Atitle = tag_sentence(Atitle)
        Atitle = sentence_split(Atitle)

#image caption         
def get_AimgText(soup2):
    global Aimg_text
    Aimg_text = ""
    p = ""
    [p for p in soup2.findAll("div", {"class" : "imageCaption"})]
    if p != "":
        for tag in p.findAll("p", {"class" : "credit"}):
            tag.replaceWith(tag.renderContents())
        for tag in p.findAll("span", {"class" : "credit"}):
            tag.replaceWith(tag.renderContents())
        for tag in p.findAll("div", {"class" : "iCaption"}):
            tag.replaceWith(tag.renderContents())
        Aimg_text = p.renderContents()
        Aimg_text = Aimg_text.replace("\n", "")
        Aimg_text = re.sub('\015', '', Aimg_text) #remove newline character "^M"
    else:
        Aimg_text = "NONE"
    if Aimg_text != "NONE":
        Aimg_text = replace_characters(Aimg_text)
        Aimg_text = tag_sentence(Aimg_text)
        Aimg_text = sentence_split(Aimg_text)
    
        
#lead text  
def get_Aintro(soup2):
    global Aintro
    Aintro = ""
    p = ""
    [p for p in soup2.findAll("div", {"class" : "lead"})]
    if p != "":
        for tag in p.findAll("iframe"):
            tag.replaceWith(tag.renderContents())
        for tag in p.findAll('a'):
            tag.replaceWith(tag.renderContents())
        Aintro = p.renderContents()
        Aintro = re.sub('\015', '', Aintro) #remove newline character "^M"
    elif soup2.find("div", {"class" : "leadText"}) > -1:
        lT = soup2.find("div", {"class" : "leadText"})
        for p in lT.findAll("p"):
            for tag in p.findAll('a'):
                tag.replaceWith(tag.renderContents())
            p = p.renderContents()
            Aintro = Aintro + p
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
    if soup2.find("p", {"class" : "body"}) > -1:
        for p in soup2.findAll("p", {"class" : "body"}):
            for tag in p.findAll():
                if tag.renderContents().startswith("<!--"):
                    print "HEST"
                    tag.extract()
            for tag in p.findAll('b'):
                tag.replaceWith("<X>"+tag.renderContents()+"</X>")
            for tag in p.findAll('u'):
                tag.replaceWith(tag.renderContents())
            for tag in p.findAll('div', {'class' : 'imageCaption'}):
                tag.extract()
            for tag in p.findAll('img'):
                tag.replaceWith(tag.renderContents())
            for tag in p.findAll('div', {'class' : 'image'}):
                tag.replaceWith(tag.renderContents())
            for tag in p.findAll('div', {'class' : 'left'}):
                tag.replaceWith(tag.renderContents())
            for tag in p.findAll('div', {'class' : ''}):
                tag.replaceWith(tag.renderContents())
            for tag in p.findAll('br'):
                tag.extract()
            for tag in p.findAll('a'):
                #tag.replaceWith(tag.renderContents())
                tag.extract()
            for tag in p.findAll('font'):
                tag.replaceWith(tag.renderContents())
            for tag in p.findAll('object'):
                tag.extract()
            for tag in p.findAll('i'):
                tag.replaceWith(tag.renderContents())
            for tag in p.findAll('ul'):
                tag.extract()
            for tag in p.findAll('embed'):
                tag.extract()
            for tag in p.findAll('iframe'):
                tag.extract()
            p = p.renderContents()
            Atext = Atext + p
    elif soup2.find("div", {"id" : "articleBody"}) > -1: #fotball.fvn.no
        body =  soup2.find("div", {"id" : "articleBody"})
        if body.find("div", {"class" : "leadText"})    > -1:
            body.find("div", {"class" : "leadText"}).extract()
        if body.find("div", {"id" : "byline"}) > -1:
            body.find("div", {"id" : "byline"}).extract()
        for p in body.findAll("p"):
            for tag in p.findAll('b'):
                for atag in tag.findAll("a"):
                    atag.replaceWith(atag.renderContents())
                tag.replaceWith(tag.renderContents())
            for tag in p.findAll('a'):
                tag.extract()
            for tag in p.findAll('div', {'class' : 'imageCaption'}):
                tag.extract()
            for tag in p.findAll('img'):
                tag.replaceWith(tag.renderContents())
            for tag in p.findAll('div', {'class' : 'image'}):
                tag.replaceWith(tag.renderContents())
            for tag in p.findAll('div', {'class' : 'left'}):
                tag.replaceWith(tag.renderContents())
            for tag in p.findAll('br'):
                tag.extract()
            for tag in p.findAll('font'):
                tag.replaceWith(tag.renderContents())
            for tag in p.findAll('object'):
                tag.extract()
            for tag in p.findAll('iframe'):
                tag.extract()
            for tag in p.findAll('i'):
                tag.replaceWith("<X>"+tag.renderContents()+"</X>")
            for tag in p.findAll('ul'):
                tag.extract()
            p = p.renderContents()
            Atext = Atext + p
    else:
        Atext == "NONE"
    if Atext != "NONE":
        Atext = replace_characters(Atext)
        Atext = tag_sentence(Atext)
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




