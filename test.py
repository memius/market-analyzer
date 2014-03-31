#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-


# see if this works without any more configuration. you probably have to define a task queue request first, though. or maybe a call to _ah_start or whatever it was from cron will do the trick?

# it has to be a dynamic backend, because only they can be started by a http request. residents must be started manually.


# from models import Article

# # this is for testing backends. put something in the db, say a new
# # company. if that works, update every ten minutes or so, to change
# # the company entry. if that works, you can try to start scrape.py
# # this way - or one of the others, if that doesn't work on the first
# # try.
# def test():
#     # # create a new company, then update it, then do scrape/dupes/clean or analyze.
#     # company = Company()
#     # company.name = "Advanced Micro Devices, Inc"
#     # company.name_lower = "advanced micro devices, inc"
#     # company.ticker = "AMD"
#     # company.ticker_lower = "amd"
#     # company.exchange = "NYSE"
#     # company.put()

#     # company = Company()
#     # company.name = "Goldman Sachs Group Inc"
#     # company.name_lower = "goldman sachs group inc"
#     # company.ticker = "GS"
#     # company.ticker_lower = "gs"
#     # company.exchange = "NYSE"
#     # company.put()

#     q = Article.all()
#     q.order("datetime")
#     articles = q.fetch(1)

#     for article in articles:
#         article.title_sentiment = "foobar"
#         article.put()




def bayes(probs):
    total = .5

    for prob in probs: # maybe use map
        total = (total * prob) / ((total * prob) + ((1 - total) * (1 - prob)))
        print total

    return total


#probs = [0.5, 0.7, 0.8, 0.2, 0.9, 0.1]
#bayes(probs)







def word_pairs(text):
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
            for word_pair in [one,two,three,four,five]:
                word_pairs.append(word_pair)

            words.pop() # removes the last word

    else:
        word_pairs = []

    return word_pairs

def count_tokens(word_pairs): # [['once','upon'],['once','a'], etc. ]
    frequencies = dict()
    if word_pairs != []:
        for pair in word_pairs:
            p = [pair if isinstance(pair, str) else ' '.join(s) for s in pair] 
            s = ' '.join(p) 
            if s in frequencies: 
                value = frequencies.get(s)
                frequencies[s] = value+1
            else:
                frequencies[s] = 1
    return frequencies

def token_probs(word_pairs,pos_freq,neg_freq,pos_size,neg_size):
    for pair in word_pairs:
        p = [pair if isinstance(pair, str) else ' '.join(s) for s in pair] 
        s = ' '.join(p) 
        try:
            fp = pos_freq[p] # it's correct also for titles, because pos_title_freqs is the argument
        except KeyError:
            fp = 0
        try:
            fn = neg_freq[p]
        except KeyError:
            fn = 0
        token_prob = token_probability(fp,fn,pos_size,neg_size)
        token_probs.append(token_prob)
    return token_probs


# pos1 = "once upon a time, there lived a terrible witch in the huge, dark, forest in the middle of the carpathians. she was so evil that even animals shunned the area around her house. however, this was in an evil world, so she was really a good witch, and it was good that the evil animals shunned her and her house. this gave her the freedom to work in peace, to construct machines that would liberate everyone on the planet."

# pos2 = ""

# pos3 = ""

# neg1 = ""

# neg2 = ""

# neg3 = ""

# pos_corp = []
# neg_corp = []
# for text in [pos1,pos2,pos3]:
#     wp = word_pairs(text)
#     pos_corp.append(text)
# for text in [neg1,neg2,neg3]:
#     wp = word_pairs(text)
#     neg_corp.append(text)

# pos_freq = count_tokens(pos_corp) #triple list (list of lists of strings) this is probabl where the problem lies.
# neg_freq = count_tokens(neg_corp)

# probs = token_probs(wp,freq)

# for pair in positive_corpus:
#     p = [word for sublist in positive_corpus for word in sublist]
#     s = ' '.join(p)

# you need to flatten once, to get a single list of lists of word pairs. then, you need to join the word pairs, and flatten again, to get a list of word pair strings.
