#!/usr/bin/python
# coding: utf-8

#python modules
import sys, os, string, re, urllib2, logging, string

from bs4 import BeautifulSoup

#my own modules:
from replace_characters import replace_characters

import crawl, clean, block

#reload(sys) # leads to illegal seek error (needs one reload to load page)
#sys.setdefaultencoding('utf-8')
logging.basicConfig(filename='fetch.log', filemode='w', level=logging.DEBUG)


# eksempel fra 2009:
# html = urllib.urlopen(address).read()
# soup = BeautifulSoup.BeautifulSoup(html)
# texts = soup.findAll(text=True)

# def visible_text(element):
#     if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
#         return ''
#     result = re.sub('<!--.*-->|\r|\n', '', str(element), flags=re.DOTALL)
#     result = re.sub('\s{2,}|&nbsp;', ' ', result)
#     return result

# visible_elements = [visible_text(elem) for elem in texts]
# visible_text = ''.join(visible_elements)
# print(visible_text)

#         return False
#     elif re.match('<!--.*-->', str(element)):
#         return False
#     return True

# visible_texts = filter(visible, texts)


def article(url):
    #the whole rpc thing is not needed here, and does not really solve the background issue anyway.
    # rpc = urlfetch.create_rpc()

    #debugging only:
#    url = "http://www.sfgate.com/news/article/US-economic-growth-slowed-to-1-5-pct-rate-in-Q2-3740379.php"
#    url = "http://www.dagbladet.no/2012/07/19/kultur/film/the_dark_knight_rises/christopher_nolan/premiere/22599777/"
#    url = "http://www.vg.no/nyheter/innenriks/artikkel.php?artid=10059206"
#    url = "http://www.dagensit.no/article2439589.ece"
#    url = "http://www.bloomberg.com/news/2012-07-24/u-s-stock-futures-are-little-changed-texas-declines.html"

    # #do other things while this goes on in the background

    # try:
    #     result = rpc.get_result()
    #     if result.status_code == 200:
    #         html = result.content

    # except urlfetch.DownloadError:
    #     print 'request timed out or failed.'

    #     try:
    #         soup = BeautifulSoup(html)
    #     except TypeError:
    #         print "input error, bad html or something."    


    logging.debug('type(url): %s END type(url)', type(url))
#    try:
    html = urllib2.urlopen(url).read()
    logging.debug('type(html): %s END type(html)', type(html))
#        try:
    soup = BeautifulSoup(html)
    logging.debug('type(soup): %s END type(soup)',type(soup))

#    logging.debug('soup: %s END soup', soup)

    # dt = doc_title(soup) #.strip()
    # k = keywords(soup)
    # t = title(soup)
    # it = img_text(soup)
    # i = intro(soup)
    txt = text(soup)
    #     except TypeError:
    #         print "input error when trying to make soup"
    # except:
    #     print '404 or 403 or something.'

    # logging.debug('doc_title: %s END doc_title', doc_title)
    # logging.debug('keywords: %s END keywords', keywords)
    # logging.debug('title: %s END title', title)
    # logging.debug('img_text: %s END img_text', img_text)
    # logging.debug('intro: %s END intro', intro)
    logging.debug('txt: %s END txt', txt)


    return txt #dt, k, t, it, i, txt

