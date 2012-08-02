import re, string



def junk(sentences):
    cleaned_sentences = []
    for sentence in sentences:

        tag = re.compile("<.*?>")
        sentence = re.sub(tag, "\n", sentence) # not "", since we still want a findable break.

        #inside words
        #should exclude 'word.<tag>' in addition to excluding 'word."'
        #should be able to tackle overlapping instances: 'code.word } code#word } ' should not yield ' } } ' but ' '
        #the crude solution to overlapping is running clean.junk() many many times.
        boilerplate = re.compile("\S+([@$<>#%^&*{}\[\]\|](?!\")\S+)+") #any of these characters inside words
        sentence = re.sub(boilerplate, "", sentence)

        boilerplate = re.compile("\S+[;():~.`/_+=](?!\")\S+") #any of these characters inside words
        sentence = re.sub(boilerplate, "", sentence)
        
        boilerplate = re.compile("\S+[0-9]\S+") #any of these characters inside words
        sentence = re.sub(boilerplate, "", sentence)
        
        #at beginning of words
        boilerplate = re.compile("\s+[@<>#%^&*{}\[\]\|]\S+") #any of these characters at beginning of word
        sentence = re.sub(boilerplate, "", sentence)

        boilerplate = re.compile("\s+[;():~.`/_+=]\S+") #any of these characters at beginning of word
        sentence = re.sub(boilerplate, "", sentence)
        
        boilerplate = re.compile("\s+[0-9]\S+") #any of these characters at beginning of word
        sentence = re.sub(boilerplate, "", sentence)
        
        #at end of words
        boilerplate = re.compile("\S+[@$<>#%^&*{}\[\]\|]\s+") #any of these characters at end of word
        sentence = re.sub(boilerplate, "", sentence)

        boilerplate = re.compile("\S+[;():~.`/_+=]\s+") #any of these characters at end of word
        sentence = re.sub(boilerplate, "", sentence)

        boilerplate = re.compile("\S+[0-9]\s+") #any of these characters at end of word
        sentence = re.sub(boilerplate, "", sentence)
        
        #alone
        boilerplate = re.compile("\s+[@$<>#%^{}\[\]\|]\s+") #any of these characters alone
        sentence = re.sub(boilerplate, " ", sentence)

        boilerplate = re.compile("\s+[;():~.`\"/_]\s+") #any of these characters alone
        sentence = re.sub(boilerplate, " ", sentence)

        dashes = re.compile("--+")
        sentence = re.sub(dashes," ",sentence)
            

#strip punctuation before it goes into crm. (so, store it with quotes and punct, but strip that when you fetch from db to put into crm. don't strip when you fetch to show on screen.

#removing words that contain :, ;, (), dot.notation, \, {, } etc, which are probably javascript or something.


        cleaned_sentences.append(sentence)

    return cleaned_sentences


#used before text is sent to crm
def strict(sentences):
    cleaned_sentences = []
    for sentence in sentences:

        sentence = sentence.replace("\""," ")
        #sentence = sentence.replace("'","") no, lots of problems with it's, 'fore, jesu', etc.
        sentence = sentence.replace("="," ")
        sentence = sentence.replace("*"," ")
        sentence = sentence.replace("$"," ")

        lineshift = re.compile("\n")
        sentence = re.sub(lineshift," ", sentence)

        punctuation = re.compile("[.!?;:,]")
        sentence = re.sub(punctuation, " ", sentence)

        numbers = re.compile("[0-9]")
        sentence = re.sub(numbers, " ", sentence)

        too_much_whitespace = re.compile("\s\s+")
        sentence = re.sub(too_much_whitespace, " ", sentence)

        cleaned_sentences.append(sentence)

    return cleaned_sentences
