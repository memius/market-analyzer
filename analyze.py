#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-

import utils, naive_bayes

from google.appengine.api import memcache

from models import Article

# naar hvert selskap faar noen hundre artikler kan man begynne aa beregne
# probs paa kun selskapets artikler - da vil antakelig accuracyen gaa
# opp. nye selskaper, og selskper med faa artikler kan bruke hele
# korpusen som grunnlag. dette loeses vha. en enkel sjekk i begynnelsen
# av analyze, som ser paa stoerrelsen av det spesifikke korpuset.
def sentiment(article_object):

# 1 artikkel inn:

# for hvert ordpar i artikkelen, lagre til db, med dupe check (bruk memcache for recent word pairs, akkurat som i scrape).

# hvert token skal ha en prob, og et ordpar (som foreløpig bare inneholder ett ord).

# eller, ord-kvintupler (windows), der du lagrer ord 1, 2, 3, 4, 5 og 6, og så henter du dem ut i form av ordpar når du trenger det. ta med ord 6 også.

# se i teab etter formelen for å legge til verdier uten å hente fram alle de gamle (du ganger med et eller annet, som gjør de nye verdiene mer verdt, som igjen, implisitt gjør de gamle verdiene mindre verdt.)

# da kan du slippe å hente dem fram mange ganger.

# smoothing factor = 2.0 / (periods + 1.0), where periods is perhaps wordpairs? or articles?
# any value 0.0-1.0 can be used. closer to 1.0 means less smooth, and more weight on recent values. value 1.0 == the most recent value.

# formula for ema:

# ema-today = ema-yesterday + smoothing-factor(price-today - ema-yesterday)

# so:

# smoothing factor = 2.0 / (number of word pairs (or articles?) + 1.0) denne kommer til å være veldig nær 0 ganske fort. kanskje gjøre 2.0 større? 20, eller til og med 100? men, må den ikke egentlig være 1.0, siden 2.0 kan gi større verdier enn 1? hm.

# current prob for this word pair = previous prob + smoothing factor * (the latest human-defined prob minus (or plus, if 0) prev prob)

# the latest human-defined prob will always be 1 or 0, so that can possibly be simplified?


# so:

# we get in an article. it is not seen by humans. we do NOT calculate, but analyze based on stored probs. for each word pair in the article, fetch that word pair, if existant, from db, and multiply their probs together. final prob -> conclusion.

# we get a human-defined sentiment for an article. THIS is when we calculate new prob. we take all the word pairs in that article, and compare their positive probs (1.0 or 0.0) with their stored probs.

# token-objektet må holde rede på hvor mange positive artikler og hvor mange negative artikler som inneholder ordparet. dette er grunnlaget for smoothing faktoren. nei - hvor mange positive brukerinputs, og hvor mange negative brukerinputs! nei, bare brukerinputs - uvesentlig hva de var.

# først: prob == 0.5
# 1 pos: prob == 1.0:  1/1: 1 av 1 er pos: 0.5  -> 1.0:  0 tidl, 1 pos
# 2 neg: prob == 0.5:  1/2: 1 av 2 er pos: 1.0  -> 0.5:  1 tidl, 1 neg
# 3 neg: prob == 0.33: 1/3: 2 av 3 er pos: 0.5  -> 0.33: 2 tidl, 1 neg
# 4 pos: prob == 0.5:  4/2: 2 av 4 er pos: 0.33 -> 0.5:  3 tidl, 1 pos
# 5 pos: prob == 0.66: 3/5: 3 av 5 er pos: 0.5  -> 0.66: 4 tidl, 1 pos

# du får ikke en nøyaktig verdi, men en smoothed average.

# prob = incoming * (tidl - 1.0)


# inc(oming) = 1.0 (pos)
# tidl = 0 (ganger): 0, 1, 2, 3, 4, osv.
# prev = 0.5 (prob)
# smo = 1.0 / (tidl + 1.0): 1.0, 0.5, 0.33, 0.25, osv.
#                           2.0, 1.0, 0.66, osv.



# DETTE ser korrekt ut (og erik eikeland har verifisert det):
# smo = 1.0 / (tidl + 1.0) # antall tidligere korreksjoner (det er dette som må vektes; manuelt vs. automatisk)
# prob = prev + smo * (inc - prev)

# altså; vi lagrer prev og tidl til db. vi får inn inc. regner ut derfra.
# dette gjør vi på hvert ordpar i artikkelen vi har fått inn, uten å hente hele artikler fra db. vi henter ordpar fra db, dersom de eksisterer. hvis ikke lagrer vi ordparet til db med inc som prob, og 1 som tidl.

# når dette er gjort går vi gjennom alle ordpar-prob'ene, og regner ut total prob for artikkelen, og lagrer dette til db.

# er dette også veldig ineffektivt? jeg henter jo enorme mengder ordpar fra db...' bruk memcache - lagre ordparene i memcache, se etter dem der, og hvis de ikke er der, hent dem fra db vha. 'name', som er ord 1? nei, du må hente vha. hele ordparet. dammit.



    
    values = memcache.get("values")
    if values: 
        [text, pos_freq, neg_freq, pos_size, neg_size, \
                                    title, pos_title_freq, neg_title_freq, pos_title_size, neg_title_size] = values
    else:


# hente article keys her?
        q = Article.all()
        q.order("datetime")
        article_objects = q.fetch(10000)
        

    # finding sizes and frequencies:
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

        memcache.add("values", [text, pos_freq, neg_freq, pos_size, neg_size, \
                                    title, pos_title_freq, neg_title_freq, pos_title_size, neg_title_size], 11000)

# ----------------------

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

    article_object.analyzed = True
    article_object.put()


def all_sentiment(): 



#LES DETTE: after you analyze them, check the length of dupe check. if > 1000, halve the length (or, rather, reduce length to 300). this happens after analyze, which is the last one.






#fetch the clean but non-analyzed ones from db, and everything else from memcache.

    # q = Article.all()
    # q.order("datetime")

    # article_cursor = memcache.get("analyze_article_cursor")

    # if article_cursor:
    #     q.with_cursor(start_cursor = article_cursor)

    # chunk_size = 30
    # articles = q.fetch(chunk_size)

    article_keys = memcache.get("article_keys")
    if article_keys:
        for article_key in article_keys: # this must be sharded!
            article = Article.get_by_id(article_key.id()) 

    # for article in articles: 
            # if article and 
            if article.clean and article.sentiment == None: # not just article.ANALYZED == None, because you need to get those who 'have been analyzed', but don't have a sentiment even so.
                sentiment(article) #,articles)
#                article_keys.remove(article_key)

        memcache.set("article_keys", article_keys, 11000)
    # else: # if no memcache
    #     q = Article.all().filter("clean =", True)
    #     articles = q.fetch(1)
    #     for article in articles:
    #         sentiment(article)


        

    # if len(articles) < chunk_size:
    #     memcache.delete("analyze_article_cursor")

    # else:
    #     article_cursor = q.cursor()
    #     memcache.set("analyze_article_cursor", article_cursor, 11000)