#any non-whitespace character, followed by
#any character, followed by
#at least one more of any character, not greedy, followed by
#a dot, an exclamation mark or a question mark
#all of the above only if followed by
#any whitespace character or the end of a line.
def text(soup):

    text = soup.get_text()
    #debugging only:
    #text = block.string5

    #this works well, but takes fewer sentences than the other one
    #sentence = re.compile("(\S.+?[.!?])(?=\s+|$|\")")


    #sentence = re.compile("(?<=[.?!]|^).*?(?=([.?!])\s{0,3}[A-Z]|$)")
    #sentence = re.compile("(?:\s[a-z]\.(?:[a-z]\.)?|.)+?[.?!]+") #php attempt. uncommented.

    #works better, but takes more sentences (junk) than the other one.
    sentence = re.compile("[^.!?\s][^.!?]*(?:[.!?](?!['\"]?\s|$)[^.!?]*)*[.!?]?['\"]?(?=\s|$)") 
    # sentence = re.compile("""
    #     [^\.!?\s]         # first char is not punct or whitespace
    #     [^\.!?]*          # greedily consume until punct
    #     (?:               # group for unrolling the loop
    #     [\.!?]             # (special) inner punct ok if
    #     (?!['\"]?\s|$)    # not followed by quotes, whitespace or eol
    #     [^.!?]*           # greedily consume until punct
    #     )*                # zero or more (special normal)*)
    #     [\.!?]?            # optional ending punct
    #     ['\"]?            # optional closing quote
    #     (?=\s|$)"         # only if followed by whitespace or eol
    # """, re.VERBOSE)



    sentences = re.findall(sentence, text)

    #junk cleaning before storing in db:
    content = clean.junk(sentences)
    #strict cleaning before sending to crm (so it should be moved to the file that does that):
    content = clean.strict(content)

    #return text_no_tags
    return content

#print article("http://www.businessweek.com/news/2012-07-31/microsoft-says-it-s-open-to-patent-peace-with-google-s-motorola")

#print article("http://www.newstodaydigest.com/google-inc-goog-added-the-google-hangouts-feature-in-place-of-gmail-video-chats/121550/")

#print article("http://www.businessweek.com/news/2012-07-31/apple-paddy-power-perdue-netflix-intellectual-property")

#print article("http://www.valuewalk.com/2012/07/q2-earnings-preview-from-the-tech-behemoths-google-inc-goog-and-microsoft-corporation-msft/")

#print article("http://www.valuewalk.com/2012/07/apple-inc-aapl-boasts-three-million-mountain-lion-downloads-within-four-days/")

#document title
def doc_title(soup):
    # if paper == "vg":
    if soup.title > -1:
        doc_title = soup.title.renderContents()
    elif soup.find("meta", {"name" : "title"}) > -1:
        doc_title = soup.find("meta", {"name" : "title"})
        doc_title = doc_title["content"]
    else:
        doc_title = "None"
    #doc_title = replace_characters(doc_title)
    logging.debug('doc_title: %s END doc_title',doc_title)
    return doc_title

#tags keywords topics - not really; it extracts the various fields in the url /reise/norgesferie/vannski, f.eksoo.
def keywords(soup):
    # if paper == "vg":
        # fjernet ['content']. det fjerner 'NoneType' object is unsubscriptable
    if soup.find("meta", {"name" : "keywords"}) > -1: 
        keywords = soup.find("meta", {"name" : "keywords"})['content']
    # elif paper == "db":
    elif soup.find("meta", {"name" : "keywords"}) > -1:
        keywords = soup.find("meta", {"name" : "keywords"})
        keywords = keywords["content"]
    else:
        keywords = "no keywords"
    #keywords = replace_characters(keywords)
    logging.debug('keywords: %s END keywords',keywords)
    return keywords

#article header    
#NB! leadtitle and subtitle inside <h2>-tags, not handled atm
def title(soup):
    # if paper == "vg":
    if soup.find("div", {"id" : "articleTop"}) > -1:
        top = soup.find("div", {"id" : "articleTop"})
        if top.h1 > -1:
            for tag in top.h1.findAll('a'):
                tag.replaceWith(tag.renderContents())
            title = top.h1.renderContents()
    elif soup.find("div", {"class" : "title"}) > -1: #e24.no
        title = soup.find("div", {"class" : "title"})
        for tag in title.findAll("span"):
            tag.replaceWith(tag.renderContents())
        for tag in title.findAll("h1"):
            tag.replaceWith(tag.renderContents())
        for tag in title.findAll("img"):
            tag.extract()
        title = title.renderContents()
    elif soup.h1 > -1:
        for tag in soup.h1.findAll('a'):
            tag.replaceWith(tag.renderContents())
        title = soup.h1.renderContents()
    elif soup.find("div", {"id" : "artikkelspalte"}) > -1:
        if soup.find("div", {"id" : "artikkelspalte"}).h2 > -1:
            for tag in soup.find("div", {"id" : "artikkelspalte"}).h2.findAll("img"):
                tag.extract()
            title = "<X>"+soup.find("div", {"id" : "artikkelspalte"}).h2.renderContents().strip()+"</X>"+title #pre-header
    if soup.find("div", {"id" : "stortArtikkelBilde"}) > -1:
        if soup.find("div", {"id" : "stortArtikkelBilde"}).h2 > -1:
            for tag in soup.find("div", {"id" : "stortArtikkelBilde"}).h2.findAll("img"):
                tag.extract()
            title = title+"<X>"+soup.find("div", {"id" : "stortArtikkelBilde"}).h2.renderContents()+"</X>" #subheader
    # elif paper == "db":
    if soup.find("span", { "id" : "webTitleSpan"}) > -1:
        title = soup.find("span", { "id" : "webTitleSpan"})
        title = title.renderContents()
    else:
        title = "no data"
    #if title != "no data":
        #title = replace_characters(title)
