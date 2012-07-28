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
#Adoc_title = ""
Akeywords = ""
Atitle = ""
AimgText = ""
Aintro = ""
Atext = ""

#document title
def get_Atitle(soup2):
    global Atitle
    Atitle = ""
    if soup2.h1 > -1:
        Atitle = soup2.h1.renderContents().strip()
    else:
        Atitle = "NONE"
    if Atitle != "" and Atitle != "NONE":
        Atitle = replace_characters(Atitle)
        Atitle = tag_sentence(Atitle)
        Atitle = sentence_split(Atitle)

        
#image caption         
def get_AimgText(soup2):
    global Aimg_text
    Aimg_text = ""
    if soup2.find("div", {"class" : "caption-inner"}) > -1: 
        Aimg_text = soup2.find("div", {"class" : "caption-inner"})
        Aimg_text = Aimg_text.renderContents().strip()
    else:
        Aimg_text = "NONE"
    if Aimg_text != "NONE":
        Aimg_text = replace_characters(Aimg_text)
        Aimg_text = tag_sentence(Aimg_text)
        Aimg_text = sentence_split(Aimg_text)

#lead text
#<p class="ingress">       
def get_Aintro(soup2):
    global Aintro
    Aintro = ""
    if soup2.find("p", {"class" : "ingress"}) > -1:
        Aintro = soup2.find("p", {"class" : "ingress"}).renderContents()
    else:
        Aintro = "NONE"
    if Aintro != "NONE":
        Aintro = replace_characters(Aintro)
        Aintro = tag_sentence(Aintro)
        Aintro = sentence_split(Aintro)


#article text and subheadings
#<div id="body_text" class="clearfloat">
def get_Atext(soup2):
    global Atext
    txt = ""
    if soup2.find("div", {"id" : "body_text"}) > -1:
        Atext = soup2.find("div", {"id" : "body_text"})
        ## for p in Atext.findAll('p'):
            ## p.renderContents()
        ## Atext = Atext.renderContents().strip()
        for tag in Atext.findAll('p'):
            for atag in tag.findAll('a'):
                atag.replaceWith(atag.renderContents())
            for spantag in tag.findAll("span", {"class" : "bold"}):
                spantag.replaceWith("<X>"+spantag.renderContents()+"</X>")
            for spantag in tag.findAll("span", {"class" : "italic"}):
                spantag.replaceWith("<X>"+spantag.renderContents()+"</X>")
            tag.replaceWith(" "+tag_sentence(replace_characters(tag.renderContents().strip()))+" ")
        Atext = Atext.renderContents()
    else:
        Atext = "NONE"
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




