import re, string


import block


def junk(text):

    text = text.replace("\"","")
    #text = text.replace("'","") no, lots of problems with it's, 'fore, jesu', etc.

    # tag = re.compile("<.*?>")
    # text = re.sub(tag, "\n", text) # not "", since we still want a findable break.

    # too_much_whitespace = re.compile("\s+")
    # text = re.sub(too_much_whitespace, "\n", text)





#strip punctuation before it goes into crm. (so, store it with quotes and punct, but strip that when you fetch from db to put into crm. don't strip when you fetch to show on screen.

#removing words that contain :, ;, (), dot.notation, \, {, } etc, which are probably javascript or something.



    return text


