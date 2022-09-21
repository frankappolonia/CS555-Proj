import os
working_directory = os.getcwd()
file_path = working_directory + "myFamily.ged"

f = open(working_directory + "\project\myFamily.ged")
results = open("output.txt", "w")


validTags = set({"INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "FAM", "MARR", "HUSB", "WIFE", "CHIL", "DIV", "DATE", "HEAD", "TRLR", "NOTE"})

for line in f:
    '''Loops through each line of the GEDCOM file'''

    #1. first, write the original line as input
    results.write("--> " + line)

    #2. Next, build the output line
    
    #2a. the output line always starts with the ouput arrow + the number in the line (either a 0, 1 or 2)
    output = "<-- " + line[:1] + "|"

    #3. from here, there are 3 scenarios for how the rest of the line could be. we iterate through the line and slice it
        # based on the scenario
    for i in range(2, len(line)):

        #3a. Scenario 1 - id is before tag (i.e. 0 @I2@ INDI)
        if line[i] == "@":
            _id = line[i: line.find("@", i+1)+1]
            tag = line[line.find("@",i+1)+2:].strip()
            output += tag
            if tag in validTags:
                output += "|Y|"
            else:
                output += "|N|"
            output += _id
            break
            
        #3b. scenario 2 - line is in standard format (i.e SOUR Family Echo)
        if line[i] == " ":
            tag = line[2:i]
            output += tag 
            if tag in validTags:
                output += "|Y|"
            else:
                output += "|N|"
            output += line[i+1:]
            break
        
        #3c. scenario 3 - Only two values, number and tag only (i.e. 1 BIRT)
        if i == len(line)-1:
            tag = line[2:]
            if tag in validTags:
                output += "Y|"+line[2:]
            else:
                output += "N|"+line[2:]

    results.write(output + "\n")

results.close()

