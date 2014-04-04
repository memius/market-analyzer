# coding: utf-8



    # #non-whitespace characters followed by a space, period, question mark or exclamation mark:
    # # should have words ending in  quotations, commas too.
    # token = re.compile("[^\.,\?!;:]\S+?(?= |\.|,|\?|!|;|:)") 



# you should look at individual words - words that contain things like \ or > are obviously not words.

# also, look at the thinking behind indicators. are they whole words, or just letters? perhaps words containing indicators should be cut right out?

# replace html codes &quot; with their real counterparts. you can probably find something for this online.

# class= means it is a rubbish word; class="alignleft' and so on. title= also. alt= too. width= too.


import re, string, logging

from bs4 import BeautifulSoup as bs
from google.appengine.api import memcache
from google.appengine.ext import db

import utils, analyze

from models import Article

logging.getLogger().setLevel(logging.DEBUG)

#1. display readable text to user - here, you only need to remove boilerplate. DONE.
#2. deliver clean, unequivocal text to the classifier - here, you need to normalize, remove whitespace, punctuation.
#3. the duplicate checker needs the same as the classifier.

#what you show the user should have the origin (forbes, insider monkey, etc) and the title, but not be a link. you should provide the link somewhere else. the thing you show could be called an excerpt, and contain as much text as possible, but not pretty and perfect.


def clean(article):

    soup = bs(unicode(article.html))
    text = remove_outright(soup.get_text())
    sentences = sentencify(text)
    sentences = filter_sentences(sentences)
    sentences = junk(sentences)
    # # strict(sentences)
    text = ' '.join(sentences)        
    # # if utils.is_prose(text):
    article.text = text
    article.clean = True
    # # else:
    # #     db.delete(article)
    # article.clean = True
    article.put()

def clean_recent(): # only cleans recently scraped articles ("article_keys" from memcache)


#     # article_ids = memcache.get("article_ids")
#     # if article_ids:
#     #     articles = []
#     #     for article_id in article_ids:
#     #         article = Article.get_by_id(article_id) 
#     #         articles.append(article)

#     #     for article in articles:
#     #         clean(article)

#     # else: # hvis article_ids er tom, maa artikler hentes fra db:
#     q = Article.all().filter("clean =", None) # both None and False
#     articles = q.fetch(2)
# #        if articles:
#     for article in articles:
#         clean(article)

#use article ids, which consists of recently scraped articles that have been duplicate (by title) checked. check their flag - if not clean, clean. some of them will be from the last round, and will be clean already.

    article_keys = memcache.get("article_keys")
    # logging.debug("clean() article keys: %s", article_keys[:3])
    clean_ctr = 0
    if article_keys:
        for article_key in article_keys:
#        article = cleaning.pop() # pop() returns last item, and changes the list in place
            article = Article.get_by_id(article_key.id())
            if article != None:
                if article.clean != True:
                    clean(article)
                    clean_ctr += 1
        # cleaning.remove(article) not needed, because pop removes it for us.
        memcache.set("article_keys", article_keys)

    logging.debug("cleaned %s articles", clean_ctr)


# def clean_all(keys):
#     for key in keys:
#         article = Article.get_by_id(key.id())
#         if article != None:
#             if article.clean != True:
#                 clean(article)


    # else: # hvis article_keys er tom, maa artikler hentes fra db:
    #     q = Article.all().filter("clean =", None) # should have both None and False
    #     articles = q.fetch(8)
    #     memcache.add("cleaning", articles)

#removes offending strings immediately:
def remove_outright(text):

    #replacing the various curly quotes:
    curly_quote = re.compile("’")
    text = re.sub(curly_quote,"'",text)
    curly_quote = re.compile("‘")
    text = re.sub(curly_quote,"'",text)
    curly_quote = re.compile("”")
    text = re.sub(curly_quote,"'",text)
    curly_quote = re.compile("“")
    text = re.sub(curly_quote,"'",text)

    #replacing dashes — with hyphens - 
    dash = re.compile("–")
    text = re.sub(dash,"-",text) 
    dash = re.compile("—") #yes, there are two types that look the same.
    text = re.sub(dash,"-",text) 

    indicators = []

    indicators.append(re.compile("\"http://.*?\""))
    indicators.append(re.compile("<.*?>"))
#    indicators.append(re.compile(""))
    indicators.append(re.compile("gaq"))
    indicators.append(re.compile("push\("))
    indicators.append(re.compile("setAccount"))
    indicators.append(re.compile("trackPageview"))
    indicators.append(re.compile("function\(\)"))
    indicators.append(re.compile("where is \w+ headed exactly\? ", re.IGNORECASE))
    indicators.append(re.compile("latest news items.*?noparsing", re.IGNORECASE))
    indicators.append(re.compile("newer news items.*?before risking your investments on the financial markets", re.IGNORECASE))
    indicators.append(re.compile("what are your thoughts on this.*?has been buying and selling", re.IGNORECASE))
    #these apparently take too much:
    #indicators.append(re.compile("we will keep you updated on this story.*?has been buying and selling", re.IGNORECASE))
    #indicators.append(re.compile("don't miss out our special coverage.*?consult your financial advisor", re.IGNORECASE))
    #indicators.append(re.compile("our blog contact us.*?forward print save", re.IGNORECASE))
    #indicators.append(re.compile("the motley fool recommends.*?has been buying and selling", re.IGNORECASE))
    #indicators.append(re.compile("page 1 of 2next.*?has been buying and selling", re.IGNORECASE))
    indicators.append(re.compile("You can follow any responses to this entry through the RSS 2.0 feed. ", re.IGNORECASE))
    indicators.append(re.compile("#post .*? we8u", re.IGNORECASE))
    indicators.append(re.compile("#panel .content .right {.*? before the closing tag. ", re.IGNORECASE))
    indicators.append(re.compile("xhtml \d+\.\d+", re.IGNORECASE))
    indicators.append(re.compile("\.com/facebook-comments/\)", re.IGNORECASE))
    indicators.append(re.compile("can \w+ show a strong recovery\? ", re.IGNORECASE))
    indicators.append(re.compile("should \w+ be a buy or sell now\? ", re.IGNORECASE))
    indicators.append(re.compile("what are \w+'s charts signaling for traders\? ", re.IGNORECASE))
    indicators.append(re.compile("Today's Stocks in focus are: \w+(, | )\w+ ", re.IGNORECASE))
    indicators.append(re.compile("AnotherWinningTrade\.com offers its daily alerts and market content newsletter to investors looking for the best information available!"))
    indicators.append(re.compile("To receive our FREE, comprehensive newsletter, visit AnotherWinningTrade\.com\. "))
    indicators.append(re.compile("[^\.,\?!;:\"]\S*?//\S*?(?= |\.|,|\?|!|;|:|\")")) # word with // in it 
    indicators.append(re.compile("[^\.,\?!;:\"]\S+?-\S+?-\S+?(?= |\.|,|\?|!|;|:|\")")) # >1 hyphen in word
    indicators.append(re.compile("[^\.,\?!;:\"]\S+?\.\S+?\.\S+?(?= |\.|,|\?|!|;|:|\")")) # >1 period in word
    indicators.append(re.compile("htmlStocks on Trader's List: .+? (.+?) and .+? (.+?)\. ", re.IGNORECASE))
    indicators.append(re.compile("We have the top alerts in the industry\. ", re.IGNORECASE))
    indicators.append(re.compile("social sharing toolkit ", re.IGNORECASE))
    indicators.append(re.compile("Quick Adsense WordPress Plugin: ", re.IGNORECASE))
    indicators.append(re.compile("\.net/", re.IGNORECASE))
#    indicators.append(re.compile("", re.IGNORECASE))
    indicators.append(re.compile("subscribe enter your email:", re.IGNORECASE))
    indicators.append(re.compile("delivered by feedburner subscribe via rss", re.IGNORECASE))
    indicators.append(re.compile("click this link", re.IGNORECASE))
    indicators.append(re.compile("to view as rss", re.IGNORECASE))
    indicators.append(re.compile("html public", re.IGNORECASE))
    indicators.append(re.compile("find out here", re.IGNORECASE))
    indicators.append(re.compile("The opinions contained herein reflect our current judgment and are subject to change without notice.", re.IGNORECASE))

    indicators.append(re.compile("find out in this research report", re.IGNORECASE))
    indicators.append(re.compile("find out in this trend analysis report", re.IGNORECASE))
    indicators.append(re.compile("Disclaimer: Information, opinions and analysis contained herein are based on sources believed to be reliable, but no representation, expressed or implied, is made as to its accuracy, completeness or correctness.", re.IGNORECASE))

    indicators.append(re.compile(" AnotherWinningTrade.com provides its subscribers with useful, timely information and exclusive alerts on penny stocks, mid cap stocks and large cap stocks with the potential to deliver gains of 100%-200% or more\.", re.IGNORECASE))
    indicators.append(re.compile("The opinions contained herein reflect our current judgment and are subject to change without notice\.", re.IGNORECASE))
    indicators.append(re.compile("We accept no liability for any losses arising from an investor's reliance on or use of this report\.", re.IGNORECASE))
    indicators.append(re.compile(" This report is for information purposes only, and is neither a solicitation to buy nor an offer to sell securities\. A third party has hired and paid IO News Wire .+? dollars for the publication and circulation of this news release\.", re.IGNORECASE))
    indicators.append(re.compile("Certain information included herein is forward-looking within the meaning of the Private Securities Litigation Reform Act of 1995, including, but not limited to, statements concerning manufacturing, marketing, growth, and expansion.", re.IGNORECASE))
    indicators.append(re.compile("Such forward-looking information involves important risks and uncertainties that could affect actual results and cause them to differ materially from expectations expressed herein.", re.IGNORECASE))
    indicators.append(re.compile("We have no ownership of equity, no representation; do no trading of any kind and send no faxes or emails.", re.IGNORECASE))
    indicators.append(re.compile("html \d*?\.\d+? ", re.IGNORECASE))
    indicators.append(re.compile("insider monkey\[if gte IE 9\]>", re.IGNORECASE))
    indicators.append(re.compile("\[if \w+ IE 9\]>",re.IGNORECASE))
    indicators.append(re.compile("all rights reserved", re.IGNORECASE))
    indicators.append(re.compile("net pr news", re.IGNORECASE))
    indicators.append(re.compile("by anotherwinningtrade on", re.IGNORECASE))
    indicators.append(re.compile("all rights reserved", re.IGNORECASE)) 

    indicators.append(re.compile("Dump Your Hedge Funds and Buy This Stock ",re.IGNORECASE))
    indicators.append(re.compile("For more information on how this would change the industry, this CNBC video is a great place to start.",re.IGNORECASE))
    indicators.append(re.compile("DISCLOSURE: I have no positions in any stock mentioned. ",re.IGNORECASE))
    indicators.append(re.compile("For more news stories, visit the following pages:",re.IGNORECASE))
    indicators.append(re.compile("Download a Free Edition! ",re.IGNORECASE))
    indicators.append(re.compile("Why You Should DUMP Your Hedge Funds ",re.IGNORECASE))
    indicators.append(re.compile("so, what do you think about these comments by ",re.IGNORECASE))

    #final cleanup:
    indicators.append(re.compile("(?<=\s)[@$<>#%^{}\[\]\|]\s+")) #any of these characters alone (overlapping)
    indicators.append(re.compile("(?<=\s)[;():~.`\"/_]\s+")) #any of these characters alone (overlapping)
    indicators.append(re.compile("\s+"))
    indicators.append(re.compile("--+"))
    indicators.append(re.compile("-\s+-"))
    indicators.append(re.compile("\.\s+\."))
    indicators.append(re.compile("\s([b-hB-H]|[j-zJ-Z])\s", re.IGNORECASE)) #any letter not a or i alone

    for indicator in indicators:
    #     if re.search(indicator,text):
    #         ind = re.search(indicator,text)
    #         print 'indicator: ',ind.group(0)
        text = re.sub(indicator, " ", text)    

