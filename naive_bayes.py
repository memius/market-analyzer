#!/usr/bin/python
# coding: utf-8

import math, re



def count_tokens(text):
    #non-whitespace characters followed by a space, period, question mark or exclamation mark:
    #now, it captures '' as well, which it shouldn't.
    token = re.compile("\S*?(?= |\.|\?|!)") 
    tokens = re.findall(token,text)
    d = dict()
    for word in tokens:
        print word
        if word in d:
            value = d.get(word)
            d[word] = value+1
        else:
            d[word] = 1

    print d

    #use python dict, which is a hash table
    #put the tokens in as keys, and let the value be the frequency

def find_probability(token):
#     fn = frequency of token in the neg corpus
# fp = frequency of token in the pos corpus
# nneg = number of neg articles
# npos = number of pos articles

# if fn > 1 or fp > 1: 
#     neg_token_presence = min(1 / (fn / nneg))
#     pos_token_presence = min(1 / (fp / npos))
#     tot_token_presence = neg_token_presence + pos_token_presence
#     neg_prob = min(.99 neg_token_presence / tot_token_presence)
#     prob = max(.01 neg_prob)
#     return prob
    pass



text = "There were n0 c1ouds ;n th.e sky th(a)t particular ..::-- eVen|ng neither. Also, thomas@gmail.com large alien craft hovered over the landscapezzz. Busy me! Said whom?"

count_tokens(text)










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


