# coding: utf-8

import re, string



def junk(sentences):
    cleaned_sentences = []
    for sentence in sentences:

        tag = re.compile("<.*?>")
        sentence = re.sub(tag, "\n", sentence) # not "", since we still want a findable break.

        #should exclude 'word.<tag>' in addition to excluding 'word."'

        #sould get words lik this: $("object, with more than one non-letter

        boilerplate = re.compile("\S+([@$<>#%^&*{}\[\]\|](?!\")\S+)+") #any of these characters inside words
        sentence = re.sub(boilerplate, " ", sentence)

        boilerplate = re.compile("\S+[;():~`/_+=](?!\")\S+") #any of these characters inside words
        sentence = re.sub(boilerplate, " ", sentence)
        
        boilerplate = re.compile("\S+[0-9]\S+") #any of these characters inside words
        sentence = re.sub(boilerplate, " ", sentence)
        
        boilerplate = re.compile("[a-zA-Z]+\.[a-zA-Z]+ ") # U.S. and D.C., but not var.function
        sentence = re.sub(boilerplate, " ", sentence)
        
        #at beginning of words
        boilerplate = re.compile("\s+[@<>#%^&*{}\[\]\|]\S+") #any of these characters at beginning of word
        sentence = re.sub(boilerplate, " ", sentence)

        boilerplate = re.compile("\s+[;():~`/_+=]\S+") #any of these characters at beginning of word
        sentence = re.sub(boilerplate, " ", sentence)
        
        boilerplate = re.compile("\s+[0-9]\S+") #any of these characters at beginning of word
        sentence = re.sub(boilerplate, " ", sentence)
        
        #at end of words
        boilerplate = re.compile("\S+[@$<>#%^&*{}\[\]\|]\s+") #any of these characters at end of word
        sentence = re.sub(boilerplate, " ", sentence)

        boilerplate = re.compile("\S+[;():~`/_+=]\s+") #any of these characters at end of word
        sentence = re.sub(boilerplate, " ", sentence)

        boilerplate = re.compile("\S+[0-9]\s+") #any of these characters at end of word
        sentence = re.sub(boilerplate, " ", sentence)
        
        #alone
        boilerplate = re.compile("(?<=\s)[@$<>#%^{}\[\]\|]\s+") #any of these characters alone (overlapping)
        sentence = re.sub(boilerplate, " ", sentence)

        boilerplate = re.compile("(?<=\s)[;():~.`\"/_]\s+") #any of these characters alone (overlapping)
        sentence = re.sub(boilerplate, " ", sentence)

        dashes = re.compile("--+")
        sentence = re.sub(dashes," ",sentence)

        lineshift = re.compile("\n")
        sentence = re.sub(lineshift," ", sentence)

        too_much_whitespace = re.compile("\s\s+")
        sentence = re.sub(too_much_whitespace, " ", sentence)

        sentence = sentence.replace("="," ")
        sentence = sentence.replace("*"," ")

        # boilerplate words 
        word = re.compile(" arial[.,]? ", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile(" img ", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile(" attr ", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile(" li[.,]? ", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile(" ul[.,]? ", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile(" elem ", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)

        #without spaces:
        word = re.compile("hentry", re.IGNORECASE)
        sentence = re.sub(word, " ", sentence)
        word = re.compile("aspectratio", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("helvetica", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("wrapwidth", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("origvideo", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("weneca", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("format-video", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("valuewalk", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("ui-tabs-panel", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("ui-tabs-nav", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("main-navigation", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("sf-menu", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("lost your password?", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("all rights reserved", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("bottom-widget", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("https", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("http", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("attr\(", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("scpt", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("remember me", re.IGNORECASE) #overkill, but ok, since such utterances are personal and therefore unimportant for a company's prospects.
        sentence = re.sub(word, " ", sentence)
        word = re.compile("send us your tips", re.IGNORECASE)
        sentence = re.sub(word, " ", sentence)
        word = re.compile("ajax", re.IGNORECASE) # sports are unimportant
        sentence = re.sub(word, " ", sentence)
        word = re.compile("tweet more on this topic", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("if sent email", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("addcomment", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("sendnotification", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("return else", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("sendnotification", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("return var", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("var po var", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("login register", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("if updated and cached", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("all information is completely confidential", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("side bar", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("sidebar", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("hosting and development by", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("var var", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("var email", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("enter a valid email", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("var data", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("enter your email", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("call to update facebook comment", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("You can follow any responses to this entry through the RSS feed", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("addedcomment", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("caught added making", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("leave comments leave a reply", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("your email address will not be published", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("cancel reply", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("var po", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("else failed to send email", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("\.content", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("\.tab", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("\.wrap", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("side-widget", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("sfhover", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("else failed to update facebook comment", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("times new roman", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("sub-navigation", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("storycontent", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("more-link", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("using custom configuration items", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("[prev|next] button key", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("\"width\"", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("\"height\"", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("\"left\"", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("\"right\"", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("name \"description\" content", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("scroll items", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("var title", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("statcounter", re.IGNORECASE) 
        sentence = re.sub(word, " ", sentence)
        word = re.compile("bottomcontainerbox", re.IGNORECASE)
        sentence = re.sub(word, " ", sentence)
        word = re.compile("google analytics for wordpress", re.IGNORECASE)
        sentence = re.sub(word, " ", sentence)
        word = re.compile("var ga", re.IGNORECASE)
        sentence = re.sub(word, " ", sentence)
        word = re.compile("var s", re.IGNORECASE)
        sentence = re.sub(word, " ", sentence)
        word = re.compile("name email website comment", re.IGNORECASE)
        sentence = re.sub(word, " ", sentence)
        word = re.compile("alt web var bsa", re.IGNORECASE)
        sentence = re.sub(word, " ", sentence)
        word = re.compile("hello guest", re.IGNORECASE)
        sentence = re.sub(word, " ", sentence)
        word = re.compile("a password will be e-mailed to you", re.IGNORECASE)
        sentence = re.sub(word, " ", sentence)

# » [if


            
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


        sentence = sentence.replace("$"," ")

        punctuation = re.compile("[.!?;:,]")
        sentence = re.sub(punctuation, " ", sentence)

        numbers = re.compile("[0-9]")
        sentence = re.sub(numbers, " ", sentence)

        cleaned_sentences.append(sentence)

    return cleaned_sentences
