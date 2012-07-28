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
def get_Adoc_title(soup):
    global Adoc_title
    if soup.title > -1:
        Adoc_title = soup.title.renderContents()
    else:
        Adoc_title = "NONE"
    Adoc_title = replace_characters(Adoc_title)

#tags keywords topics       
def get_Akeywords(soup):
    global Akeywords
    if soup.find("meta", {"name" : "keywords"})['content'] > -1:
        Akeywords = soup.find("meta", {"name" : "keywords"})['content']
    else:
        Akeywords = "NONE"
    Akeywords = replace_characters(Akeywords)

#article header    
#NB! leadtitle and subtitle inside <h2>-tags, not handled atm
def get_Atitle(soup):
    global Atitle
    if soup.find("div", {"id" : "articleTop"}) > -1:
        top = soup.find("div", {"id" : "articleTop"})
        if top.h1 > -1:
            for tag in top.h1.findAll('a'):
                tag.replaceWith(tag.renderContents())
            Atitle = top.h1.renderContents()
    elif soup.find("div", {"class" : "title"}) > -1: #e24.no
        title = soup.find("div", {"class" : "title"})
        for tag in title.findAll("span"):
            tag.replaceWith(tag.renderContents())
        for tag in title.findAll("h1"):
            tag.replaceWith(tag.renderContents())
        for tag in title.findAll("img"):
            tag.extract()
        Atitle = title.renderContents()
    elif soup.h1 > -1:
        for tag in soup.h1.findAll('a'):
            tag.replaceWith(tag.renderContents())
        Atitle = soup.h1.renderContents()
    else:
        Atitle = "NONE"
    if soup.find("div", {"id" : "artikkelspalte"}) > -1:
        if soup.find("div", {"id" : "artikkelspalte"}).h2 > -1:
            for tag in soup.find("div", {"id" : "artikkelspalte"}).h2.findAll("img"):
                tag.extract()
            Atitle = "<X>"+soup.find("div", {"id" : "artikkelspalte"}).h2.renderContents().strip()+"</X>"+Atitle #pre-header
    if soup.find("div", {"id" : "stortArtikkelBilde"}) > -1:
        if soup.find("div", {"id" : "stortArtikkelBilde"}).h2 > -1:
            for tag in soup.find("div", {"id" : "stortArtikkelBilde"}).h2.findAll("img"):
                tag.extract()
            Atitle = Atitle+"<X>"+soup.find("div", {"id" : "stortArtikkelBilde"}).h2.renderContents()+"</X>" #subheader
    if Atitle != "NONE":
        Atitle = replace_characters(Atitle)
#        Atitle = tag_sentence(Atitle)
#        Atitle = sentence_split(Atitle)

#image caption          
def get_AimgText(soup):
    global Aimg_text
    if soup.find("span", {"class" : "edrumImageCaption"}) > -1:
	Aimg_text = soup.find("span", {"class" : "edrumImageCaption"})
	Aimg_text = Aimg_text.renderContents().strip()
    else:
        Aimg_text = "NONE"
    if Aimg_text != "NONE":
        Aimg_text = replace_characters(Aimg_text)
 #       Aimg_text = tag_sentence(Aimg_text)
 #       Aimg_text = sentence_split(Aimg_text)

#lead text         
def get_Aintro(soup):
    global Aintro
    if soup.find("p", {"class" : "ingress"}) > -1:
        Aintro = soup.find("p", {"class" : "ingress"})
        for tag in Aintro.findAll('a'):
            tag.replaceWith(tag.renderContents())
        Aintro = Aintro.renderContents()
    elif soup.find("div", {"id" : "articleContent"}) > -1:
        AC = soup.find("div", {"id" : "articleContent"})
        if AC.find("div", {"class" : "leadText"}) > -1:
            leadtext = AC.find("div", {"class" : "leadText"})
            for tag in leadtext.findAll('p'):
                tag.replaceWith(tag.renderContents())
            Aintro = leadtext.renderContents()
    else:
        Aintro = "NONE"
    if Aintro != "NONE":
        Aintro = replace_characters(Aintro)
#        Aintro = tag_sentence(Aintro)
#        Aintro = sentence_split(Aintro)

def get_Atext(soup):
    global Atext
    if soup.find("p", {"id" : "brodtekst_uten_bilde"}) > -1:
        Atext = soup.find("p", {"id" : "brodtekst_uten_bilde"}) 
        for tag in Atext.findAll('a'):
            if tag.find('b') > -1:
                tag.extract()
            else:
                tag.replaceWith(tag.renderContents())
        for tag in Atext.findAll('table'):
            tag.extract()
        for tag in Atext.findAll('b'):
            tag.replaceWith("<X>"+tag.renderContents()+"</X>")
        Atext = Atext.renderContents()
    elif soup.find("div", {"xtcz" : "articleBodyText"}) > -1: #e24.no
        Atext = soup.find("div", {"xtcz" : "articleBodyText"})
        for tag in Atext.findAll("a", {"href" : re.compile("http://e24.no/")}):
            tag.replaceWith(tag.renderContents())
        for tag in Atext.findAll("a"):
            tag.replaceWith(tag.renderContents())
        for tag in Atext.findAll("em"):
            tag.replaceWith(tag.renderContents())
        for tag in Atext.findAll("strong"):
            for emtag in tag.findAll("em"):
                emtag.replaceWith(emtag.renderContents())
            tag.replaceWith(tag.renderContents())
        for tag in Atext.findAll("ul"):
            tag.extract()
        for tag in Atext.findAll('p'):
#            tag.replaceWith(" "+tag_sentence(replace_characters(tag.renderContents().strip()))+" ")
            tag.replaceWith(" "+replace_characters(tag.renderContents().strip())+" ")
        Atext = Atext.renderContents()
    else:
        Atext = "NONE"
    if Atext != "NONE":
        Atext = replace_characters(Atext)
#        Atext = tag_sentence(Atext)
#        Atext = sentence_split(Atext)        
        
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