#    print 'clean text: ',text
    return text

def sentencify(text):
    sentence = re.compile("[^.!?\s][^.!?]*(?:[.!?](?!['\"]?\s|$)[^.!?]*)*[.!?]?['\"]?(?=\s|$|\")") #includes quote at end.    
    sentences = re.findall(sentence, text)
    # for sentence in sentences:
    #     print 'sentence: ',sentence,'\n'
    return sentences

def filter_sentences(sentences):
    clean_sentences = []
    for sentence in sentences:
        if not is_boilerplate(sentence):
            clean_sentences.append(sentence)

#    print 'clean sentences: ', clean_sentences
    return clean_sentences

def is_boilerplate(sentence):
#you should include sentences ending with : and ;, because you will want to remove those sub-sentences that are spam, and attached to prose sentences.

    indicators = []
    # indicators.append(re.compile("\S+([@$<>#%^&*{}\[\]\|](?!\")\S+)+")) #any of these characters inside words
    # indicators.append(re.compile("\S+[;():~`/_+=](?!\")\S+")) #any of these characters inside words
    # indicators.append(re.compile("\S+[0-9]\S+")) #any of these characters inside words
    # indicators.append(re.compile("[a-zA-Z]+\.[a-zA-Z]+ ")) # U.S. and D.C., but not var.function
    # indicators.append(re.compile("\s+[@<>#%^&*{}\[\]\|]\S+")) #any of these characters at beginning of word
    # indicators.append(re.compile("\s+[;():~`/_+=]\S+")) #any of these characters at beginning of word
    # indicators.append(re.compile("\s+[0-9]\S+")) #any of these characters at beginning of word
    # indicators.append(re.compile("\S+[@$<>#%^&*{}\[\]\|]\s+")) #any of these characters at end of word
    # indicators.append(re.compile("\S+[;():~`/_+=]\s+")) #any of these characters at end of word
    # indicators.append(re.compile("\S+[0-9]\s+")) #any of these characters at end of word
    indicators.append(re.compile("xhtml1", re.IGNORECASE))
    indicators.append(re.compile("gcse ", re.IGNORECASE))
    indicators.append(re.compile("cx ", re.IGNORECASE))
    indicators.append(re.compile("async", re.IGNORECASE))
    indicators.append(re.compile("protocol", re.IGNORECASE))
    indicators.append(re.compile("javascript", re.IGNORECASE))
    indicators.append(re.compile("subscribe", re.IGNORECASE))
    indicators.append(re.compile("click", re.IGNORECASE))
    indicators.append(re.compile("email", re.IGNORECASE))
    indicators.append(re.compile("rss", re.IGNORECASE))
    indicators.append(re.compile("xml", re.IGNORECASE))
    indicators.append(re.compile("news tags:", re.IGNORECASE))
    indicators.append(re.compile("see all category:", re.IGNORECASE))
    indicators.append(re.compile("ddtabcontent", re.IGNORECASE))
    indicators.append(re.compile("setpersist", re.IGNORECASE))
    indicators.append(re.compile("setselectedclasstarget", re.IGNORECASE))
    indicators.append(re.compile("init\(\)", re.IGNORECASE))
    indicators.append(re.compile("tabber advertisement", re.IGNORECASE))
    indicators.append(re.compile("comment end", re.IGNORECASE))
    indicators.append(re.compile("widgetnews", re.IGNORECASE))
    indicators.append(re.compile("by clicking submit", re.IGNORECASE))
    indicators.append(re.compile("you agree to ", re.IGNORECASE))
    indicators.append(re.compile("it only takes 5 seconds", re.IGNORECASE))
    indicators.append(re.compile("please correct it", re.IGNORECASE))
    indicators.append(re.compile("return true", re.IGNORECASE))
    indicators.append(re.compile("return false", re.IGNORECASE))
    indicators.append(re.compile("validatechk", re.IGNORECASE))
    indicators.append(re.compile("email has a mistake", re.IGNORECASE))
