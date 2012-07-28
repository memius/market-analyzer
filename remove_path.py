#!/usr/bin/python
# coding: utf-8

#Gyri S. Losnegaard

import string

def remove_path(s):
    while 1:
        if s.find("/") == -1:
            break
        else:
            i = s.find("/") +1
            s = s[i:]
    return s

if __name__ == '__main__':
    import sys
#    remove_path(open(sys.argv[1]).read())
    remove_path(sys.argv[1])

