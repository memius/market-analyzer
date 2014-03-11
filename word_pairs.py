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

#du vil bare bruke de 15 beste, så derfor regner du ikke sammen
#underveis, men putter i liste, og kjører bayes() på listen til slutt.

# ikke bruk memcache, bare få det til å virke, slik det gjorde, bare
# sakte. bedre hvis du kan, med slices og andretriks.

# mulig dict er enda bedre enn list når du har en 3d struktur med
# probs til hvert ordpar.  hvert ord skal bare lagres en gang som
# first, så det andre ordet i ordparet er en av en rekke ord som
# kommer etter first-ordet. probs er da en tredje dimensjon som ligger
# bakenfor hvert av second-ordene.

# skal de puttes inn kronoligisk eller alfabetisk eller etter prob? antakelig etter prob.

from google.appengine.api import memcache

## from google.appengine.ext import db

#import numpy as np

from models import Article, Word_pair



def word_pairs():
    article_keys = memcache.get("article_keys")
    if article_keys:
        for key in article_keys: #[:2]: #testing ONLY! ordinarily the whole list
            article = Article.get_by_id(key.id())
            if article != None:
                if article.clean:
                    text = article.text
                    words = text.split() # split strips white space implicitly

 #                   words = np.array(words) # a 1d array

                    num_of_word_pairs = (len(words) * 5) - 10
                    unseen_word_pairs = []
#                    running_total = 0.5
                    for n in range(3): #len(words) - 5): testing ONLY!
                        window = words[-6:] # the last six words in the text
                        one = window[:2]
                        two = window[:1] + window[2:3]
                        three = window[:1] + window[3:4]
                        four = window[:1] + window[4:5]
                        five = window[:1] + window[5:6] # all windows are complete, since we go backwards

#                    pairs = memcache.get("most_interesting_pairs") #a 2d array containing first, second, prob
                    # ctr = 1 # naar ctr ruller, saa ruller første ord, og andre ord blir satt tilbake.

                    # i = 0
                    # j = 2
                    # k = 1

                    # x = 0
                    # y = 2
                    # z = 3

#                     for n in range(n):


# # np.any(np.equal(a,[1,2]).all(1)) ?

# # du er her: nei, du skal ikke sammenligne med ETT par fra memcache - du skal sjekke om ordparet dit is in memcache:
# #                        any(np.equal(a,[1,2]).all(1))
#                         if any(np.equal(pairs, words[i,j,k]).all(1)):

# string comparison is not implemented in numpy arrays. maybe you have to translate to utf-8 bytes? oh, the horror.

# np.char.strip(words)

# i may actually want a dict for the strings with their probs. dammit. numpy arrays aren't meant for ' strings, since, they are not of the same length.

# probably, holding the most interesting ones in memory can save me a lot of time. try just that.

# where does that list get compiled and stored? in cleanup? not here, so wait; don't use it here until it exists.

# #                        if (words[i,j,k] == pairs[x,y]).all():
#                             prob = pairs[y,z]
#                             running_total = bayes(prob,running_total)

#                         else: #wait until article finished, then whatever.
#                             unseen_pairs.append(words[i,j,k])

#                     ctr += 1
#                     i,j,k += 1 
#                     x,y,z += 3



# keep the 5000 most interesting and frequent words in memory. kanskje i final cleanup, eller i en egen fil.

# compare equality with slices:
# 1d array of words from article:
# one = a[:2]
# two = a[0:3:2]
# three = a[0:4:3]
# four = a[0:5:4]
# etc.
# 2d array of word pairs from memcache. (with probs)
# einz = b[0:2]
# zwei = b[3:5]
# drei = b[6:8]
# etc.

# have a final cleanup file, that takes care of storing stuff to db. perhaps also storing the most used to memcache (but this is not changed after word_pairs.py, so somewhere else). this is after word pair has completed. word pairs should be quick and simple, and only quickly deliver a classification of the articles at hand, without any thinking or calculation (other than straight up combined prob). no fetching from, or storing to, db in word_pairs.py.


# paul graham:
# only consider words with frequency > 5
# if a word occurs only in one corpus, assign .01 or .99.
# use number of articles rather than total (word) length of corpus.
# the 15 most interesting tokens in each article is used (farthest from .5).
# words you have never seen before are ignored.
# combined prob:

# prob a and prob b:

# ab / (ab + (1 - a)(1 - b))

# example: .60 and .72:

# (.6)(.72) / ((.6)(.72) + (1 - .6)(1 - .72))

# so:

# r = running_total
# p = wp.prob
# running_total = (r * p) / ((r * p) ((1 - r) * (1 - p)))


                        probs = []
                        for word_pair in [one,two,three,four,five]:
                            q = Word_pair.all().filter("first =", word_pair[0]) # dict fra memcache er muligens mye bedre her.
                            wp = q.filter("second =",word_pair[1]).get()

                            if wp == None:
                                unseen_word_pairs.append(word_pair)
                            else:
                                if wp.prob > 0.9 or wp.prob < 0.1:
                                    probs.append(wp.prob) 
# z = np.zeros(16)
# t = z.reshape((4,4))
# p = t + 0.5 # gir en 4*4 array der alle verdiene == 0.5
# a = np.average(p)
    
# DU ER HER - putt tallene i en numpy array, og gjør average under, bare for å teste at numpy funker. sjekk online også.
  #                              running_total = running_total + wp.prob
                                    #foo.append(wp.prob)
# you'll want ' to keep the x most used word pairs in memcache, and refer to them. their probs don't ' change unless the size of the corpus changes noticeably, or there is a correction involving them. keep incrementing their frequencies whenever they are encountered, and then check to see if the frequency relative to the size of the corpus changes by more than, say, 10%.
                        words.pop() # removes the last word