#    indicators.append(re.compile("", re.IGNORECASE))
    indicators.append(re.compile("oas_target", re.IGNORECASE))
    indicators.append(re.compile("oas_query", re.IGNORECASE))
    indicators.append(re.compile("document\.write", re.IGNORECASE))
    indicators.append(re.compile("href", re.IGNORECASE))
    indicators.append(re.compile("target=", re.IGNORECASE))
    indicators.append(re.compile("mc_embed_signup", re.IGNORECASE))
    indicators.append(re.compile("oas ad", re.IGNORECASE))
    indicators.append(re.compile("topright", re.IGNORECASE))
    indicators.append(re.compile("x13", re.IGNORECASE))
    indicators.append(re.compile("css link", re.IGNORECASE))
    indicators.append(re.compile("html file", re.IGNORECASE))
    indicators.append(re.compile("socialize with us!", re.IGNORECASE))
    indicators.append(re.compile("position\d", re.IGNORECASE))
    indicators.append(re.compile("plugin", re.IGNORECASE))
    indicators.append(re.compile("try again", re.IGNORECASE))
    indicators.append(re.compile("leave a reply", re.IGNORECASE))
    indicators.append(re.compile("comment_failure", re.IGNORECASE))
    indicators.append(re.compile("prowl_failure", re.IGNORECASE))
    indicators.append(re.compile("please check", re.IGNORECASE))
    indicators.append(re.compile("validation_message", re.IGNORECASE))
    indicators.append(re.compile("one or more fields were not completed", re.IGNORECASE))
    indicators.append(re.compile("leave_webapp", re.IGNORECASE))
    indicators.append(re.compile("clicking this link will ", re.IGNORECASE))
    indicators.append(re.compile("visiting this link will ", re.IGNORECASE))
    indicators.append(re.compile("browser settings", re.IGNORECASE))
    indicators.append(re.compile("web-app mode", re.IGNORECASE))
    indicators.append(re.compile("disable the menu", re.IGNORECASE))
    indicators.append(re.compile("resource page", re.IGNORECASE))
    indicators.append(re.compile("bio, quotes", re.IGNORECASE))
    indicators.append(re.compile("books, articles, videos", re.IGNORECASE))
    indicators.append(re.compile("recommended reading list", re.IGNORECASE))
    indicators.append(re.compile("premium access", re.IGNORECASE))
    indicators.append(re.compile("thank you", re.IGNORECASE))
    indicators.append(re.compile("get our newsletter", re.IGNORECASE))
    indicators.append(re.compile("written by", re.IGNORECASE))
    indicators.append(re.compile("account reset", re.IGNORECASE))
    indicators.append(re.compile("if comments are open", re.IGNORECASE))
    indicators.append(re.compile("there are no comments", re.IGNORECASE))
    indicators.append(re.compile("you must be logged", re.IGNORECASE))
    indicators.append(re.compile("noiframes", re.IGNORECASE))
    indicators.append(re.compile("requires inline", re.IGNORECASE))
    indicators.append(re.compile("oldonload", re.IGNORECASE))
    indicators.append(re.compile("explore related", re.IGNORECASE))
    indicators.append(re.compile("related content", re.IGNORECASE))
    indicators.append(re.compile("onload", re.IGNORECASE))
    indicators.append(re.compile("sitecatalyst", re.IGNORECASE))
    indicators.append(re.compile("more info available at", re.IGNORECASE))
    indicators.append(re.compile("do not remove", re.IGNORECASE))
    indicators.append(re.compile("code version", re.IGNORECASE))
    indicators.append(re.compile("begin ad tag ", re.IGNORECASE))
    indicators.append(re.compile("tile=", re.IGNORECASE))
    indicators.append(re.compile("legendary value investors", re.IGNORECASE))
    indicators.append(re.compile("robertson jr\.", re.IGNORECASE))
    indicators.append(re.compile("philip fisher", re.IGNORECASE))
    indicators.append(re.compile("bill ruane", re.IGNORECASE))
    indicators.append(re.compile("walter schloss", re.IGNORECASE))
    indicators.append(re.compile("thomas rowe price jr\.", re.IGNORECASE))
    indicators.append(re.compile("chris browne", re.IGNORECASE))
    indicators.append(re.compile("benjamin graham", re.IGNORECASE))
    indicators.append(re.compile("david dreman", re.IGNORECASE))
    indicators.append(re.compile("jesse livermore", re.IGNORECASE))
    indicators.append(re.compile("john neff", re.IGNORECASE))
    indicators.append(re.compile("sir john templeton", re.IGNORECASE))
    indicators.append(re.compile("irving kahn", re.IGNORECASE))
    indicators.append(re.compile("peter lynch", re.IGNORECASE))
    indicators.append(re.compile("mohnish pabrai", re.IGNORECASE))
    indicators.append(re.compile("footer-container",re.IGNORECASE))
    indicators.append(re.compile("text-link",re.IGNORECASE))
    indicators.append(re.compile("ad tag",re.IGNORECASE))
    indicators.append(re.compile("button begin",re.IGNORECASE))
    indicators.append(re.compile("button end",re.IGNORECASE))
    indicators.append(re.compile("adsense",re.IGNORECASE))
    indicators.append(re.compile("wordpress",re.IGNORECASE))
    indicators.append(re.compile("Category: News Tags:",re.IGNORECASE))
    indicators.append(re.compile("Related Posts ",re.IGNORECASE))
    indicators.append(re.compile("Subscribe to Hedge Fund Alpha",re.IGNORECASE))
    indicators.append(re.compile("Most Read Articles ",re.IGNORECASE))
    indicators.append(re.compile("Buy This Stock",re.IGNORECASE))
    indicators.append(re.compile("blog-subscribe",re.IGNORECASE))
    indicators.append(re.compile("take a report",re.IGNORECASE))
    indicators.append(re.compile("middle-col",re.IGNORECASE))
    indicators.append(re.compile("main-col",re.IGNORECASE))
    indicators.append(re.compile("terms of use",re.IGNORECASE))
    indicators.append(re.compile("site map",re.IGNORECASE))
    indicators.append(re.compile("text and design",re.IGNORECASE))
    indicators.append(re.compile("_qevents",re.IGNORECASE))
    indicators.append(re.compile("forum shortname",re.IGNORECASE))
    indicators.append(re.compile("nameofcookie",re.IGNORECASE))
    indicators.append(re.compile("&&",re.IGNORECASE))
    indicators.append(re.compile("else if",re.IGNORECASE))
    indicators.append(re.compile("google analytics",re.IGNORECASE))
    indicators.append(re.compile("seo pack",re.IGNORECASE))
    indicators.append(re.compile("semper fi web design",re.IGNORECASE))
    indicators.append(re.compile("start media suite utility bar",re.IGNORECASE))
    indicators.append(re.compile("hold to center",re.IGNORECASE))
    indicators.append(re.compile("margin-top",re.IGNORECASE))
    indicators.append(re.compile("!important",re.IGNORECASE))
    indicators.append(re.compile("nasdaq",re.IGNORECASE)) #need to be more lenient than > 1
    indicators.append(re.compile("{",re.IGNORECASE))
    indicators.append(re.compile("}",re.IGNORECASE))
    indicators.append(re.compile("#",re.IGNORECASE))
    indicators.append(re.compile("\|",re.IGNORECASE))
    indicators.append(re.compile("start of header",re.IGNORECASE))
    indicators.append(re.compile("netprnews",re.IGNORECASE))
    indicators.append(re.compile("super_search",re.IGNORECASE))
    indicators.append(re.compile("begin top",re.IGNORECASE))
    indicators.append(re.compile("end top",re.IGNORECASE))
    indicators.append(re.compile("html4",re.IGNORECASE))
    indicators.append(re.compile("html5",re.IGNORECASE))
    indicators.append(re.compile("nav fallback",re.IGNORECASE))
    indicators.append(re.compile("horizonatal",re.IGNORECASE)) #yes, really
    indicators.append(re.compile("div start",re.IGNORECASE))
    indicators.append(re.compile("home navigation",re.IGNORECASE))
    indicators.append(re.compile("hold the important links",re.IGNORECASE))
    indicators.append(re.compile("end of header",re.IGNORECASE))
    indicators.append(re.compile("press releases",re.IGNORECASE))
    indicators.append(re.compile("news pricing",re.IGNORECASE))
    indicators.append(re.compile("contact us",re.IGNORECASE))
    indicators.append(re.compile("order now",re.IGNORECASE))
    indicators.append(re.compile("start page wrapper",re.IGNORECASE))
    indicators.append(re.compile("site promo end",re.IGNORECASE))
    indicators.append(re.compile("press release display",re.IGNORECASE))
    indicators.append(re.compile(" arial[.,]? ", re.IGNORECASE)) 
    indicators.append(re.compile(" img ", re.IGNORECASE)) 
    indicators.append(re.compile(" attr ", re.IGNORECASE)) 
    indicators.append(re.compile(" li[.,]? ", re.IGNORECASE)) 
    indicators.append(re.compile(" ul[.,]? ", re.IGNORECASE)) 
    indicators.append(re.compile(" elem ", re.IGNORECASE)) 
    indicators.append(re.compile("hentry", re.IGNORECASE))
    indicators.append(re.compile("aspectratio", re.IGNORECASE)) 
    indicators.append(re.compile("helvetica", re.IGNORECASE)) 
    indicators.append(re.compile("jquery", re.IGNORECASE)) 
    indicators.append(re.compile("disqus", re.IGNORECASE)) 
    indicators.append(re.compile("getelementsbytagname", re.IGNORECASE)) 
    indicators.append(re.compile("wrapwidth", re.IGNORECASE)) 
    indicators.append(re.compile("origvideo", re.IGNORECASE)) 
    indicators.append(re.compile("weneca", re.IGNORECASE)) 
    indicators.append(re.compile("format-video", re.IGNORECASE)) 
    indicators.append(re.compile("valuewalk", re.IGNORECASE)) 
    indicators.append(re.compile("ui-tabs-panel", re.IGNORECASE)) 
    indicators.append(re.compile("ui-tabs-nav", re.IGNORECASE)) 
    indicators.append(re.compile("main-navigation", re.IGNORECASE)) 
    indicators.append(re.compile("sf-menu", re.IGNORECASE)) 
    indicators.append(re.compile("lost your password?", re.IGNORECASE)) 
    indicators.append(re.compile("bottom-widget", re.IGNORECASE)) 
    indicators.append(re.compile("attr\(", re.IGNORECASE)) 
    indicators.append(re.compile("scpt", re.IGNORECASE)) 
    indicators.append(re.compile("remember me", re.IGNORECASE)) #overkill, but ok, since such utterances are personal and therefore unimportant for a company's prospects.
    indicators.append(re.compile("send us your tips", re.IGNORECASE))
    indicators.append(re.compile("ajax", re.IGNORECASE)) # sports are unimportant
    indicators.append(re.compile("tweet more on this topic", re.IGNORECASE)) 
    indicators.append(re.compile("if sent email", re.IGNORECASE)) 
    indicators.append(re.compile("addcomment", re.IGNORECASE)) 
    indicators.append(re.compile("sendnotification", re.IGNORECASE)) 
    indicators.append(re.compile("return else", re.IGNORECASE)) 
    indicators.append(re.compile("sendnotification", re.IGNORECASE)) 
    indicators.append(re.compile("var", re.IGNORECASE)) 
    indicators.append(re.compile("login register", re.IGNORECASE)) 
    indicators.append(re.compile("if updated and cached", re.IGNORECASE)) 
    indicators.append(re.compile("all information is completely confidential", re.IGNORECASE)) 
    indicators.append(re.compile("side bar", re.IGNORECASE)) 
    indicators.append(re.compile("sidebar", re.IGNORECASE)) 
    indicators.append(re.compile("hosting and development by", re.IGNORECASE)) 
    indicators.append(re.compile("enter a valid email", re.IGNORECASE)) 
    indicators.append(re.compile("enter your email", re.IGNORECASE)) 
    indicators.append(re.compile("call to update facebook comment", re.IGNORECASE)) 
    indicators.append(re.compile("You can follow any responses to this entry through the RSS feed", re.IGNORECASE)) 
    indicators.append(re.compile("addedcomment", re.IGNORECASE)) 
    indicators.append(re.compile("caught added making", re.IGNORECASE)) 
    indicators.append(re.compile("leave comments leave a reply", re.IGNORECASE)) 
    indicators.append(re.compile("your email address will not be published", re.IGNORECASE)) 
    indicators.append(re.compile("cancel reply", re.IGNORECASE)) 
    indicators.append(re.compile("else failed to send email", re.IGNORECASE)) 
    indicators.append(re.compile("\.content", re.IGNORECASE)) 
    indicators.append(re.compile("\.tab", re.IGNORECASE)) 
    indicators.append(re.compile("\.wrap", re.IGNORECASE)) 
    indicators.append(re.compile("side-widget", re.IGNORECASE)) 
    indicators.append(re.compile("sfhover", re.IGNORECASE)) 
    indicators.append(re.compile("else failed to update facebook comment", re.IGNORECASE)) 
    indicators.append(re.compile("times new roman", re.IGNORECASE)) 
    indicators.append(re.compile("sub-navigation", re.IGNORECASE)) 
    indicators.append(re.compile("storycontent", re.IGNORECASE)) 
    indicators.append(re.compile("more-link", re.IGNORECASE)) 
    indicators.append(re.compile("using custom configuration items", re.IGNORECASE)) 
    indicators.append(re.compile("[prev|next] button key", re.IGNORECASE)) 
    indicators.append(re.compile("\"width\"", re.IGNORECASE)) 
    indicators.append(re.compile("\"height\"", re.IGNORECASE)) 
    indicators.append(re.compile("\"left\"", re.IGNORECASE)) 
    indicators.append(re.compile("\"right\"", re.IGNORECASE)) 
    indicators.append(re.compile("name \"description\" content", re.IGNORECASE)) 
    indicators.append(re.compile("scroll items", re.IGNORECASE)) 
    indicators.append(re.compile("statcounter", re.IGNORECASE)) 
    indicators.append(re.compile("bottomcontainerbox", re.IGNORECASE))
    indicators.append(re.compile("google analytics for wordpress", re.IGNORECASE))
    indicators.append(re.compile("name email website comment", re.IGNORECASE))
    indicators.append(re.compile("hello guest", re.IGNORECASE))
    indicators.append(re.compile("a password will be e-mailed to you", re.IGNORECASE))
    indicators.append(re.compile("charts signalling", re.IGNORECASE))
    indicators.append(re.compile("signalling for traders", re.IGNORECASE))
    indicators.append(re.compile("source: anotherwinningtrade", re.IGNORECASE))
    indicators.append(re.compile("permalink", re.IGNORECASE))
    indicators.append(re.compile("addthis button", re.IGNORECASE))
    indicators.append(re.compile("end end index", re.IGNORECASE))
    indicators.append(re.compile("side content", re.IGNORECASE))
    indicators.append(re.compile("promos", re.IGNORECASE))
    indicators.append(re.compile("contact information", re.IGNORECASE))
    indicators.append(re.compile("responsesource", re.IGNORECASE))
    indicators.append(re.compile("latest images", re.IGNORECASE))
    indicators.append(re.compile("latest video", re.IGNORECASE))
    indicators.append(re.compile("view our facebook profile", re.IGNORECASE))
    indicators.append(re.compile("page_wrapper", re.IGNORECASE))
    indicators.append(re.compile("footer", re.IGNORECASE))
    indicators.append(re.compile("header", re.IGNORECASE))
    indicators.append(re.compile("world vision", re.IGNORECASE))
    indicators.append(re.compile("if if", re.IGNORECASE))
    indicators.append(re.compile("sitemap", re.IGNORECASE))
    indicators.append(re.compile("copyright", re.IGNORECASE))
    indicators.append(re.compile("page generated by", re.IGNORECASE))
    indicators.append(re.compile("cached page", re.IGNORECASE))
    indicators.append(re.compile("wp cache ", re.IGNORECASE))

    ctr = 0
    for indicator in indicators:
        if re.search(indicator,sentence):
            # r = re.search(indicator,sentence)
            # print r.group(0)
            ctr = ctr + 1
            #print ctr

    if ctr > 1:
        return True
    else:
        return False