#        title = tag_sentence(title)
#        title = sentence_split(title)
    logging.debug('title: %s END title',title)
    return title

#image caption          
def img_text(soup):
    it = ""
    if soup.find("span", {"class" : "edrumImageCaption"}) > -1:
	img_text = soup.find("span", {"class" : "edrumImageCaption"})
	img_text = img_text.renderContents().strip()
    elif soup.find("p", {"class" : re.compile("imageCaption")}) > -1:
        img_texts =  soup.findAll("p", {"class" : re.compile("imageCaption")})
        for img in img_texts:
            for tag in img.findAll("a"):
                logging.debug("tags in img.findAll('a'): %s END tags in img.findAll('a')",tag)
                tag.replaceWith(tag.renderContents())
            for tag in img.findAll("gjensyn"):
                tag.extract()
            img = img.renderContents()
            img = re.sub("[fF][oO][tT][oO]:\s*[A-ZÆØÅ].*", "", img)
            img = re.sub("<b id=.*>", "", img)
            it = it + img + " "
        img_text = it
    else:
        img_text = "no data"
#    if img_text != "no data":
#        img_text = replace_characters(img_text)
 #       img_text = tag_sentence(img_text)
 #       img_text = sentence_split(img_text)
    logging.debug('img_text: %s END img_text',img_text)
    return img_text

#lead text         
def intro(soup):
    if soup.find("p", {"class" : "ingress"}) > -1:
        intro = soup.find("p", {"class" : "ingress"})
        for tag in intro.findAll('a'):
            tag.replaceWith(tag.renderContents())
        intro = intro.renderContents()
    elif soup.find("div", {"id" : "articleContent"}) > -1:
        article_content = soup.find("div", {"id" : "articleContent"})
        if articleContent.find("div", {"class" : "leadText"}) > -1:
            leadtext = articleContent.find("div", {"class" : "leadText"})
            for tag in leadtext.findAll('p'):
                tag.replaceWith(tag.renderContents())
            intro = leadtext.renderContents()
    elif soup.h2 > -1:
        intro = soup.h2
        for tag in intro.findAll("b", {"id" : re.compile("ext-gen")}):
            tag.replaceWith("<X>"+tag.renderContents()+"</X>")
        for tag in intro.findAll("span"):
            tag.replaceWith(tag.renderContents())
        intro = intro.renderContents()
    else:
        intro = "no data"
#    if intro != "no data":
#        intro = replace_characters(intro)
#        intro = tag_sentence(intro)
#        intro = sentence_split(intro)
    logging.debug('intro: %s END intro',intro)
    return intro

