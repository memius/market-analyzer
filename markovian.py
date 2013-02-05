#like this:
#for current_word in line.split():

#not like this:
# for line in file:
#     words = line.split(" ")


#he uses file paths to his own machine. i will use the text that comes in directly. at the bottom is the call, with his file paths. substitute your own call, which calls it with the article from your db.

from __future__ import with_statement
import random
 
def create_chain(file_paths):
    markov_chain = {}
    word1 = "\n"
    word2 = "\n"
    for path in file_paths:
        with open(path) as file:
            for line in file:
                for current_word in line.split():
                    if current_word != "":
                        markov_chain.setdefault((word1, word2), []).append(current_word)
                        word1 = word2
                        word2 = current_word
    return markov_chain
 
def construct_sentence(markov_chain, word_count=30):
    generated_sentence = ""
    word_tuple = random.choice(markov_chain.keys())
    w1 = word_tuple[0]
    w2 = word_tuple[1]
    
    for i in xrange(word_count):
        #"total count" is a special key used to track word frequency.
        newword = random.choice(markov_chain[(w1, w2)])
        generated_sentence = generated_sentence + " " + newword
        w1 = w2
        w2 = newword
        
    return generated_sentence
 
markov = create_chain(
                      (
                       "/users/darkxanthos/documents/workspace/markovchain/src/documents/shanechat.txt",
                       "/users/darkxanthos/documents/workspace/markovchain/src/documents/bible.txt",
                       "/users/darkxanthos/documents/workspace/markovchain/src/documents/arabiannights.txt",
                       "/users/darkxanthos/documents/workspace/markovchain/src/documents/alice.txt",
                       "/users/darkxanthos/documents/workspace/markovchain/src/documents/taoteching.txt",
                       "/users/darkxanthos/documents/workspace/markovchain/src/documents/communist_manifesto.txt",
                       "/users/darkxanthos/documents/workspace/markovchain/src/documents/portrait.txt",
                       "/users/darkxanthos/documents/workspace/markovchain/src/documents/ulysses.txt",
                       "/users/darkxanthos/documents/workspace/markovchain/src/documents/dubliners.txt",
                       ))
#print markov
print construct_sentence(markov_chain = markov, word_count=100)


# from __future__ import with_statement
# import random
 
# def create_chain(file_paths):
#     word_counter = {}
#     previous_word = ""
#     for path in file_paths:
#         with open(path) as file:
#             for line in file:
#                 words = line.split(" ")
                
#                 for word in words:
#                     if word != "":
#                         word = word.lower()
#                         if previous_word not in word_counter:
#                             word_counter[previous_word] = {"total count":0}
                        
#                         if word not in word_counter[previous_word]:
#                             word_counter[previous_word][word] = 0
#                         word_counter[previous_word][word] = word_counter[previous_word][word] + 1
#                         word_counter[previous_word]["total count"] = word_counter[previous_word]["total count"] + 1
#                         previous_word = word.lower()
#     return word_counter
 
# def construct_sentence(markov_chain, word_count=300,initial_word=""):
#     generated_sentence = ""
#     initial_word = initial_word.lower()
    
    
#     for i in range(1,word_count):
#         updated = False
#         while initial_word not in markov_chain:
#             initial_word = markov_chain[markov_chain.keys()[random.randrange(0,length(markov_chain))]]
#         #assign a probability to all of the possible
#         #successive words
        
#         #choose a random number between 1 and the total number of words
#         word_index_to_use = random.randrange(1, markov_chain[initial_word]["total count"]+1)
#         index_count = 0
#         #Count thru the occurences until u reach the destination word
#         for next_word in markov_chain[initial_word]:
#             #"total count" is a special key used to track word frequency.
#             if next_word != "total count":
#                 if word_index_to_use in range(index_count, index_count + markov_chain[initial_word][next_word]+1) or markov_chain[initial_word]["total count"] == 1:
#                     if generated_sentence == "":
#                         generated_sentence = generated_sentence + " " + initial_word + " " + next_word
#                     else:
#                         generated_sentence = generated_sentence + " " + next_word
                        
#                     if next_word not in markov_chain:
#                         next_word = markov_chain[markov_chain.keys()[random.randrange(0,length(markov_chain))]]
                        
#                     initial_word = next_word
#                     break
#                 else:
#                     index_count = index_count + markov_chain[initial_word][next_word]
#     return generated_sentence
 
# markov = create_chain(
#                       (
#                        "/users/darkxanthos/documents/workspace/markovchain/src/documents/bible.txt",
#                        "/users/darkxanthos/documents/workspace/markovchain/src/documents/arabiannights.txt",
#                        "/users/darkxanthos/documents/workspace/markovchain/src/documents/alice.txt",
#                        "/users/darkxanthos/documents/workspace/markovchain/src/documents/taoteching.txt",
#                        "/users/darkxanthos/documents/workspace/markovchain/src/documents/communist_manifesto.txt",
#                        "/users/darkxanthos/documents/workspace/markovchain/src/documents/portrait.txt",
#                        "/users/darkxanthos/documents/workspace/markovchain/src/documents/ulysses.txt",
#                        "/users/darkxanthos/documents/workspace/markovchain/src/documents/dubliners.txt"))
# #print markov
# print construct_sentence(markov_chain = markov, initial_word = "i", word_count=300)