#you don't manage to remove words like 'get and "We. make sure you get words that have a quote at the beginning.


#eksempel paa skrot foer artikkel:
# html PUBLIC HTML Make That New Microsoft Corporation Retail Stores in - Insider gte IE gradient var document + function category action try category action label if ' + + ' ' s var js fjs if js 'script' var marginTop + + limit - - marginTop limit Hedge Funds Insider Trading Premium News Blog Log In Sign Up IMONKEY IMONKEY if 'ESC' login-screen signup-screen forgot-pass-screen index new account-actions closes nav-bar closes Main Education Center Data Screener Insider Purchases Insider Sales Browse Companies Main Education Center Browse Hedge Funds Best Performing Worst Performing ´ Newsletters My Subscriptions Main Hedge Funds Insider Trading Hedge Fund Analysis Stock Analysis We Disagree Lists Market Movers Predictions Dividend Stocks Authors var navigationMenu new Make That New Microsoft Corporation Retail Stores in By The Motley Fool in News February at pm End Text-Link ad tag AddThis Button BEGIN AddThis Button END Page of All closes single-post-title IMS

#eksempel paa skrot etter artikkel:
 # Page of All News Amazon Com Inc Inc Buy Co Inc Inc Corp Inc Corp Related Posts Microsoft Corporation Digs Deeper Into Retail More Microsoft Corporation Retail Stores on the Way Microsoft Corporation Surface Pro Sold Out Really Latest Tablet Shipment Report Shows Microsoft Corporation Needs Help Microsoft Corporation to Open Temporary Stores for Holiday Shopping Comments var replace example with your forum shortname var developer mode is on dsq + + Please enable JavaScript to view the comments powered by Disqus blog comments powered by Disqus closes post comments closes post closes blog-content container blog-middle-col if 'Premium - Sqr - 'View' '' Hedge Fund Resource Center Subscribe to Hedge Fund Alpha How to Beat the Market by Percentage Points Why Track Hedge Funds Download a Free Edition Why You Should DUMP Your Hedge Funds Most Read Articles Dump Your Hedge Funds and Buy This Stock Two Outstanding Dividend General Electric Company Siemens AG George Soros Doubling Down on Apple Inc Bullish on Big Citigroup Inc JPMorgan Chase & Co Will Windstream Corporation and Frontier Communications Corp Follow CenturyLink Inc Dividend Cut Schmidt Dumps Google Inc Stock Is It Still a Buy Can Following The Insiders Into VMware Inc and NewLink Genetics Corp Lead To Big Rewards Billionaire Hedge Funds Warren Buffett Berkshire Hathaway David Einhorn Greenlight Capital George Soros Soros Fund Management T Boone Pickens Bp Capital Jim Simons Renaissance Technologies Subscribe Enter your by FeedBurner Subscribe via RSS Click this link to view as XML closes blog-subscribe Blogroll Benzinga Qfinance Greg Speicher Take a Report Greenbackd SEC Whistleblower Advocate closes middle-col closes main-col Home Hedge Funds Insider Trading Blog Authors About Us Contact Us Privacy Policy Terms of Use Site Map All text and design is copyright InsiderMonkey LLC closes footer closes footer-container Quantcast Tag + var End Quantcast tag Cross Pixel Ad New var CONFIGURATION EDIT BEFORE PASTING INTO YOUR WEBPAGE var replace example with your forum shortname var ' developer mode is on DON'T EDIT BELOW THIS LINE + + Place this tag after the last button tag Investing Channel Tracker no-repeat IE function scrOfY number scrOfY else document document scrOfY else document document scrOfY return function var if begin if begin end document cookie indexOf( if end return return function ExpireDate new Date + NameOfCookie + + value + expires + + else var + - false if lastScreen if if var closes content Page served from cache in seconds