def old_text(soup):    
    if soup.find("p", {"id" : "brodtekst_uten_bilde"}) > -1:
        text = soup.find("p", {"id" : "brodtekst_uten_bilde"}) 
        for tag in text.findAll('a'):
            logging.debug("tags in findAll('a') in text(): %s END tags in findAll('a') in text()",tag)
            if tag.find('b') > -1:
                tag.extract()
            else:
                tag.replaceWith(tag.renderContents())
        for tag in text.findAll('table'):
            tag.extract()
        for tag in text.findAll('b'):
            logging.debug("tags in findAll('b') in text(): %s END tags in findAll('b') in text()",tag)
            tag.replaceWith("<X>"+tag.renderContents()+"</X>")
        text = text.renderContents()
    elif soup.find("div", {"xtcz" : "articleBodyText"}) > -1: #e24.no
        text = soup.find("div", {"xtcz" : "articleBodyText"})
        for tag in text.findAll("a", {"href" : re.compile("http://e24.no/")}):
            tag.replaceWith(tag.renderContents())
        for tag in text.findAll("a"):
            logging.debug("tags2 in findAll('a') in text(): %s END tags2 in findAll('a') in text()",tag)
            tag.replaceWith(tag.renderContents())
        for tag in text.findAll("em"):
            tag.replaceWith(tag.renderContents())
        for tag in text.findAll("strong"):
            for emtag in tag.findAll("em"):
                emtag.replaceWith(emtag.renderContents())
            tag.replaceWith(tag.renderContents())
        for tag in text.findAll("ul"):
            tag.extract()
        for tag in text.findAll('p'):
            logging.debug("tags in findAll('p') in text(): %s END tags in findAll('p') in text()",tag)
#            tag.replaceWith(" "+tag_sentence(replace_characters(tag.renderContents().strip()))+" ")
            tag.replaceWith(" "+replace_characters(tag.renderContents().strip())+" ")
        text = text.renderContents()
    elif soup.find("div", {"id" : "editableBodyText"}) > -1:
        text = soup.find("div", {"id" : "editableBodyText"})
        logging.debug("editable body text: %s END editable body text",text)
        for tag in text.findAll("b", {"class" : "mtit"}):
            tag.replaceWith("<X>"+tag.renderContents().strip()+"</X>")
            tag = tag.renderContents()
            tag = tag.replace("</b>", "")
            tag = tag.replace("\n", "")
        for tag in  text.findAll("strong", {"class" : "mtit"}):
            tag.extract()
        for tag in text.findAll("hl2"):
            tag.extract()
        for tag in text.findAll("o:p"):
            tag.extract()
        for tag in text.findAll("a"): #Sometimes the content of the a-tag is a unit (or sentence), but most often it is part of a larger structure/sentence.
            tag.replaceWith(tag.renderContents()) #Text found inside a-elements are thus not embedded in "<X>"-tags, since this would break up sentences into syntactically ill-formed units
        for tag in text.findAll("div"):
            tag.replaceWith(tag.renderContents())
        for tag in text.findAll("media"):
            tag.extract()
        for tag in text.findAll("b"):
            tag.replaceWith(tag.renderContents())
        #seqence of exceptions due to errors I couldn't solve
        try:
            for tag in text.findAll("p"):
                tag.replaceWith(tag.renderContents())
        except AttributeError:
            logging.debug('attribute error 1')
        try:
            for tag in text.findAll("br"):
                tag.extract()
        except AttributeError:
            logging.debug('attribute error 2')
        try:
            for tag in text.findAll("span"):
                tag.replaceWith(tag.renderContents())
                tag.extract()
        except AttributeError:
            logging.debug('attribute error 3')
        text = text.renderContents()
        text = text.replace("<div class=\"fg-black art-ingress1\">(Dagbladet):", "")
        text = text.replace("</div>", "")
        logging.debug("editable body text2: %s END editable body text2",text)
    elif soup.find("(Dagbladet)"):
        for text in soup.findAll("(Dagbladet)"):
            logging.debug("(Dagbladet): %s END (Dagbladet)",text)
    else:
        return soup.get_text()
    if text != "no data":
        text = replace_characters(text)
#        text = tag_sentence(text)
#        text = sentence_split(text)        
    logging.debug('text: %s END text',text)
    return text
        

# def news_page(): #uses the urls from crawl to get to news pages containing articles, to be handled later, by article()
#     div = soup.find("div", {"id" : "Article*"}) > -1:


#debugging only:
#article('bla bla dot no')






#     elif soup.find("div", {"id" : "Article*"}) > -1:


# the work of getting hold of the article text (before actually fetching the article) belongs in this module, since crawl only returns links.

# this means that this module has to handle businessweek, which has an extra link which simply says 'go to businessweek' on a separate page before you actually get there. it also has to handle every other gotcha that shows up. 
