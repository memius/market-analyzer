lst = ["one","two","three","four"]

def helper():
    print "in helper"
    return #ends the function
    exit() #ends the program



ctr = 1
for string in lst:
    print "in loop"
    if ctr > 2:
        print "ctr > 2"
        break
    else:
        ctr += 1
        print "ctr = ",ctr
        helper()
        print "after helper"
        break # jumps out of the for loop
        continue # ignores the rest of this iteration, but continues the loop.
    print "did you get here?"

