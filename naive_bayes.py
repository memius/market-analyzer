#!/usr/bin/python
# coding: utf-8

import math, re

# will have a (small) corpus of positive and negative articles. you count the words in them.
# you use these frequencies, as well as the sizes of the corpuses, to determine the bayesian probability that the word is negative. you will also put words into, and remove words from, two lists of positive and negative words. this list will be updated each time trained.

#counts the token frequency in one corpus, and stores all tokens, with their frequencies, in a dict:
def count_tokens(text):
    #non-whitespace characters followed by a space, period, question mark or exclamation mark:
    token = re.compile("[^\.,\?!;:]\S+?(?= |\.|,|\?|!|;|:)") 
    #token = re.compile("\w+") not satisfactory
    tokens = re.findall(token,text)
    frequencies = dict()
    for word in tokens:
        word = word.strip()
        #ignore case
        #print "|"+word+"|",
        if word in frequencies:
            value = frequencies.get(word)
            #print 'incrementing\n'
            frequencies[word] = value+1
        else:
            #print 'new word\n'
            frequencies[word] = 1

    #print 'frequencies: ',frequencies
    return frequencies

# pos = ["good","winning","up","rising","win","large"]
# neg = ["down","loss","warning","warns","deep","recession"]

#takes in both frequencies for ONE token, as well as both corpus
#sizes; it returns the probability that this token is negative.
def token_probability(freq_pos,freq_neg,size_pos,size_neg):
    if freq_neg > 1 or freq_pos > 1: 
        neg_token_presence = min(1, (float(freq_neg) / size_neg))
        pos_token_presence = min(1, (float(freq_pos) / size_pos))
        tot_token_presence = neg_token_presence + pos_token_presence
        neg_prob = min(.99, (float(neg_token_presence) / tot_token_presence))
        prob = max(.01, neg_prob)
    else:
        prob = 0.4
    return prob

#takes in a single article, and compares the words in it to the
#words in the two corpuses, returning the token probs for that
#article:
def token_probs(text,freq_pos,freq_neg,size_pos,size_neg):

    word = re.compile("[^\.,\?!;:]\S+?(?= |\.|,|\?|!|;|:)")  #duplicated from count_tokens()
    words = re.findall(word,text)

    token_probs = []
    for word in words:
        word = word.strip() #duplicated from count_tokens()
        #print "|"+word+"|",

        try:
            fp = freq_pos[word] 
            #print "positive: ",fp
        except KeyError:
            fp = 0
            #print fp,

        try:
            fn = freq_neg[word]
            #print "negative: ",fn
        except KeyError:
            fn = 0
            #print fn,

        token_prob = token_probability(fp,fn,size_pos,size_neg)
        token_probs.append(token_prob)

    #print token_probs
    return token_probs #and then you need to do abc / abc(a-1)(b-1)(c-1) to that result.

#takes in a bunch of token probs, and calculates a total prob of the text countaining those tokens.
def combined_prob(lst):
    mult = reduce(lambda x, y: x*y, lst)
    norms = map(lambda x: 1-x, lst)
    norms = reduce(lambda x, y: x*y, norms)
    result = mult / (mult + norms)
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


