import re, string



def junk(sentences):
    cleaned_sentences = []
    for sentence in sentences:

        tag = re.compile("<.*?>")
        sentence = re.sub(tag, "\n", sentence) # not "", since we still want a findable break.

        boilerplate = re.compile("\S+[@$<>#%^&*{}\[\]\|]\S+") #any of these characters inside words
        sentence = re.sub(boilerplate, "", sentence)

        more_boilerplate = re.compile("\S+[;():~.`\"/_+=]\S+") #any of these characters inside words
        sentence = re.sub(more_boilerplate, "", sentence)
        
    

#strip punctuation before it goes into crm. (so, store it with quotes and punct, but strip that when you fetch from db to put into crm. don't strip when you fetch to show on screen.

#removing words that contain :, ;, (), dot.notation, \, {, } etc, which are probably javascript or something.


        cleaned_sentences.append(sentence)

    return cleaned_sentences


#used before text is sent to crm
def strict(sentences):
    cleaned_sentences = []
    for sentence in sentences:

        sentence = sentence.replace("\"","")
        #sentence = sentence.replace("'","") no, lots of problems with it's, 'fore, jesu', etc.

        too_much_whitespace = re.compile("\s\s+")
        sentence = re.sub(too_much_whitespace, "", sentence)

        lineshift = re.compile("\n")
        sentence = re.sub(lineshift," ", sentence)

        punctuation = re.compile("[.!?;:,]")
        sentence = re.sub(punctuation, "", sentence)

        cleaned_sentences.append(sentence)

    return cleaned_sentences
