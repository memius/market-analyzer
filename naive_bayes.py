#!/usr/bin/python
# coding: utf-8

import math

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


def find_prob(token):
fn = frequency of token in the neg corpus
fp = frequency of token in the pos corpus
nneg = number of neg articles
npos = number of pos articles

if fn + fp > 6: # probably an unecessary filter
    neg_token_presence = min(1 / (fn / nneg))
    pos_token_presence = min(1 / (fp / npos))
    tot_token_presence = neg_token_presence + pos_token_presence
    neg_prob = min(.99 neg_token_presence / tot_token_presence)
    prob = max(.01 neg_prob)
    return prob

# max(.01 (min(.99 (min(1 (b / nbad) / (min(1 (g / ngood) + min(1 (b / nbad)))))))

# max(.01 


# (let ((g (* 2 (or (gethash word good) 0)))
#       (b (or (gethash word bad) 0)))
#    (unless (< (+ g b) 5)
#      (max .01
#           (min .99 (float (/ (min 1 (/ b nbad))
#                              (+ (min 1 (/ g ngood))   
#                                 (min 1 (/ b nbad)))))))))


