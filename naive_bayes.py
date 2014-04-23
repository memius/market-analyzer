#!/usr/bin/python
# coding: utf-8

#should only be started by cron job, NOT by main. should fetch from, and return to, db.

import math, re, logging

logging.getLogger().setLevel(logging.DEBUG)

#counts the token frequency in one corpus, and stores all tokens, with their frequencies, in a dict:
# triple list example:
# [[["word", "pair"],["also", "pair"]],[["next", "one"],["also", "next"]]]
def count_tokens(word_pairs): # [['once','upon'],['once','a'], etc. ]
    frequencies = dict()
    if word_pairs != []:
#        logging.debug("word pairs: %s", word_pairs)
        pairs = [' '.join(pair) for sublist in word_pairs for pair in sublist] # each pair one string, triple list.
#        logger.debug('pairs: ',str(pairs))
        for pair in pairs:
#            logging.debug("pairs: %s", pairs)
            if pair in frequencies: 
                value = frequencies.get(pair)
                frequencies[pair] = value + 1
            else:
                frequencies[pair] = 1
    return frequencies


# pos = ["good","winning","up","rising","win","large"]
# neg = ["down","loss","warning","warns","deep","recession"]

#takes in both frequencies for ONE token, as well as both corpus
#sizes; it returns the probability that this token is positive.
# double list example:
# [["word","pair"],["also","pair"],["also", "pair"],["not","again"]]
def token_probability(pos_freq,neg_freq,pos_size,neg_size):
    if pos_freq > 5 and neg_freq < 1:
        prob = .99
    elif pos_freq < 1 and neg_freq > 5:
        prob = .01
    elif pos_freq > 5 and neg_freq > 5:
        pos_token_presence = min(1, (float(pos_freq) / pos_size))
        neg_token_presence = min(1, (float(neg_freq) / neg_size))
        tot_token_presence = pos_token_presence + neg_token_presence
        pos_prob = min(.99, (float(pos_token_presence) / tot_token_presence))
        prob = max(.01, pos_prob) # so it can never be 0
    else:  # if pos_freq < 1 and neg_freq < 1, so not in any corpus
        prob = 0.5

    return prob

#takes in a single article, and compares the words in it to the
#words in the two corpuses, returning the token probs for that
#article:
def token_probs(word_pairs,pos_freq,neg_freq,pos_size,neg_size):
    # logging.debug("word pairs in token probs: %s", word_pairs)
    token_probs = []
    if word_pairs != None:
        pairs = [' '.join(pair) for pair in word_pairs] # each word pair as one string from double list
        for pair in pairs:
            try:
                fp = pos_freq[pair] # correct also for titles, because pos_title_freqs is the argument
            except KeyError:
                fp = 0
            try:
                fn = neg_freq[pair]
            except KeyError:
                fn = 0

            token_prob = token_probability(fp,fn,pos_size,neg_size)
            token_probs.append(token_prob)

#    logging.debug("token probs: %s", token_probs)
    return token_probs

#takes in a bunch of token probs, and calculates a total prob of the text containing those tokens.
# abc / abc(a-1)(b-1)(c-1): 
def combined_prob(lst):
#    return 0.5 #debug only
    mult = reduce(lambda x, y: x*y, lst) # lst = [1,2,3,4] -> (((1*2)*3)*4) -> 24
    if mult == 0.0:
        mult = 0.1
    norms = map(lambda x: 1-x, lst)      # lst = [1,2,3,4] -> [0,1,2,3]
    norm = reduce(lambda x, y: x*y, norms)
    if norm == 0.0:
        norm = 0.1

    #try:
    result = mult / (mult + norm)
    # except:
    #     if mult == 0.0:
    #         result = 0.1 # this may be very wrong to do, but it fixes division by zero for now.
    #     elif norms == 0.0:
    #         result = 0.9
    #     else:
    #         result = 0.5

    # logging.debug("combined prob: %s", result)
    return result

