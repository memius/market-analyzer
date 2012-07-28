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
	if Aimg_text.span > -1:
            #Aimg_text.span.extract()
            Aimg_text.span.replaceWith(Aimg_text.span.renderContents())
	Aimg_text = Aimg_text.renderContents().strip()
    else:
        Aimg_text = "NONE"
    Aimg_text = replace_characters(Aimg_text)
    if Aimg_text == "":
        Aimg_text = "NONE"
    if Aimg_text != "NONE":
        Aimg_text = tag_sentence(Aimg_text)
        Aimg_text = sentence_split(Aimg_text)

#lead text        
def get_Aintro(soup2):
    global Aintro
    if soup2.find("div", {"class" : "leadIn"}) > -1:
        Aintro = soup2.find("div", {"class" : "leadIn"})
    elif soup2.find("div", {"class" : "leadText"}) > -1:
        Aintro  = soup2.find("div", {"class" : "leadText"})
    else:
        Aintro = "NONE"
    if Aintro != "NONE":
        for tag in Aintro.findAll('a'):
            tag.replaceWith(tag.renderContents())
        if Aintro.find('p') > -1:
            for p in Aintro.findAll('p'):
                Aintro = p.renderContents()
                Aintro = str(Aintro)
                Aintro = Aintro.strip()
                Aintro = re.sub("\s{2,}", " ", Aintro)
        else:
            Aintro = "NONE"
    Aintro = replace_characters(Aintro)
    if Aintro == "":
        Aintro = "NONE"
    if Aintro != "NONE":
        Aintro = tag_sentence(Aintro)
        Aintro = sentence_split(Aintro)


#article text and subheadings
def get_Atext(soup2):
    global Atext
    #if soup2.find("div", {"id" : "articleBody"}) > -1:
	if soup2.find("div", {"class" : "body"}) > -1:
        #Atext = soup2.find("div", {"id" : "articleBody"})
		Atext = soup2.find("div", {"class" : "body"})
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
        #for tag in Atext.findAll('h3'):
            #tag.replaceWith(tag.renderContents())
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
        for tag in Atext.findAll('p'):
            tag.replaceWith(" "+tag_sentence(replace_characters(tag.renderContents().strip()))+" ")
        Atext = Atext.renderContents()
    else:
        Atext = "NONE"
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



##---
##NEW ENCODING
#<div class="body ">
#<p>Krimteknikere har i dag foretatt undersøkelser av brannstedet på Lademoen.</p><p>- Brannen startet i en koblingsboks tilhørende en varmtvannsbereder, sier vaktleder Are Løw-Owesen ved krimvakta på sentrum politistasjon i Trondheim.</p><p><strong><em><u>LES OGSÅ: <a href="http://www.adressa.no/nyheter/trondheim/article3241457.ece" target="_blank">Store skader etter brannen</a></u></em></strong></p><p><u><em><strong>LES OGSÅ: <a href="http://www.adressa.no/nyheter/trondheim/article3241095.ece">Kjempet mot flammene</a></strong></em></u></p><p><strong><em><u>SE OGSÅ:<a href="http://www.adressa.no/tv/?id=20218"> - Våknet av bråk og luktet røyk</a></u></em></strong></p><p>Han forteller at brannen spredte seg fra baksiden av en vegg i tredje etasje, og tok derifra veien opp til en leilighet i fjerde etasje.</p><p>- Plasseringen gjorde at brannen ble vanskelig å lokalisere og slukke, sier Løw-Owesen.</p><p> Politiet vil foreløpig ikke spekulere i årsaken til at koblingsboksen begynte å brenne.</p><p>- Neste steg er å vurdere om dette skyldes en koblingsfeil, sier Løw-Owesen.</p><p> </p>
#</div>
