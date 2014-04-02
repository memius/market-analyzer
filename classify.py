#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-


# extract word pairs from article. done
# look up their counterparts in db.
# collect probs from db for each word pair.
# update frequencies in db (do this later, gather in list? what is faster?). probably store later, in final cleanup.
# put unseen word pairs in unseen list.
# combine probs to yeld article prob. graham.
#
# store unseen word pairs with prob 0.5 if article == neutral, 0.01 if
# article == neg and .99 if pos, and increment frequencies for the
# ones already there.

# how about using map() for this? will it be more efficient? 

#du vil antakelig bruke lister, og slices for å adressere de riktige
#bitene av listen for å få ordpar. akkurat som i numpy, bare at her
#kan du sammenligne for equality.

# mulig dict er enda bedre enn list når du har en 3d struktur med
# probs til hvert ordpar.  hvert ord skal bare lagres en gang som
# first, så det andre ordet i ordparet er en av en rekke ord som
# kommer etter first-ordet. probs er da en tredje dimensjon som ligger
# bakenfor hvert av second-ordene.

# skal de puttes inn kronoligisk eller alfabetisk eller etter prob? antakelig etter prob.

import logging, math

from google.appengine.api import memcache

## from google.appengine.ext import db

from models import Article, Word_pair

logging.getLogger().setLevel(logging.DEBUG)

def recent_word_pairs():
    article_keys = memcache.get("article_keys")
    wp = []
    if article_keys:
        for key in article_keys: 
            article = Article.get_by_id(key.id())
            if article != None:
                if article.clean:
                    text = article.text # later, you'll want to do this with titles as well, and see if equally good.
                    if text != None:
                        wp.append(word_pairs(text))

        return wp


def word_pairs(text):
    # titles are often shorter than six words, so this will return empty list for those. fix.
    if text != None:
        words = text.split() # split strips white space implicitly
        num_of_word_pairs = (len(words) * 5) - 10
        word_pairs = []
        for n in range(len(words) - 5): 
            window = words[-6:] # the last six words in the text
            one = window[:2]
            two = window[:1] + window[2:3]
            three = window[:1] + window[3:4]
            four = window[:1] + window[4:5]
            five = window[:1] + window[5:6] # all windows are complete, since we go backwards

# i may actually want a dict for storing the strings with their probs in memcache. 

# have a final cleanup file, that takes care of storing stuff to db. perhaps also storing the most used to memcache (but this is not changed after word_pairs.py, so somewhere else). this is after word pair has completed. word pairs should be quick and simple, and only quickly deliver a classification of the articles at hand, without any thinking or calculation (other than straight up combined prob). no fetching from, or storing to, db in word_pairs.py. final cleanup må også fjerne keys fra article keys etterhvert, slik at word pair ikke klassifiserer de samme artiklene igjen og igjen.

# paul graham:
# only consider words with frequency > 5
# if a word occurs only in one corpus, assign .01 or .99.
# use number of articles rather than total (word) length of corpus.
# the 15 (no, 20) most interesting tokens in each article is used (farthest from .5).
# words you have never seen before are ignored.
# combined prob:

# r = running_total
# p = wp.prob
# running_total = (r * p) / ((r * p) ((1 - r) * (1 - p)))


            for word_pair in [one,two,three,four,five]:
                word_pairs.append(word_pair)

            words.pop() # removes the last word

        return word_pairs




def classify(word_pairs):
    probs = []
    unseen_word_pairs = []

    if word_pairs != [] and isinstance(word_pairs[0], str):
        pairs = [' '.join(pair) for pair in word_pairs]
        for word_pair in pairs:
            # logging.debug("word_pair: %s", word_pair)
            wp = Word_pair.all().filter("words =", word_pair).get() # dict fra memcache er muligens mye bedre her.
            # logging.debug("wp: %s", wp)

            if wp == None:
                unseen_pairs.append(word_pair)
            else:
                if wp.prob > 0.9 or wp.prob < 0.1:
                    probs.append(wp.prob) 

        article.prob = bayes(probs)
        article.put()

        store_unseen_pairs(unseen_pairs, combined_prob)


def store_unseen_pairs(unseen_pairs, combined_prob):
    # move this to final cleanup.
    for word_pair in unseen_word_pairs: # commented out ONLY for testing!
        wp = Word_pair()
        wp.first = word_pair[0]
        wp.second = word_pair[1]
        wp.prob = combined_prob # the word pair is simply given the article's prob
        wp.corrections = 0
        wp.put()


def bayes(probs):
    total = .5

    probs = interesting(probs)

    for prob in probs:
        total = (total * prob) / ((total * prob) + ((1 - total) * (1 - prob)))

    return total

def interesting(probs): # returns the 20 most interesting probabilities
    results = []
    for prob in probs: 
        distance = math.fabs(0.5 - prob) # distance from 0.5
        results.append((distance,prob)) # tuple, immutable
        results.sort()
        results.reverse() # largest distance first
    
    if len(results) > 20:
        results = results[:20]

    interesting_probs = [tupl[1] for tupl in results] 

    return interesting_probs


def test(text):
    words = text.split()
    print "words:", words
    for n in range(len(words) - 5):
        window = words[-6:] # the last six words in the text
        print "window:", window
        one = window[:2]
        two = window[:1] + window[2:3]
        three = window[:1] + window[3:4]
        four = window[:1] + window[4:5]
        five = window[:1] + window[5:6]
        print "one:",one
        print "two:", two
        print "three:", three
        print "four:", four
        print "five:", five
        words.pop()