#                    running_total = running_total / num_of_word_pairs
#                    bar = np.array(foo)
#                    r = float(np.average(bar))
                    combined_prob = bayes(probs)
                    article.prob = combined_prob
                    article.put()

                    # move this to final cleanup.
                    for word_pair in unseen_word_pairs: # commented out ONLY for testing!
                        wp = Word_pair()
                        wp.first = word_pair[0]
                        wp.second = word_pair[1]
                        wp.prob = combined_prob # the word pair is simply given the article's prob
                        wp.corrections = 0
                        wp.put()
# word pairs må fjerne article keys fra article_keys etterhvert som den blir ferdig med dem. dette for å unngå at den analyserer artikler om og om igjen. word pairs gjør det siden den er sist i rekken. 


def bayes(probs):
    # map to list:
    # grahams ab 1-b, etc.
    running_total = 0.5 # ONLY testing
    return running_total
    


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

#text = "once upon a time in the deep, dark forest, there lived a terrible witch."
#test(text)



# -hent inn en artikkel.
# -lag ordpar av artikkelen.
#  -putt alle ordene i artikkelen i en liste
#  -sjekk om ordet er et ord? regex for å finne ord? hent liste fra /usr/share/dict/american-english og ~british.
#  -slice de seks siste ordene
#   -lag ordpar av disse seks.
#  -hiv det siste ordet.
#  -pop det syvende ordet, og du har en ny gruppe på seks.
# -hent probs fra db for hvert ordpar dersom ordparet eksisterer i db.
# -lagre ordparet til db dersom ikke finnes. prob = 0.5.
# -dette gir den automatisk kategoriserte sentimenten.

# -vi får inn en manuell korreksjon:
# -dette oppdaterer probs for ordparene i den artikkelen.
# -ordparene får inn 0.0 eller 1.0 alt etter hva denne artikkelen er.
# -dette smoothes mot tidligere prob.
# -antall manuelle korreksjoner er viktig.
# -sentimenten i de manuelle korreskjonene er viktig, men kan leses av current prob?
# -antall ganger ordparet opptrer i interessante (> 0.9 eller < 0.1) artikler er viktig. med andre ord: hvor betydningsfullt er dette ordparet - er det "is the" eller er det "catastrophic loss"? her er det du vekter i forhold til tidligere manuelle korreksjoner.


# det under ser korrekt ut. før du kommer dit: putt alle ordene i artikkleen i en liste. ta de fem første ordene. trekk ut alle ordparene, og lagre til db, med prob. pop hodet (reverse eller noe, da?) av listen, og gjenta.


# du trenger 2 forskjellige vektinger for hvor mange ganger artikkelen har blitt kategorisert; 1 for manuelt kategoriserte, og en (f.x. 1/10 av den andre) for automatisk kategorisert. disse brukes til å vekte hvor viktig prev prob er i forhold til incoming prob fra bruker/automasjon. lag en teller, og inkrementer den med f.eks. 1 for hver gang et menneske kategoriserer, og 0.1 for hver gang systemet kategoriserer.

# denne vektingen brukes for å fortelle hvor mange ganger ordparet har blitt brukt (i artikler som har blitt kategorisert). eh? poenget med denne todelte vektingen er ...


# i tillegg til disse to vektingene, bruker du smoothing factor til å vekte siste manuelle korrigering mot alle de tidligere.


# dersom ordparet opptrer i svært mange artikler er det viktigere enn dersom det er sjeldent (så lenge det ikke er nøytralt).

# dersom ordparet har en prob som er langt unna 0.5 er det også viktigere. in fact, så kan du ignorere alle ordpar som har en prob mellom f.eks. 0.2 og 0.8.







# dette ble hentet ut av recover file analyze.py: du har lest gjennom det.

# 1 artikkel inn:

# for hvert ordpar i artikkelen, lagre til db, med dupe check (bruk memcache for recent word pairs, akkurat som i scrape).

# hvert token skal ha en prob, og et ordpar (som foreløpig bare inneholder ett ord).

# eller, ord-kvintupler (windows), der du lagrer ord 1, 2, 3, 4, 5 og 6, og så henter du dem ut i form av ordpar når du trenger det. ta med ord 6 også. nei, lagre hvert ordpar for seg - eller i alle fall hver enkelt prob!


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








# ------------


# that's because you need to store total frequency and positive frequency of that word pair:'
# prob of pos given "it is" = (pos freq of "it is" * ratio of pos vs. neg) / total freq of "it is"
# wp = "it is"
# pos = positive
# p(wp|pos) = (p(pos|wp) * p(pos)) / p(wp)

# so you need to store pos freq and tot freq for each word pair, and you need to keep track of the ratio - keep in memory? memcache? you also need the size of pos corpus and total corpus - in order to get the actual prob of wp given pos corpus. dammit.

# you need to count how many times a user has corrected, and measure his accuracy.

# every time a correction comes, all the word pairs in that article must be updated.

# maybe you dont need to take into account the frequencies right here (for unseen words) and now, but you might be able to let that slide (and just use the article's ' prob) until there is an actual correction, at which time the prob for the word pair is updated. it is, of course, also updated when new articles containing that unseen word are analyzed (NO - it isn't'!). this way, you get a very fast and efficient automatic classifier, which doesn't ' have to actualy calculate anything using lots of variables.

# so then you're back to ' adding word pair probs to each other.

# (0.5 + 0.5 + 0.5) / 3 = 0.5

# (0.5 + 0.5 + 1.0) / 3 = 0.66


# so you simply want the average! hah! easy. DU ER HER!


                        # else: no, you don't know that after a single word pair!
                        #     article.prob = 0.5 # there are no interesting word pairs in it.
