#!/usr/bin/python
# coding: utf-8

#----------------------------------------------------------------------------
#SNIPPET GENERATOR
#Gyri S. Losnegaard
#2010/2011
#Infomedia/Dag Elgesem: The Content Re-use Project 
#Courtesy of Uni Research (Dep. Computing) & Norwegian Newspaper Corpus (NNC) 
#Knut Hofland (developer) & Gisle Andersen (project manager) 
#----------------------------------------------------------------------------

import string
import re
import codecs

def tag_sentence(s):
    s = s.lstrip()
    s = s.rstrip()
    #replace subheader intermediate tags with <s>-tags
    s = re.sub("(?P<id1><X>){1,}(?P<id2>\s*)(?P<id3></X>){1,}", "", s) #00A: replace empty <X>-tags 
    s = re.sub("<X>", "</s><s>", s)#00B: replace ad hoc-tag <X> (unoptimal solution for subheaders in running text)
    s = re.sub("</X>", "</s><s>", s)#00C: replace ad hoc-tag </X>
    #preprocessing
    s = re.sub("\A(?P<id1>–)(?P<id2>\.)(?P<id3>[A-ZÆØÅ])", "\g<id1>\g<id3>", s) #PP01: typo "-.Det er..." -> remove punctuation mark 
    #remove unwanted whitespace, insert <s> at beginning of line, and sentence-tags (</s><s>)at sentence boundaries
    s = re.sub("(?P<id1>[\.\?!:])(?P<id2> )(?P<id3>[A-ZÆØÅ])", "\g<id1>\g<id3>", s)#001: remove space after punctuation
    s = re.sub("(?P<id1>– [A-ZÆØÅ0-9])", "<s>\g<id1>", s) #002: "- Jeg har et syn som er 2000 år gammelt"
    s = re.sub("\A(?P<id1>\s*-*\s*[A-ZÆØÅa-zæøå0-9])", "<s>\g<id1>", s) #003: insert "<s>" before line-initial capital letter potentially preceeded by "-" and/or whitespace
    s = re.sub("\A(?P<id1>«[A-ZÆØÅ0-9])", "<s>\g<id1>", s) #004a: insert "<s>" before line-initial left-quote
    s = re.sub("\A(?P<id1>\"[A-ZÆØÅ0-9])", "<s>\g<id1>", s) #004b: insert "<s>" before line-initial left-quote
    s = re.sub("\A(?P<id1>\()", "<s>\g<id1>", s) #005: insert "<s>" before line-initial left-parenthesis
    s = re.sub("\A(?P<id1>\*)", "<s>\g<id1>", s) #005: insert "<s>" before line-initial "*"
    s = re.sub("(?P<id1>[A-ZÆØÅa-zæøå][\.\?!:]»$)", "\g<id1></s>", s) #006: insert end-tag after puncutation followed by right-quote
    s = re.sub("(?P<id1>[\.\?!:])(?P<id2>[A-ZÆØÅ0-9])", "\g<id1> </s><s>\g<id2>", s) #007: sentence boundaries inside string (not line-initial): insert </s> before captial letter if preceeded by punctuation. NB! Without inserting a whitespace between "<id1>" and "</s>", this expressions "deletes" these two items and causes lots of trouble. NB! Adds " </s><s>" inside among other things numerical expressions.
    s = re.sub("(?P<id1>[\.\?!:]\s*)(?P<id2>\([A-ZÆØÅ0-9])", "\g<id1></s><s>\g<id2>", s) #008: insert </s> before captial letter if immediately preceeded by left-parenthesis
    s = re.sub("(?P<id1>[\.\?!:])(?P<id2>\s*)(?P<id3>[-\"«\(”]*\s*[A-ZÆØÅ0-9])", "\g<id1> </s><s>\g<id3>", s) #009: insert </s> before captial letter if preceeded by punctuation and whitespace
    s = re.sub("(?P<id1>[_\.\?!:])(?P<id2>\n)(?P<id3>[A-ZÆØÅ0-9])", "\g<id2>\g<id1></s><s>\g<id3>", s) #010: insert </s> before captial letter if preceeded by punctuation and newline
    s = re.sub("(?P<id1>[\.\?!:])(?P<id2> \n)(?P<id3>[A-ZÆØÅ0-9])", "\g<id2>\g<id1></s><s>\g<id3>", s) #011: insert </s> before captial letter if preceeded by punctuation, whitespace and newline
    s = re.sub("(?P<id1>[\.\?!:])(?P<id2>\s*-\s*)", "\g<id1></s><s>\g<id2>", s) #012: punctuation+"-"
    #handle exceptions (remove inserted tags from special expression types like abbreviations, time-expressions, urls and e-mails etc.)
    s = re.sub("\A(?P<id1>\.{3,})(?P<id2> </s>)(?P<id3><s>)", "<s>\g<id1>", s) #013: remove end-tag "</s>" after line-initial "..." ("...</s>" -> "...")
    s = re.sub("\A(?P<id1><s>\.{3,})(?P<id2></s><s>)", "\g<id1>", s) #014: <s>...</s><s>for overfall og ran</s> -> <s>...for overfall og ran</s> (nl-20091207-20)
    s = re.sub("(?P<id1>[0-9][\.:])(?P<id2>\s*</s><s>)(?P<id3>[0-9]{2})", "\g<id1>\g<id3>", s)#015: exception from #007 which inserted end and start tags between punctuation and uppercase letter, to avoid splitting hours (18:00 etc.) by ":"
    s = re.sub("(?P<id1>vs\. )(?P<id2></s><s>)", "\g<id1>", s)#016: "vs." -> exception from #007 
    s = re.sub("(?P<id1>\(*[fF][oO][tT][oO]:)(?P<id2> </s><s>)", "\g<id1> ", s) #017: yadi yadi ya Foto: -> yadi yadi ya </s><s>Foto:
    s = re.sub("(?P<id1>»)(?P<id2>-\s*[A-ZÆØÅ])", "\g<id1></s>\n<s>\g<id2>", s)#018: "mat»-Jeg synes..."
    s = re.sub("(?P<id1>:\s*)(?P<id2>«[A-ZÆØÅ])", "\g<id1></s>\n<s>\g<id2>", s)#019: "e: «"
    s = re.sub("(?P<id1>[a-zæøå0-9]\.\s*»)(?P<id2>[A-ZÆØÅ0-9])", "\g<id1></s><s>\g<id2>", s) #020: "r.»T"
    s = re.sub("(?P<id1>[A-ZÆØÅ]\. ?)(?P<id2></s><s>)(?P<id3>[A-ZÆØÅ]\.)", "\g<id1>\g<id3>", s) #021: H. H. Hagen -> H.</s><s>H.</s><s>Hagen -> H. H. Hagen
    s = re.sub("(?P<id1>[A-ZÆØÅ]\. ?)(?P<id2></s><s>)(?P<id3>[A-ZÆØÅ][a-zæøå])", "\g<id1>\g<id3>", s) #022: Madeleine A. Rodriguez -> Madeleine A.</s><s>Rodriguez -> Madeleine A.Rodriguez
    s = re.sub("(?P<id1>St. *)(?P<id2></s><s>)(?P<id3>Olavs)", "\g<id1>\g<id3>", s) #023: St. Olavs hospital
    s = re.sub("(?P<id1>[a-zæøå])(?P<id2> )(?P<id3>\.)", "\g<id1>\g<id3>", s) #024: 
    s = re.sub("(?P<id1>\([A-Za-z][A-Za-z]* ?\.)(?P<id2></s><s>)(?P<id3>no\):</s>)", "\g<id1>\g<id3>", s) #025: (Aftenposten.</s><s>no):</s><s> -> (Aftenposten.no):</s>
    s = s.replace(".</s> mai", ". mai")#026: 
    s = re.sub("(?P<id1><s>)(?P<id2>\.*)(?P<id3>no\.*)", "\g<id2>\g<id3>", s) #027:
    s = re.sub("(?P<id1>\([A-Za-z][A-Za-z]* ?\.)(?P<id2></s><s>)(?P<id3>no\):</s>)", "\g<id1>\g<id3>", s)#028: jonas.skybakmoen@adresseavisen.no
    s = s.replace("vs.</s><s>", "vs.") #029: 
    s = re.sub("(?P<id1>[0-9]?\s*\.\s*)(?P<id2></s><s>\s*)(?P<id3>[a-zæøå])", "\g<id1>\g<id3>", s)  #029: 21.desember, 21 .desember, 21. desember
    s = re.sub("(?P<id1>[a-zæøå]\.)(?P<id2>\s*)(?P<id3><s>–)", "\g<id1></s>\g<id3>", s) #030:
    s = re.sub("(?P<id1>[Kk][Ll]\.\s*)(?P<id2></s><s>)(?P<id3>[0-9]?)", "\g<id1>\g<id3>", s) #031: klokkeslett/yime kl. 18.30
    s = re.sub("Super Mario Bros\.\s</s><s>", "Super Mario Bros.", s) #032
    s = re.sub("(?P<id1> VM\.)(?P<id2> )(?P<id3>[A-ZÆØÅ][a-zæøå])", "\g<id1></s><s>\g<id3>", s) #033: "VM. Det er..."
    s = re.sub("(?P<id1>[a-zæåø0-9][\.:!\?])(?P<id2> )(?P<id3>[ÆØÅ])", "\g<id1> </s><s>\g<id3>", s) #034: Ad hoc-rule handeling sentences starting with Æ, Ø or Å.
    s = re.sub("(?P<id1>[a-zæøå] [A-ZÆØÅ]\.)(?P<id2>\s*)(?P<id3>[A-ZÆØÅ][a-zæøå])", "\g<id1></s><s>\g<id3>", s) #035: "J, K og L. Mange..."
    s = re.sub("(?P<id1>[0-9][0-9]*\.[0-9][0-9]*\.)(?P<id2>\s*</s><s>\s*)(?P<id3>[0-9]{4})", "\g<id1>\g<id3>", s) #036: dates
    s = re.sub("(?P<id1>[0-9]\.)(?P<id2></s><s>)(?P<id3>-del)", "\g<id1>\g<id3>", s) #037: "16.-delsfinalene"
    s = re.sub("(?P<id1>[0-9]\.)(?P<id2></s><s>)(?P<id3>-plass)", "\g<id1>\g<id3>", s) #038:  "16.-plass"
    s = re.sub("(?P<id1>ca\.\s*)(?P<id2></s><s>)", "\g<id1>", s) #039: "ca."
    s = re.sub("(?P<id1>pr\.\s*)(?P<id2></s><s>)", "\g<id1>", s) #040: "pr."
    s = re.sub("(?P<id1>kr\.\s*)(?P<id2></s><s>)", "\g<id1>", s) #041: "kr."
    s = re.sub("(?P<id1>Mr\.\s*)(?P<id2></s><s>)", "\g<id1>", s) #042: "Mr."
    s = re.sub("(?P<id1>Mrs\.\s*)(?P<id2></s><s>)", "\g<id1>", s) #043: "Mrs."
    s = re.sub("(?P<id1>mill\.\s*)(?P<id2></s><s>)", "\g<id1>", s) #044: "mill."
    s = re.sub("(?P<id1>PS:\s*)(?P<id2></s><s>)", "\g<id1>", s) #045: "PS:"
    s = re.sub("(?P<id1>[a-zæøå]\s?)(?P<id2><s>)(?P<id3>\s*–\s*[A-ZÆØÅa-zæøå])", "\g<id1>\g<id3>", s) #046: "den eldste av de alle - Tonje Larsen - at hun...."
    #insert endtag at end of line
    if len(s) > 1:
        s = re.sub("(?P<id>$)", "\g<id> </s>", s) #046: insert </s> at end-of-line (NB! whitespace is necessary for the same reasons as in #007)
    return s
##    print s

##use as a main function (use print s instead of return s)
## if __name__ == '__main__':
##     import sys
##     tag_sentence(sys.argv[1])
    
    