def junk(sentences):
    cleaned_sentences = []
    for sentence in sentences:

        tag = re.compile("<.*?>")
        sentence = re.sub(tag, "\n", sentence) # not "", since we still want a findable break.

        #should exclude 'word.<tag>' in addition to excluding 'word."'

        #sould get words lik this: $("object, with more than one non-letter

        boilerplate = re.compile("\S+([@$<>#%^&*{}\[\]\|](?!\")\S+)+") #any of these characters inside words
        sentence = re.sub(boilerplate, " ", sentence)

        boilerplate = re.compile("\S+[;():~`/_+=](?!\")\S+") #any of these characters inside words
        sentence = re.sub(boilerplate, " ", sentence)
        
        boilerplate = re.compile("\S+[0-9]\S+") #any of these characters inside words
        sentence = re.sub(boilerplate, " ", sentence)
        
        boilerplate = re.compile("[a-zA-Z]+\.[a-zA-Z]+ ") # U.S. and D.C., but not var.function
        sentence = re.sub(boilerplate, " ", sentence)
        
        #at beginning of words
        boilerplate = re.compile("\s+[@<>#%^&*{}\[\]\|]\S+") #any of these characters at beginning of word
        sentence = re.sub(boilerplate, " ", sentence)

        boilerplate = re.compile("\s+[;():~`/_+=]\S+") #any of these characters at beginning of word
        sentence = re.sub(boilerplate, " ", sentence)
        
        boilerplate = re.compile("\s+[0-9]\S+") #any of these characters at beginning of word
        sentence = re.sub(boilerplate, " ", sentence)
        
        #at end of words
        boilerplate = re.compile("\S+[@$<>#%^&*{}\[\]\|]\s+") #any of these characters at end of word
        sentence = re.sub(boilerplate, " ", sentence)

        boilerplate = re.compile("\S+[;():~`/_+=]\s+") #any of these characters at end of word
        sentence = re.sub(boilerplate, " ", sentence)

        boilerplate = re.compile("\S+[0-9]\s+") #any of these characters at end of word
        sentence = re.sub(boilerplate, " ", sentence)
        
        #alone
        boilerplate = re.compile("(?<=\s)[@$<>#%^{}\[\]\|]\s+") #any of these characters alone (overlapping)
        sentence = re.sub(boilerplate, " ", sentence)

        boilerplate = re.compile("(?<=\s)[;():~.`\"/_]\s+") #any of these characters alone (overlapping)
        sentence = re.sub(boilerplate, " ", sentence)

        dashes = re.compile("--+")
        sentence = re.sub(dashes," ",sentence)

        lineshift = re.compile("\n")
        sentence = re.sub(lineshift," ", sentence)

        too_much_whitespace = re.compile("\s\s+")
        sentence = re.sub(too_much_whitespace, " ", sentence)

        sentence = sentence.replace("="," ")
        sentence = sentence.replace("*"," ")

        # boilerplate words 
        word = re.compile(" arial[.,]? ", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile(" img ", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile(" attr ", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile(" li[.,]? ", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile(" ul[.,]? ", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile(" elem ", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)

        #without spaces:
        word = re.compile("hentry", re.IGNORECASE)
        sentence = re.sub(word, " ", sentence)
        word = re.compile("aspectratio", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("helvetica", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("wrapwidth", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("origvideo", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("weneca", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("format-video", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("valuewalk", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("ui-tabs-panel", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("ui-tabs-nav", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("main-navigation", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("sf-menu", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("lost your password?", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("bottom-widget", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("attr\(", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("scpt", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("remember me", re.IGNORECASE) #overkill, but ok, since such utterances are personal and therefore unimportant for a company's prospects.
        sentence = re.sub(word, " ", sentence)
        word = re.compile("send us your tips", re.IGNORECASE)
        sentence = re.sub(word, " ", sentence)
        word = re.compile("ajax", re.IGNORECASE) # sports are unimportant
        sentence = re.sub(word, " ", sentence)
        word = re.compile("tweet more on this topic", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("if sent email", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("addcomment", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("sendnotification", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("return else", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("sendnotification", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("return var", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("var po var", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("login register", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("if updated and cached", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("all information is completely confidential", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("side bar", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("sidebar", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("hosting and development by", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("var var", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("var email", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("enter a valid email", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("var data", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("enter your email", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("call to update facebook comment", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("You can follow any responses to this entry through the RSS feed", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("addedcomment", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("caught added making", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("leave comments leave a reply", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("your email address will not be published", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("cancel reply", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("var po", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("else failed to send email", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("\.content", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("\.tab", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("\.wrap", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("side-widget", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("sfhover", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("else failed to update facebook comment", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("times new roman", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("sub-navigation", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("storycontent", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("more-link", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("using custom configuration items", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("[prev|next] button key", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("\"width\"", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("\"height\"", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("\"left\"", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("\"right\"", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("name \"description\" content", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("scroll items", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("var title", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("statcounter", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("bottomcontainerbox", re.IGNORECASE)
        sentence = re.sub(word, " ", sentence)
        word = re.compile("google analytics for wordpress", re.IGNORECASE)
        sentence = re.sub(word, " ", sentence)
        word = re.compile("var ga", re.IGNORECASE)
        sentence = re.sub(word, " ", sentence)
        word = re.compile("var s", re.IGNORECASE)
        sentence = re.sub(word, " ", sentence)
        word = re.compile("name email website comment", re.IGNORECASE)
        sentence = re.sub(word, " ", sentence)
        word = re.compile("alt web var bsa", re.IGNORECASE)
        sentence = re.sub(word, " ", sentence)
        word = re.compile("hello guest", re.IGNORECASE)
        sentence = re.sub(word, " ", sentence)
        word = re.compile("a password will be e-mailed to you", re.IGNORECASE)
        sentence = re.sub(word, " ", sentence)

# » [if


            
#strip punctuation before it goes into crm. (so, store it with quotes and punct, but strip that when you fetch from db to put into crm. don't strip when you fetch to show on screen.

#removing words that contain :, ;, (), dot.notation, \, {, } etc, which are probably javascript or something.


        cleaned_sentences.append(sentence)

    return cleaned_sentences


#used before text is sent to crm
def strict(sentences):
    cleaned_sentences = []
    for sentence in sentences:

        sentence = sentence.replace("\""," ")
        #sentence = sentence.replace("'","") no, lots of problems with it's, 'fore, jesu', etc.


        sentence = sentence.replace("$"," ")

        punctuation = re.compile("[.!?;:,]")
        sentence = re.sub(punctuation, " ", sentence)

        numbers = re.compile("[0-9]")
        sentence = re.sub(numbers, " ", sentence)

        cleaned_sentences.append(sentence)

    return cleaned_sentences


#text = """html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"Microsoft Corporation (MSFT) To Pay $70 Million French Tax Adjustment #panel .content .right { width: 63%; } #body, #panel .content, .tab .wrap { width: 1044px; } #sidebar { width: 305px; } #sidebar .side-widget { width: 281px; } #maincontent, #premiumcontent { width: 659px; float: left; } body.home #maincontent { width: 659px; float: left; } body.home #premiumcontent { width: 659px; float: left; } body.fullwidth #maincontent { width: 1004px; float: left; } body.fullwidth #premiumcontent { width: 1004px; float: left; } #lowersection { width: 1004px; float: right;; margin: 1px 2% 0 2%;; } #leftposts { width: 100%; } #rightposts { width: -4%; } #leftline { background-position: 9999px 0; } #featured, #featured .ui-tabs-panel { width: 409px; } #featured ul.ui-tabs-nav { left: 409px; } #featured .ui-tabs-panel img { min-width: 409px; } #tabberota, #tabberota .ui-tabs-panel { width: 579px; } #tabberota ul.ui-tabs-nav { left: 579px; } #tabberota .ui-tabs-panel img { min-width: 579px; } #sliderota, #sliderota img,#scrollerota, #scrollerota ul.images li, #scrollerota ul.images li img { width: 659px; } .section1 .hentry { width: 30%; } .section1 .post2 { margin: 8px 5% 15px; } .section2 .hentry { width: 30%; } .section2 .post2 { margin: 8px 5% 15px; } body { color: #444444; font-size: 12px; line-height: 18px; font-family: Arial, Helvetica, sans-serif; } #body { background-color: #FFFFFF; } #header { background-color: #FFFFFF; } #title h1, #title h2 { font-size: 48px; line-height: 50px; font-family: Georgia, "Times New Roman", Times, serif;} h1, h1 a, h2, h2 a, h3, h3 a, h4, h4 a, h5, h5 a, h6, h6 a { color: #222222; } a { color: #205B87; } a:hover { color: #444444; } .main-navigation .sf-menu a, .main-navigation .sf-menu a:visited { color: #FFFFFF; } .main-navigation .sf-menu a:hover { color: #FFFFFF; } .main-navigation { background: #272727; font-size: 16px; font-family: Arial, Helvetica, sans-serif; } .main-navigation .sf-menu li.sfHover, .main-navigation .sf-menu li li, .main-navigation .sf-menu li li li, .main-navigation .sf-menu a:focus, .main-navigation .sf-menu a:hover { background: #666666; } .sub-navigation a { color: #222222; font-size: 12px; font-family: Arial, Helvetica, sans-serif; } .sub-navigation a:hover { color: #444444; } .side-widget { background-color: #F6F6F6; color: #444444; font-size: 12px; font-family: Arial, Helvetica, sans-serif; line-height: 14px; } .side-widget a, .bottom-widget a { color: #205B87; font-family: Arial, Helvetica, sans-serif; } .side-widget a:hover, .bottom-widget a:hover { color: #444444; } .side-widget h3, .bottom-widget h3 { font-size: 14px; line-height: 16px; font-family: Georgia, "Times New Roman", Times, serif; } .storycontent a.more-link { color: #FFFFFF; background-color: #AAAAAA; } .storycontent a:hover.more-link { color: #EEEEEE; background-color: #666666; } .hentry h1 { font-size: 28px; line-height: 30px; font-family: Georgia, "Times New Roman", Times, serif; } .hentry h2, .info h2 { font-size: 22px; line-height: 24px; font-family: Georgia, "Times New Roman", Times, serif; } ol.commentlist li.odd { background-color: #FFFFFF; } ol.commentlist li.even, #pagination { background-color: #F6F6F6; } h1.catheader { border-color: #222222; } #disqus_thread { clear:both; } a {color:#2964BF;} .index_top_featured_post_hd a { color: #000000; text-decoration: none; } .index_top_featured_post_hd a:hover { color: ##205B87; text-decoration: none; } .mc-field-group { margin-bottom: 20px; } #mc_embed_signup ul { list-style-type: none; padding-left: 0px; } #mc_embed_signup br { display:none; } #mc_embed_signup label { width: 160px; float:left; } .indicates-required { color: #f00; } [if IE]> /* */ All in one Favicon 4.2.1 Start of StatCounter Code var sc_project=5794736; var sc_invisible=1; var sc_security="b41137cb"; End of StatCounter Code Put the following javascript before the closing tag. (function() { var cx = '009788561534405790803:rmpwtadvvpg'; var gcse = document.createElement('script'); gcse.type = 'text/javascript'; gcse.async = true; gcse.src = (document.location.protocol == 'https:' ? 'https:' : 'http:') + '//www.google.com/cse/cse.js?cx=' + cx; var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(gcse, s); })(); function gotoSearch(theform) { var get_asset_id = document.getElementById('asset_class'); var asset = get_asset_id.options[get_asset_id.selectedIndex].value; var get_location_id = document.getElementById('location'); var location = get_location_id.options[get_location_id.selectedIndex].value; var get_no_of_analysts_id = document.getElementById('no_of_analysts'); var no_of_analysts = get_no_of_analysts_id.options[get_no_of_analysts_id.selectedIndex].value; var get_position_id = document.getElementById('position'); var position = get_position_id.options[get_position_id.selectedIndex].value; var get_returns_id = document.getElementById('returns'); var returns = get_returns_id.options[get_returns_id.selectedIndex].value; var get_sector_id = document.getElementById('sector'); var sector = get_sector_id.options[get_sector_id.selectedIndex].value; var get_search_text = document.getElementById('searchbox'); var search_text = get_search_text.value; if (sector == "none" && asset == "none" && returns == "none" && no_of_analysts == "none" && location == "none" && position == "none") { document.getElementById('error').innerHTML="Please choose one or more of the following: Asset Class, Location, No of Analysts, Position, Returns or Sector."; } else { var query = ""; var firstQueryTermPassedIn = false; if (search_text != "") { query += search_text; firstQueryTermPassedIn = true; } if (asset != "none") { if (firstQueryTermPassedIn) { query += "\+"; } query += "\"Asset:%20" +asset+"\""; firstQueryTermPassedIn = true; } if (location != "none") { if (firstQueryTermPassedIn) { query += "\+"; } query += "\"Location:%20" +location+"\""; firstQueryTermPassedIn = true; } if (no_of_analysts != "none") { if (firstQueryTermPassedIn) { query += "\+"; } query += "\"Analysts:%20" +no_of_analysts+"\""; firstQueryTermPassedIn = true; } if (position != "none") { if (firstQueryTermPassedIn) { query += "\+"; } query += "\"Position:%20" +position+"\""; firstQueryTermPassedIn = true; } if (returns != "none") { if (firstQueryTermPassedIn) { query += "\+"; } query += "\"Returns:%20" +returns+"\""; firstQueryTermPassedIn = true; } if (sector != "none") { if (firstQueryTermPassedIn) { query += "\+"; } query += "\"Sector:%20" +sector+"\""; firstQueryTermPassedIn = true; } theform.action = "http://www.valuewalk.com/stock-screener-results/?q="+query; return true; } return false; } End of code added by Srikant for Google Custom Search Random number generator to be placed in page header var ord = Math.random() * 10000000000000000 begin header All Breaking News in Business, Finance, Politics, Tech & Investing News Business News Tech News Political News Books Editors’ Full List of Book Recommendations Editors Favorite Ten Books Recommendations For Beginners Michael Burry’s List Tom Gayner’s List Donald Yacktman’s List Eddie Lampert’s List Bill Gates’ List Peter Cundill’s List John Griffin’s List Ray Dalio’s List Howard Marks’ List Charlie Munger’s List Bill Ackman’s List Dan Loeb’s List David Einhorn’s List Jamie Dimon’s List Joel Greenblatt’s List Guy Spier’s Reading List Seth Klarman’s List Warren Buffett’s List John Griffin’s List Value Investors Activist Investors Wilbur Ross Nelson Peltz Carl Icahn Dan Loeb Eddie Lampert Bill Ackman Current Value Investors Alan Howard Donald Yacktman George Soros Howard Marks David Tepper Francis Chou John Paulson Jim Chanos Tom Russo Robert Rodriguez Joel Greenblatt Michael Price David Einhorn Mason Hawkins Seth Klarman Charles Royce Bruce Greenwald Mario Gabelli Glenn Greenberg Kyle Bass Michael Burry Bruce Berkowitz James Montier Julian H. Robertson Jr. Legendary Value Investors Philip Fisher Bill Ruane Walter Schloss Thomas Rowe Price Jr. Chris Browne Benjamin Graham David Dreman Jesse Livermore John Neff Sir John Templeton Irving Kahn Peter Lynch Mohnish Pabrai Michael H. Steinhardt Foreign Investors Francisco García Paramés Jean-Marie Eveillard Chandrkant Sampat Dr Lee Shau-Kee Kerr Neilson Albert, Baron Frere Prince Alwaleed Bin Talal Alsaud Insurance Gurus Prem Watsa Warren Buffett Charlie Munger Tom Gayner Get Premium Access Screeners Valuation Stock Screener DCF Calculator Graham Formula Stock Screener Graham-Dodd Stock Screener Intrinsic Value Stock Screener Our Newsletter Premium Corner Premium Posts ValueWalk Stock Screener About About ValueWalk Authors About ValueWalk Corporation Advertise on ValueWalk Shorts Contact Timeless Reading Stock Watchlists Legal Disclaimer end header Prophecy Plat Prophecy Coal randomAd = function() { var ads = document.getElementsByClassName('ad'); var random = Math.floor(Math.random() * ads.length); var i = ads.length; while (i--) { ads[i].style.display = 'none'; } ads[random].style.display = 'block'; }(); Microsoft Corporation (MSFT) To Pay $70 Million French Tax Adjustment February 15, 2013By Michelle Jones Social Share French tax authorities will require Microsoft Corporation (MSFT) to pay $70 million in a tax adjustment. The company’s French subsidiary and its operations have been the topic of scrutiny by French tax officials for years. Social Sharing Toolkit v2.1.1 | http://www.active-bits.nl/support/social-sharing-toolkit/ TweetMicrosoft Corporation (NASDAQ:MSFT) will be required to pay a $70 million readjustment on its taxes in France, according to the French media outlet BFMTV. This is the third time in just five years the company’s French operations had to pay a tax readjustment. French tax authorities audited Microsoft Corporation (NASDAQ:MSFT) in 2010 in connection with the transfer prices between the company’s subsidiary in France and the parent company between the years of 2007 and 2009. BFMTV reports that the French subsidiary of Microsoft Corporation (NASDAQ:MSFT) works under a different subsidiary that’s based in Ireland. Whenever a Microsoft product is sold, the French subsidiary only covers a small part of the price, which is its commission on the sale of the product. The majority of the price of the product is redirected to Ireland. Quick Adsense WordPress Plugin: http://quicksense.net/ Tax officials in France have disputed the amount of the commissions Microsoft’s French subsidiary receives on sales. They also suspect that the subsidiary has a direct commercial presence in France. Officials raided Microsoft’s Paris office in 2012. Microsoft Corporation (NASDAQ:MSFT) said it is still disputing this most recent readjustment and that it expects to receive money back from an adjustment after the audit of a different fiscal year. This wouldn’t be the first time Microsoft got tax money back from French authorities. Between 1999 and 2011, French officials had to pay $32 million back to Microsoft, including the adjustment amount and interest. A number of other tech companies are on the hot seat in other parts of the world, especially the U.K., as governments in numerous countries begin to crack down on allegations of tax dodging. Trading on shares of Microsoft Corporation (NASDAQ:MSFT) is mostly flat in Friday afternoon trading at the NASDAQ. 'Get ValueWalk's Daily Edition By Email and Never Miss Our Top Stories' window._taboola = window._taboola || []; _taboola.push({article:"auto"}); _taboola.push({mode:"grid-4x2", container:"taboola-div"}); Tags: France, Microsoft, taxes Social Share This entry was posted on February 15, 2013 at 2:38 pm and is filed under Technology. You can follow any responses to this entry through the RSS 2.0 feed. #post Facebook Comments for WordPress v3.1.3 by we8u (http://we8u.com/facebook-comments/)"""

#text = """html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd" Microsoft Corporation (MSFT) Dealing with Tax Hike in France - Insider Monkey[if gte IE 9]> As one of the largest companies in the world, there is no denying the fact that Microsoft Corporation (NASDAQ:MSFT) pays a lot of money in taxes. With that being said, the company is getting ready to pay even more in France. According to a report by French TV channel BFM TV, Microsoft Corporation (NASDAQ:MSFT) is going to be faced with €52.5m added to its tax bill in France. ZDNet took a closer look at this story to better explain in English what is going on. “The reassessment relates to its 2007, 2008 and 2009 financial years, according to French TV channel BFM TV. It comes as a result of a tax audit in 2010 that looked into the fees paid by the local branch of the company to its main shareholder, Microsoft Ireland (Microsoft's European headquarters and main centre of business in the continent are located in Dublin).” Nobody likes to pay taxes. Even more so, nobody likes to pay more than they have to. This is magnified when dealing with a company that has revenue as large as Microsoft Corporation (NASDAQ:MSFT) . The article by ZDNet goes on to explain the company’s tax setup in France and why they will owe additional tax money: “In France, Microsoft acts as a 'commission agent' for Microsoft Ireland and gets a fee on every deal signed between the company and French customers. The French income tax department has looked into the amount of those fees, and now believes Microsoft owes an additional €52.5m in tax, BFM reports.” At this point, there is no word on when MSFT will have to pay the money. This is not the first time the company has dealt with a similar situation. In fact, in 2005 they successfully had a reassessment overturned. It is safe to say they are hoping for more of the same this time around. We will keep you updated on this story as more information becomes available. DISCLOSURE: I have no positions in any stock mentioned. For more Microsoft Corporation (NASDAQ:MSFT) news, visit these pages: Looking for Love in All the Wrong Places Surface Pro is Sold Out? Really? Surface Pro Dazzles Category: News Tags: Microsoft Corporation (MSFT),NASDAQ:MSFT Related Posts Get Ready for a Microsoft Corporation (MSFT) Windows 8 Price Hike Google Inc (GOOG), Apple Inc. (AAPL): Higher Digital Tax in France? Microsoft Corporation (MSFT) Ready to Invest in Brazil, TV Microsoft Corporation (MSFT) Surface RT Spreading the Love in Europe Microsoft Corporation (MSFT) Cuts Kinect Price, Adds Xbox Essentials Pack Comments var disqus_shortname = 'insidermonkeyblog'; // required: replace example with your forum shortname var disqus_developer = 0; // developer mode is on var disqus_identifier = '66757'; (function() { var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true; dsq.src = 'http://' + disqus_shortname + '.disqus.com/embed.js'; (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq); })(); Please enable JavaScript to view the comments powered by Disqus. blog comments powered by Disqus closes post comments closes post closes blog-content container blog-middle-col $(function () { if (typeof _gaq !== "undefined") { _gaq.push(['_trackEvent', 'Premium - Sqr - v1', 'View', '', 0, true]); } }); Hedge Fund Resource Center Subscribe to Hedge Fund Alpha How to Beat the Market by 20 Percentage Points Why Track Hedge Funds? Download a Free Edition! Why You Should DUMP Your Hedge Funds Most Read Articles Dump Your Hedge Funds and Buy This Stock Einhorn Loads Up on Apple Inc. (AAPL) Calls George Soros Doubling Down on Apple Inc. (AAPL), Bullish on Big Banks: Citigroup Inc. (C), JPMorgan Chase & Co (JPM) Will Windstream Corporation (WIN) and Frontier Communications Corp (FTR) Follow CenturyLink, Inc. (CTL)’s Dividend Cut? Here’s What Buffett’s Berkshire Hathaway Inc. (BRK.A) Has Been Buying and Selling Dump Your Hedge Funds and Buy This Stock Billionaire Hedge Funds Warren Buffett Berkshire Hathaway $75,326,633,000 David Einhorn Greenlight Capital $6,000,765,000 George Soros Soros Fund Management $9,266,419,000 T Boone Pickens Bp Capital $98,821,000 Jim Simons Renaissance Technologies $32,566,458,000 Subscribe Enter your email:Delivered by FeedBurner Subscribe via RSS Click this link to view as XML. closes blog-subscribe Blogroll Benzinga Qfinance Greg Speicher Take a Report Greenbackd SEC Whistleblower Advocate closes middle-col closes main-col Home Hedge Funds Insider Trading Blog Authors About Us Contact Us Privacy Policy Terms of Use Site Map All text and design is copyright ©2011 InsiderMonkey, LLC. All rights reserved. closes footer closes footer-container Quantcast Tag var _qevents = _qevents || []; (function() { var elem = document.createElement('script'); elem.src = (document.location.protocol == "https:" ? "https://secure" : "http://edge") + ".quantserve.com/quant.js"; elem.async = true; elem.type = "text/javascript"; var scpt = document.getElementsByTagName('script')[0]; scpt.parentNode.insertBefore(elem, scpt); })(); _qevents.push({ qacct:"p-87BdyAKNzkDAw" }); End Quantcast tag Cross Pixel Ad (function(){ var sNew = document.createElement("script"); sNew.defer = true; sNew.src = "http://tag.crsspxl.com/s1.js?d=819"; var s0 = document.getElementsByTagName('script')[0]; s0.parentNode.insertBefore(sNew, s0); })(); /* * * CONFIGURATION VARIABLES: EDIT BEFORE PASTING INTO YOUR WEBPAGE * * */ var disqus_shortname = 'insidermonkeyblog'; // required: replace example with your forum shortname var disqus_developer = ''; // developer mode is on /* * * DON'T EDIT BELOW THIS LINE * * */ (function () { var s = document.createElement('script'); s.async = true; s.type = 'text/javascript'; s.src = 'http://' + disqus_shortname + '.disqus.com/count.js'; (document.getElementsByTagName('HEAD')[0] || document.getElementsByTagName('BODY')[0]).appendChild(s); }()); Place this tag after the last +1 button tag. (function() { var po = document.createElement('script'); po.type = 'text/javascript'; po.async = true; po.src = 'https://apis.google.com/js/plusone.js'; var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(po, s); })(); Investing Channel Tracker icBeacon('insidermonkey'); .nrelate_flyout {display:block; right: -400px; bottom: 0px; width:360px;} #nrelate_flyout_open{display:block; right: -80px;bottom: 0px;} #nrelate_flyout_close{background: #fff url(http://www.insidermonkey.com/blog/wp-content/plugins/nrelate-flyout/images/close_window.gif) no-repeat 0 0} [if IE 6]> 0) { begin = document.cookie.indexOf(NameOfCookie+"="); if (begin != -1) { begin += NameOfCookie.length+1; end = document.cookie.indexOf(";", begin); if (end == -1) end = document.cookie.length; return unescape(document.cookie.substring(begin, end)); } } return "false"; } function nr_fo_set_closed_cookie(value,domain) { var NameOfCookie="nr_fo_closed"; var ExpireDate = new Date (); ExpireDate.setTime(ExpireDate.getTime() + (7*24*60*60*1000)); document.cookie = NameOfCookie + "=" + value + "; expires=" + ExpireDate.toGMTString()+"; path=/" + "; domain="+domain ; } value=nr_fo_get_closed_cookie(); if(value=="false") nr_fo_closed=false; else nr_fo_closed=true; var nr_fo_hidden = true; jQuery(function($){$(window).scroll(function() {var lastScreen;lastScreen = getScrollY() + $(window).height() < ($("#nr_fo_bot_of_post").offset().top) - ($("#nr_fo_top_of_post").offset().top) ? false : true;if (lastScreen && !nr_fo_closed && getScrollY()!=0 && nRelate.flyout_show) {$(".nrelate_flyout").stop().animate({"right":"0px"});nr_fo_hidden = false}else if (nr_fo_closed && lastScreen && getScrollY()!=0 && nRelate.flyout_show) {$("#nrelate_flyout_open").stop().animate({"right":"0px"});nr_fo_hidden=false;}else if (!nr_fo_hidden && !nr_fo_closed) {$(".nrelate_flyout").stop().animate({"right":"-400px"});nr_fo_hidden = true;}else if (!nr_fo_hidden && nr_fo_closed) {$("#nrelate_flyout_open").stop().animate({"right":"-80px"});nr_fo_hidden = true;}});$("#nrelate_flyout_close").live("click",function() { $(".nrelate_flyout").stop().animate({"right":"-400px"}); $("#nrelate_flyout_open").stop().animate({"right":"0px"}); nr_fo_closed = true; nr_fo_hidden = false; nr_fo_set_closed_cookie(true,"www.insidermonkey.com/blog");});$("#nrelate_flyout_open").live("click",function() { $("#nrelate_flyout_open").stop().animate({"right":"-80px"}); $(".nrelate_flyout").stop().animate({"right":"0px"});nr_fo_closed = false; nr_fo_hidden = false; nr_fo_set_closed_cookie(false,"www.insidermonkey.com/blog");});}); nRelate.domain = "www.insidermonkey.com%2Fblog"; var entity_decoded_nr_url = jQuery('"""



#text = """html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd" Microsoft Corporation (MSFT) Xbox Creator Talks the Potential for Apple Inc. (AAPL) TV Gaming - Insider Monkey[if gte IE 9]> Is it possible that Apple Inc. (NASDAQ:AAPL) could dive into the video gaming industry in the near future? While there are a lot of rumors floating around, one that you want to pay attention to is this: Apple may have an interest in bringing video games to its TV platform. For more information on how this would change the industry, this CNBC video is a great place to start. Apple Inc. (NASDAQ:AAPL) Press Info In the video, the host talks with Microsoft Corporation (NASDAQ:MSFT) Xbox creator Nat Brown. If anybody would have knowledge of the gaming industry, including a strong idea of what an entrance by Apple would mean, it is Brown. Getting started, the host asks Brown to explain how Apple Inc. (NASDAQ:AAPL) could possibly kill the competition when the company does not even have a presence in the industry at the current time. Here is what Brown had to say: “I started writing about this because I was very frustrated with what Microsoft has been doing with Xbox. Xbox has been stumbling, not letting independent developers create games, and also the user interface has become frustrating and slow and difficult to use for consumers.” According to Brown, if Xbox does not begin to perform better in these key areas it is a prime target for competitors such as Apple Inc. (NASDAQ:AAPL). He goes on to add the following: “Apple has really a great opportunity if they want to, to take the advantage that they have in simple user interface and great developers writing games, to come into this market.” The host then asks Brown if competitors should be anticipating “Apple coming in” and “how soon it will happen.” He provided this: “Apple will make a product when they are ready and when it is right, so you really can’t second guess that. It could really happen anytime. They have all the pieces in place to really build something that is very competitive in the console space.” So, what do you think about these comments by Nat Brown? Do you agree that Apple Inc. (NASDAQ:AAPL) may be getting into this space in the near future? DISCLOSURE: I have no positions in any stock mentioned. For more news stories, visit the following pages: Another Sign Apple Inc. is Moving Towards OLED Technology? Thieves Continue to Target Apple Inc. Stores Is Samsung Beating Apple Inc. in the Innovation Department? Category: News Tags: Apple Inc (AAPL),Microsoft Corporation (MSFT),NASDAQ:AAPL,NASDAQ:MSFT Related Posts Peter Misek Talks about Potential for Apple Inc. (AAPL) TV Microsoft Corporation (MSFT): Zune Out, Xbox Music In Microsoft Corporation (MSFT): Xbox Ad Breakthrough? Maynard Um Talks Potential for Apple Inc. (AAPL) Rebound Josh Brown of Fusion Analytics Talks About the Rise of Apple Inc. (AAPL) Shares Comments var disqus_shortname = 'insidermonkeyblog'; // required: replace example with your forum shortname var disqus_developer = 0; // developer mode is on var disqus_identifier = '67968'; (function() { var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true; dsq.src = 'http://' + disqus_shortname + '.disqus.com/embed.js'; (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq); })(); Please enable JavaScript to view the comments powered by Disqus. blog comments powered by Disqus closes post comments closes post closes blog-content container blog-middle-col $(function () { if (typeof _gaq !== "undefined") { _gaq.push(['_trackEvent', 'Premium - Sqr - v1', 'View', '', 0, true]); } }); Hedge Fund Resource Center Subscribe to Hedge Fund Alpha How to Beat the Market by 20 Percentage Points Why Track Hedge Funds? Download a Free Edition! Why You Should DUMP Your Hedge Funds Most Read Articles Dump Your Hedge Funds and Buy This Stock Einhorn Loads Up on Apple Inc. (AAPL) Calls George Soros Doubling Down on Apple Inc. (AAPL), Bullish on Big Banks: Citigroup Inc. (C), JPMorgan Chase & Co (JPM) Will Windstream Corporation (WIN) and Frontier Communications Corp (FTR) Follow CenturyLink, Inc. (CTL)’s Dividend Cut? Here’s What Buffett’s Berkshire Hathaway Inc. (BRK.A) Has Been Buying and Selling Dump Your Hedge Funds and Buy This Stock Billionaire Hedge Funds Warren Buffett Berkshire Hathaway $75,326,633,000 David Einhorn Greenlight Capital $6,000,765,000 George Soros Soros Fund Management $9,266,419,000 T Boone Pickens Bp Capital $98,821,000 Jim Simons Renaissance Technologies $32,566,458,000 Subscribe Enter your email:Delivered by FeedBurner Subscribe via RSS Click this link to view as XML. closes blog-subscribe Blogroll Benzinga Qfinance Greg Speicher Take a Report Greenbackd SEC Whistleblower Advocate closes middle-col closes main-col Home Hedge Funds Insider Trading Blog Authors About Us Contact Us Privacy Policy Terms of Use Site Map All text and design is copyright ©2011 InsiderMonkey, LLC. All rights reserved. closes footer closes footer-container Quantcast Tag var _qevents = _qevents || []; (function() { var elem = document.createElement('script'); elem.src = (document.location.protocol == "https:" ? "https://secure" : "http://edge") + ".quantserve.com/quant.js"; elem.async = true; elem.type = "text/javascript"; var scpt = document.getElementsByTagName('script')[0]; scpt.parentNode.insertBefore(elem, scpt); })(); _qevents.push({ qacct:"p-87BdyAKNzkDAw" }); End Quantcast tag Cross Pixel Ad (function(){ var sNew = document.createElement("script"); sNew.defer = true; sNew.src = "http://tag.crsspxl.com/s1.js?d=819"; var s0 = document.getElementsByTagName('script')[0]; s0.parentNode.insertBefore(sNew, s0); })(); /* * * CONFIGURATION VARIABLES: EDIT BEFORE PASTING INTO YOUR WEBPAGE * * */ var disqus_shortname = 'insidermonkeyblog'; // required: replace example with your forum shortname var disqus_developer = ''; // developer mode is on /* * * DON'T EDIT BELOW THIS LINE * * */ (function () { var s = document.createElement('script'); s.async = true; s.type = 'text/javascript'; s.src = 'http://' + disqus_shortname + '.disqus.com/count.js'; (document.getElementsByTagName('HEAD')[0] || document.getElementsByTagName('BODY')[0]).appendChild(s); }()); Place this tag after the last +1 button tag. (function() { var po = document.createElement('script'); po.type = 'text/javascript'; po.async = true; po.src = 'https://apis.google.com/js/plusone.js'; var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(po, s); })(); Investing Channel Tracker icBeacon('insidermonkey'); .nrelate_flyout {display:block; right: -400px; bottom: 0px; width:360px;} #nrelate_flyout_open{display:block; right: -80px;bottom: 0px;} #nrelate_flyout_close{background: #fff url(http://www.insidermonkey.com/blog/wp-content/plugins/nrelate-flyout/images/close_window.gif) no-repeat 0 0} [if IE 6]> 0) { begin = document.cookie.indexOf(NameOfCookie+"="); if (begin != -1) { begin += NameOfCookie.length+1; end = document.cookie.indexOf(";", begin); if (end == -1) end = document.cookie.length; return unescape(document.cookie.substring(begin, end)); } } return "false"; } function nr_fo_set_closed_cookie(value,domain) { var NameOfCookie="nr_fo_closed"; var ExpireDate = new Date (); ExpireDate.setTime(ExpireDate.getTime() + (7*24*60*60*1000)); document.cookie = NameOfCookie + "=" + value + "; expires=" + ExpireDate.toGMTString()+"; path=/" + "; domain="+domain ; } value=nr_fo_get_closed_cookie(); if(value=="false") nr_fo_closed=false; else nr_fo_closed=true; var nr_fo_hidden = true; jQuery(function($){$(window).scroll(function() {var lastScreen;lastScreen = getScrollY() + $(window).height() < ($("#nr_fo_bot_of_post").offset().top) - ($("#nr_fo_top_of_post").offset().top) ? false : true;if (lastScreen && !nr_fo_closed && getScrollY()!=0 && nRelate.flyout_show) {$(".nrelate_flyout").stop().animate({"right":"0px"});nr_fo_hidden = false}else if (nr_fo_closed && lastScreen && getScrollY()!=0 && nRelate.flyout_show) {$("#nrelate_flyout_open").stop().animate({"right":"0px"});nr_fo_hidden=false;}else if (!nr_fo_hidden && !nr_fo_closed) {$(".nrelate_flyout").stop().animate({"right":"-400px"});nr_fo_hidden = true;}else if (!nr_fo_hidden && nr_fo_closed) {$("#nrelate_flyout_open").stop().animate({"right":"-80px"});nr_fo_hidden = true;}});$("#nrelate_flyout_close").live("click",function() { $(".nrelate_flyout").stop().animate({"right":"-400px"}); $("#nrelate_flyout_open").stop().animate({"right":"0px"}); nr_fo_closed = true; nr_fo_hidden = false; nr_fo_set_closed_cookie(true,"www.insidermonkey.com/blog");});$("#nrelate_flyout_open").live("click",function() { $("#nrelate_flyout_open").stop().animate({"right":"-80px"}); $(".nrelate_flyout").stop().animate({"right":"0px"});nr_fo_closed = false; nr_fo_hidden = false; nr_fo_set_closed_cookie(false,"www.insidermonkey.com/blog");});}); nRelate.domain = "www.insidermonkey.com%2Fblog"; var entity_decoded_nr_url = jQuery('

#').html("http://api.nrelate.com/fow_wp/0.51.4/?tag=nrelate_flyout&keywords=Microsoft+Corporation+%28MSFT%29+Xbox+Creator+Talks+the+Potential+for+Apple+Inc.+%28AAPL%29+TV+Gaming&domain=www.insidermonkey.com%2Fblog&url=http%3A%2F%2Fwww.insidermonkey.com%2Fblog%2Fmicrosoft-corporation-msft-xbox-creator-talks-the-potential-for-apple-inc-aapl-tv-gaming-67968%2F&nr_div_number=1").text(); nRelate.getNrelatePosts(entity_decoded_nr_url); /*]]>*/ closes content Page served from cache in 0.00282096862793 seconds"""


# text =  """htmlStocks on Trader’s List: Netflix, Inc. (NASDAQ:NFLX) and Microsoft Corporation (NASDAQ:MSFT). | Net PR End Google Analytics All in One SEO Pack 1.6.13.8 by Michael Torbert of Semper Fi Web Design[135,248] /all in one seo pack html { margin-top: 0px !important; } * html body { margin-top: 0px !important; } START MEDIA SUITE UTILITY BAR hold to center February 18, 2013 How We WorkOrder NowSupport Privacy Contact end hold to center END START MEDIA SUITE UTILITY BAR start of HEADER Netprnews Distribution key utitilities area for switch lang and SUPER_SEARCH Begin Top Search Search End Top Search html5 semantic NAV fallback NAV div start horizonatal nav Home navigation to hold the important links Press Releases News Pricing Contact us Order Now end navigation to hold the important links end horizontal nav end of HEADER start page wrapper site promo end site promo START INDEX PRESS RELEASE DISPLAY Stocks on Trader’s List: Netflix, Inc. (NASDAQ:NFLX) and Microsoft Corporation (NASDAQ:MSFT). By anotherwinningtrade on 18/02/2013 Houston, TX – February18, 2013 — (Net PR News) – AnotherWinningTrade.com offers its daily alerts and market content newsletter to investors looking for the best information available! AnotherWinningTrade.com provides its subscribers with useful, timely information and exclusive alerts on penny stocks, mid cap stocks and large cap stocks with the potential to deliver gains of 100%-200% or more. We have the top alerts in the industry. To receive our FREE, comprehensive newsletter, visit AnotherWinningTrade.com. Today’s Stocks in focus are: NFLX, MSFT A famous Hedge-fund manager, Whitney Tilson, was advertising Netflix, Inc. (NASDAQ:NFLX)’s shares when they were trading a little higher than $50′s during October. The featured stock has grown almost three times over the span of the past few months. What Are NFLX’s Charts Signaling for Traders? Find Out Here Tilson still believes the company’s shares will grow rapidly in the near future. He added that the turnaround strategy served the company well and therefore, the company is going to reap notable gains in the very near future. Tilson went on to appreciate the contributions which were made by the company’s CEO, Reed Hastings, in guiding his company away from danger. According to Tilson, the CEO of the company did a very good job by ignoring the overwhelming level of criticism and sharp eyes of the people, who considered the company as a failure. Should NFLX be a Buy or Sell Now? Find Out Here Microsoft Corporation (NASDAQ:MSFT) cannot compete effectively with the likes of Apple Inc. (NASDAQ:AAPL) and Google Inc (NASDAQ:GOOG), while the company does not have an alternative strategy to win the growing number of customers in the industry. Can MSFT Show a Strong Recovery? Find out in This Research Report MSFT’s chief financial officer, Peter Klein, added that they are facing many difficulties in the industry, primarily because of the shrinking PC industry, which is causing the company to see a significant decline in sales and profitability. Klein identified the growing demand of smartphones and tablets as the most significant reason for declining sales in the PC market, during the annual Goldman Sachs Technology and Internet Conference in San Francisco, the Sydney Morning Herald reports. Where is MSFT Headed Exactly? Find out in This Trend Analysis Reports Disclaimer: Information, opinions and analysis contained herein are based on sources believed to be reliable, but no representation, expressed or implied, is made as to its accuracy, completeness or correctness. The opinions contained herein reflect our current judgment and are subject to change without notice. We accept no liability for any losses arising from an investor’s reliance on or use of this report. This report is for information purposes only, and is neither a solicitation to buy nor an offer to sell securities. A third party has hired and paid IO News Wire twelve hundred and ninety five dollars for the publication and circulation of this news release. Certain information included herein is forward-looking within the meaning of the Private Securities Litigation Reform Act of 1995, including, but not limited to, statements concerning manufacturing, marketing, growth, and expansion. Such forward-looking information involves important risks and uncertainties that could affect actual results and cause them to differ materially from expectations expressed herein. We have no ownership of equity, no representation; do no trading of any kind and send no faxes or emails. Source: anotherwinningtrade Posted Mon, February 18, 2013 13:22 - Permalink AddThis Button BEGIN AddThis Button END END INDEX PRESS RELEASE DISPLAY START INDEX SIDE CONTENT PROMOS Contact Information Ty Hoffer Email || Web || Rss

# Send a ResponseSource Media Enquiry
# END PROMOS LATEST IMAGES Submit Your Press Release END LATEST IMAGES LATEST VIDEO
# END LATEST VIDEO FACEBOOK LINK (EN ONLY)
# View our facebook profile
# END FACEBOOK LINK END INDEX SIDE CONTENT end of page_wrapper footer shadow end of footer shadow end of main start of footer proper World Vision 1162 Stratford Rd Hall Green, Birmingham West Midlands B28 8AF, UK Phone: 00 44 121 288 0751 © 2012 Net PR News. Support
# Sitemap
# Korean
# Chinese
# Privacy Policy How we works Terms of Service
# Follow Us:
# Facebook
# Twitter
# YouTube
# Blog
# International
# United States
# © Copyright 2002-2012. Net PR News. All Rights Reserved. end of footer var _gaq = _gaq || []; _gaq.push(['_setAccount', 'UA-35402920-1']); _gaq.push(['_trackPageview']); (function() { var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true; ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js'; var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s); })(); Dynamic page generated in 1.257 seconds. Cached page generated by WP-Super-Cache on 2013-02-18 13:27:03"""


# sentences = sentencify_dev_only(text)
# t = filter_sentences(sentences) #uses is_boilerplate 
# j = ' '.join(t)
# i = remove_outright(j) #is_boilerplate() is used by text(), which uses sentences as input


# print 'i: ',i




#def clean():
    # sentences = re.findall(sentence, text)
    # content = clean.filter_sentences(sentences)

    # text = ' '.join(content)
    # text = clean.remove_outright(text)