# def text_prob(token_probs):
#     #this might be your best bet:
#     (let ((prod (apply function* probs)))
#      (/ prod (+ prod (apply function* (mapcar function(lambda (x)
#                                                                                (- 1 x))
#                                                    probs)))))
    
#     apply: applies function to elements in list
#     mapcar: apply function (lambda, etc) to each element in probs
#     lambda: applies the function (- 1 x) to the argument x.


#     for x in probs:
#         1 - x

#     #bayes says: the combined prob of a, b, and c is (a*b*c) / (a*b*c
#     #+ (1 - a)(1 - b)(1 - c))

#     # thinkbayes says: after we count the frequencies of the words, we
#     # can compute probs by dividing through with the total number of
#     # words. this is because the frequencies are proportional to the
#     # probs. this is just to calculate the probability that a word
#     # occurs in a text, though, not the prob that it belogongs to a
#     # category.
#     pass

# h = prob of hypothesis before data - in this case 0.5 that the article is neg. the prior.
# d = new data coming in, and updating the probs. probs of tokens.
# p(h|d) is the prob of h after we have seen the data. this is what we want to compute. the posterior.
# p(d|h) is the prob of the data under the h, the likelihood.
# p(d) is prob of data under any h, the normalizing constant.


# #should take in the probabilities of all the tokens in a text, and return a verdict.
# def verdict(token_probs):
#     # use count tokens to get the frequencies of each word in both corpuses. keep this around.
#     # which corpus a text belongs to should simply be a tag in the value list for that article. or a field of the object.
#     # find corpus sizes
#     #both these can be derived from the db itself, through calculation.

#     # use the pos/neg frequencies for each word in the text, along with the corpus sizes, to determine the total probability for a text.
#     pass







# #takes in two corpuses, gets the frequency of each token in them, and returns the probabilities for each token.
# def something(pos,neg): #pos and neg being the corpuses, not the word lists
#     npos = length(pos)
#     nneg = length(neg)
#     fp = count_tokens(pos)
#     fn = count_tokens(neg)
#     pos_probs = []
#     neg_probs = []
#     for pair in fp:
#         pprob = find_probability(fp,fn,npos,nneg)
#         pos_probs.append(pprob)
        
#     for pair in fn:
#         nprob = find_probability(fp,fn,npos,nneg)
#         neg_probs.append(nprob)

#     for each word in both lists; if the probability is higher than .9, put the word in the pos list, and vice versa.
        
    


#     fn = frequency of token in the neg corpus
# fp = frequency of token in the pos corpus
# nneg = number of neg articles
# npos = number of pos articles



# # #debug only:
# text = "There were n0 c1ouds ;n th.e sky th(a)t particular .eVen|ng neither. Also, .40 thomas@gmail.com large alien craft hovered over the landscapezzz. Well, this! Busy me! Said whom? For this; whom else were here? Well: him!"

# count_tokens(text)

















# one corpus of positive, one of negative. never mind neutral. get them from google finance.

# make sure they are the same size.

# each corpus is one large text file. tokenize the text file with [[:graph:]], 
# or rather, the python equivalent, which is \s or something like that.

# ignore html comments.

# count frequency of each token in each corpus. don't double frequency
# in one, since they are equally important, and ffalse positives are
# dangerous both ways.

# compute probability of neg/pos: if token is only seen in one corpus, then its prob. is .01 or .99.

# otherwise, compute like this:

#if frequency of word in pos + freq. of word in neg < 5, don't do anything.

# max(.01 (min(.99 (min(1 (b / nbad) / (min(1 (g / ngood) + min(1 (b / nbad)))))))

# max(.01 


# (let ((g (* 2 (or (gethash word good) 0)))
#       (b (or (gethash word bad) 0)))
#    (unless (< (+ g b) 5)
#      (max .01
#           (min .99 (float (/ (min 1 (/ b nbad))
#                              (+ (min 1 (/ g ngood))   
#                                 (min 1 (/ b nbad)))))))))


