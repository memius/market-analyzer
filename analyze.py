#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-

import utils, naive_bayes

from google.appengine.api import memcache

from models import Article

def sentiment(article_object, article_objects):

# naar hvert selskap faar noen hundre artikler kan man begynne aa beregne
# probs paa kun selskapets artikler - da vil antakelig accuracyen gaa
# opp. nye selskaper, og selskper med faa artikler kan bruke hele
# korpusen som grunnlag. dette loeses vha. en enkel sjekk i begynnelsen
# av analyze, som ser paa stoerrelsen av det spesifikke korpuset.

    # finding sizes and frequincies:
    positive_article_texts = [""]
    negative_article_texts = [""]

    pos_titles = [""]
    neg_titles = [""]

    # if article_objects = []:
    #     article_objects = Article.all() 

    for article in article_objects:
        sentiment = article.sentiment

        if sentiment == "positive":
            positive_article_texts.append(article.text)
        elif sentiment == "negative":
            negative_article_texts.append(article.text)

        title_sentiment = article.title_sentiment

        if title_sentiment == "positive":
            pos_titles.append(article.title)
        elif title_sentiment == "negative":
            neg_titles.append(article.title)

    pos_size = len(positive_article_texts)
    neg_size = len(negative_article_texts)

    pos_title_size = len(pos_titles)
    neg_title_size = len(neg_titles)


    # finding token frequencies for the whole corpus:
    pos_text = ' '.join(map(unicode, positive_article_texts)) # possibly undesirable hack
    neg_text = ' '.join(map(unicode, negative_article_texts))

    pos_title = ' '.join(map(unicode, pos_titles))
    neg_title = ' '.join(map(unicode, neg_titles))
        
    pos_freq = naive_bayes.count_tokens(pos_text)
    neg_freq = naive_bayes.count_tokens(neg_text)

    pos_title_freq = naive_bayes.count_tokens(pos_title)
    neg_title_freq = naive_bayes.count_tokens(neg_title)

    # finding sentiment for one incoming article:
    # norm = article_object.normalized
    text = utils.string_normalize(article_object.text)
    title = utils.string_normalize(article_object.title)

    # it seems you only use token_probs from here:
    # words, token_probs, word_pos_freqs, word_neg_freqs = naive_bayes.token_probs(text,pos_freq,neg_freq,pos_size,neg_size)
    token_probs = naive_bayes.token_probs(text,pos_freq,neg_freq,pos_size,neg_size)
    title_token_probs = naive_bayes.token_probs(title,pos_title_freq,neg_title_freq,pos_title_size,neg_title_size)

    prob = naive_bayes.combined_prob(token_probs)
    title_prob = naive_bayes.combined_prob(title_token_probs)

    if article_object.mod != None: # this just changes the conclusion - it does not teach the bayes anything until later, when the article is part of a different corpus.
        prob = min(.99, prob + article_object.mod) # from the user's button click - see CorrectionHandler
        prob = max(.01, prob)
        title_prob = min(.99, title_prob + article_object.mod)
        title_prob = max(.01, title_prob)

    article_object.prob = prob
    if prob >= 0.9:
        article_object.sentiment = "positive"
    elif prob <= 0.1:
        article_object.sentiment = "negative"
    else:
        article_object.sentiment = "neutral"

    article_object.title_prob = title_prob
    if title_prob >= 0.9:
        article_object.title_sentiment = "positive"
    elif title_prob <= 0.1:
        article_object.title_sentiment = "negative"
    else:
        article_object.title_sentiment = "neutral"
    
    article_object.put()


def all_sentiment(): 

#fetch the clean but non-analyzed ones from db, and everything else from memcache.

    q = Article.all()
    q.order("datetime")

    article_cursor = memcache.get("analyze_article_cursor")

    if article_cursor:
        q.with_cursor(start_cursor = article_cursor)

    chunk_size = 30
    articles = q.fetch(chunk_size)

    for article in articles: 
        if article.clean:
            sentiment(article,articles)

    if len(articles) < chunk_size:
        memcache.delete("analyze_article_cursor")

    else:
        article_cursor = q.cursor()
        memcache.set("analyze_article_cursor", article_cursor)


 # companies = memcache.get("companies")
 #   if not companies:
 #      companies = Company.all()
 #      memcache.add("companies",companies,30) # n = seconds


    # articles = Article.all() # filter on clean, of course! don't fetch everything!
    # for article in articles:
    #     if article.clean: # must be clean to get at cleaned text
    #         sentiment(article, articles)






#         pos_freq = naive_bayes.count_tokens(pos_text)
#         neut_freq = naive_bayes.count_tokens(neut_text)
#         neg_freq = naive_bayes.count_tokens(neg_text)
#         words, token_probs, word_pos_freqs, word_neg_freqs = naive_bayes.token_probs(norm,pos_freq,neg_freq,pos_size,neg_size)

#         article_prob = naive_bayes.combined_prob(token_probs)


#         pos_freq = naive_bayes.count_tokens(pos_text)
# #        neut_freq = naive_bayes.count_tokens(neut_text)
#         neg_freq = naive_bayes.count_tokens(neg_text)
#         words, token_probs, word_pos_freqs, word_neg_freqs = naive_bayes.token_probs(norm,pos_freq,neg_freq,pos_size,neg_size)
#         article_prob = naive_bayes.combined_prob(token_probs)






# +    #     if article.content in duplicates: # probably never hits, because text is cleaned before new ones come in.
# -#     prob = db.FloatProperty()
# -#     prob = db.FloatProperty()
#      prob = db.FloatProperty()
#      prob = db.FloatProperty()
# @@ -86,7 +86,7 @@ def token_probs(text,pos_freq,neg_freq,pos_size,neg_size):
#      #print token_probs
#      return words, token_probs, word_pos_freqs, word_neg_freqs #and then you need to do abc / abc(a-1)(b-1)(c-1) to that result. (done in combined_prob).
# -#takes in a bunch of token probs, and calculates a total prob of the text countaining those tokens.
# +#takes in a bunch of token probs, and calculates a total prob of the text containing those tokens.
#  def combined_prob(lst):
# -#     prob = db.FloatProperty()
# -#     prob = db.FloatProperty()
# +#                continue # with company loop - NO! this probably continues the links loop!
# +this will reduce the number of requests a lot. you can probably do the
# -locally. (prob. same reason as above).
# +det er ogsaa mulig at problemet er saa enkelt som andre linje i








# dc8e41e330cedc329cf279a439011754c2d5307f

# 94b66bc48d0ac4334f6f8f708cab39c3c325da97


# 906dc74a0cde2486863507c95682b8f9ac82db90




# 28025894a60df8e97e6079b4826e60588d054299

# f8d0688ddcd56b21772bc8261d77f5bbada9b3f6




# df0faad85c5ddad0562f8b9b16c15b91d24114eb

# e698092368b48bd3df15f1f57a7668d1ef8e2a58

# a88a52af63b7bd776d5bdbe9938201b419ac08fb

# 36ee74c3b95797f0aa9a8c69d1389d75868b20a0
