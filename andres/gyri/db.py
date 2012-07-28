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
    if soup2.find("meta", {"name" : "title"}) > -1:
        Adoc_title = soup2.find("meta", {"name" : "title"})
        Adoc_title = Adoc_title["content"]
    else:
        Adoc_title = "NONE"

#tags keywords topics      
def get_Akeywords(soup2):
    global Akeywords
    if soup2.find("meta", {"name" : "keywords"}) > -1:
        Akeywords = soup2.find("meta", {"name" : "keywords"})
        Akeywords = Akeywords["content"]
    Akeywords = "NONE"
    
#article header
def get_Atitle(soup2):
    global Atitle
    if soup2.find("span", { "id" : "webTitleSpan"}) > -1:
        Atitle = soup2.find("span", { "id" : "webTitleSpan"})
        Atitle = Atitle.renderContents()
    else:
        Atitle = "NONE"
    if Atitle != "NONE":
        Atitle = replace_characters(Atitle)
        Atitle = tag_sentence(Atitle)
        Atitle = sentence_split(Atitle)

#image caption         
def get_AimgText(soup2):
    global Aimg_text
    it = ""
    if soup2.find("p", {"class" : re.compile("imageCaption")}) > -1:
        Aimg_texts =  soup2.findAll("p", {"class" : re.compile("imageCaption")})
        for img in Aimg_texts:
            for tag in img.findAll("a"):
                tag.replaceWith(tag.renderContents())
            for tag in img.findAll("gjensyn"):
                tag.extract()
            img = img.renderContents()
            img = re.sub("[fF][oO][tT][oO]:\s*[A-ZÆØÅ].*", "", img)
            img = re.sub("<b id=.*>", "", img)
            it = it + img + " "
        Aimg_text = it
    else:
        Aimg_text = "NONE"
    if Aimg_text != "NONE":
        Aimg_text = replace_characters(Aimg_text)
        Aimg_text = tag_sentence(Aimg_text)
        Aimg_text = sentence_split(Aimg_text)

#lead text        
def get_Aintro(soup2):
    global Aintro
    if soup2.h2 > -1:
        Aintro = soup2.h2
        for tag in Aintro.findAll("b", {"id" : re.compile("ext-gen")}):
            tag.replaceWith("<X>"+tag.renderContents()+"</X>")
        for tag in Aintro.findAll("span"):
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
    if soup2.find("div", {"id" : "editableBodyText"}) > -1:
        Atext = soup2.find("div", {"id" : "editableBodyText"})
        for tag in Atext.findAll("b", {"class" : "mtit"}):
            tag.replaceWith("<X>"+tag.renderContents().strip()+"</X>")
            tag = tag.renderContents()
            tag = tag.replace("</b>", "")
            tag = tag.replace("\n", "")
        for tag in  Atext.findAll("strong", {"class" : "mtit"}):
            tag.extract()
        for tag in Atext.findAll("hl2"):
            tag.extract()
        for tag in Atext.findAll("o:p"):
            tag.extract()
        for tag in Atext.findAll("a"): #Sometimes the content of the a-tag is a unit (or sentence), but most often it is part of a larger structure/sentence.
            tag.replaceWith(tag.renderContents()) #Text found inside a-elements are thus not embedded in "<X>"-tags, since this would break up sentences into syntactically ill-formed units
        for tag in Atext.findAll("div"):
            tag.replaceWith(tag.renderContents())
        for tag in Atext.findAll("media"):
            tag.extract()
        for tag in Atext.findAll("b"):
            tag.replaceWith(tag.renderContents())
        #seqence of exceptions due to errors I couldn't solve
        try:
            for tag in Atext.findAll("p"):
                tag.replaceWith(tag.renderContents())
        except AttributeError:
            pass
        try:
            for tag in Atext.findAll("br"):
                tag.extract()
        except AttributeError:
            pass
        try:
            for tag in Atext.findAll("span"):
                tag.replaceWith(tag.renderContents())
                tag.extract()
        except AttributeError:
            pass
        Atext = Atext.renderContents()
        Atext = Atext.replace("<div class=\"fg-black art-ingress1\">(Dagbladet):", "")
        Atext = Atext.replace("</div>", "")
    else:
        Atext = "NONE"
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




