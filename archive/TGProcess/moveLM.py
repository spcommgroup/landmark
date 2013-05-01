from TGProcess import * #TGProcess.py must be in the same directory as this file, \
                        # or in the Python modules directory, for this import to succeed.
import sys
import os
import re


def userInterface(t):
    print("")
    print("==================================")
    print("Welcome to the TextGrid Processor!")
    print("")
    print("The original TextGrid file will stay unmodified at: " + filepath)
    print("The processed TextGrid file will be written to: " + destpath)
    print("")

    print("STEP 1 OF 2: Enter the landmarks you wish to move, one per line.")
    print("Enter an empty line to end the list when you're done.")

    tagList = [] #"tag" and "landmark" are used interchangable.  "tag" is just shorter and more general.
    while True:
        i = input("> ")
        if i != "":
            tagList.append(i)
        else:
            break
    print("")

    if tagList == []:
        tagList = ["+g","-g","<ipp","ipp>","+g-?","+g?","-g-?","<ipp>",">ipp","ipp<"]
        print("No landmarks entered.  Using default landmarks:")
        print(tagList)
        print("")
    
    print("STEP 2 OF 2: The TextGrid contains the following tiers: ")
    for i in range(0,len(t)):
        print("   " + str(i+1) + ": " + str(t[i]))
    print()

    print("Enter the row numbers of the source tier(s), separated by commas if there are muliple sources.")
    print("For example: > 2,4")
    sourceTiers = [int(x) for x in input("> ").rsplit(",")]
    print("")

    print("Enter the row number of the *ONE* destination tier.")
    print("For example: > 3")
    print("Or, to add a *NEW* tier as the destination, type the + sign")
    inp = input("> ")
    print("")

    if inp == "+":
        print("What tier number would you like to insert the new tier *AFTER*? (Type 0 to add the tier at the top.)")
        newTierAfter = int(input("> "))
        destTier = newTierAfter + 1
        print("Enter the name of the new tier:")
        newTierName = input("> ")
        for i in range(0,len(sourceTiers)):
            if (sourceTiers[i] > newTierAfter):
                sourceTiers[i]+=1 #Tiers after the inserted tier now have higher tier number.
        t.tiers.insert(newTierAfter,Tier(tierClass="TextTier",name=newTierName,xmin="0",xmax=t.xmax))
        print(str([tier.name for tier in t.tiers]))
        print(sourceTiers)
        print("Tier added.")
        print("")
    else:
        destTier = int(inp)
    return(tagList,sourceTiers,destTier)

def process(t,tagList,sourceTiers,destTier):
    for tier in sourceTiers:
        #We cannot use a for loop, because we alter the list we'd be looping through.
        #Instead, we keep track of the index of the point we're currently considering
        pointIndex = 0
        while pointIndex<len(t[tier-1]):
            #split, eg, "f/t-cl" into ["f","t-cl"] for separate analysis
            allLMs = t[tier-1][pointIndex].landmarkList()
            remainingLMs = [] #list of landmarks from allLMs that are not moved.
            for landmark in allLMs:
                if landmark in tagList:
                    #Add landmarks to destTier
                    t[destTier-1].addPoint(Point(t[tier-1][pointIndex].time,landmark))
                    #Here, we DO NOT add landmark to remainingLMs
                else:
                    #Don't move the landmark; add it to remainingLMs to keep it where it is
                    remainingLMs.append(landmark)
            if  remainingLMs == []:
                #remove points from which all landmarks were removed
                t[tier-1].removeItem(pointIndex)
                #The next item in the list will "slide back" into this position.
                #So, we don't increment pointIndex... it already refers to this next point!
            else:
                #or, reassemble remaining landmarks into one string, update the point.
                t[tier-1][pointIndex].setMarkFromList(remainingLMs)
                pointIndex += 1

#If is program was run on its own (not imported into another file):
if __name__=="__main__":
    if len(sys.argv) < 2:
        exit("Usage: python moveLM.py /Path/To/File.TextGrid")
    filepath = os.path.abspath(sys.argv[1])
    pathsplit = os.path.splitext(filepath)
    destpath = pathsplit[0] + ".processed" + pathsplit[1]
    
    t = TextGrid(filepath=filepath)
        
    (tagList, sourceTiers, destTier) = userInterface(t)
    print("Processing TextGrid...\n")
    process(t,tagList,sourceTiers,destTier)
    t.writeGridToPath(destpath)
    print("File written to " + destpath +  ".")
    print("The TextGrid Processor has finished.")
    print("")
