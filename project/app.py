import os
from pprint import pprint
from prettytable import PrettyTable
from datetime import date
import traceback

working_directory = os.getcwd()
input_file = working_directory + "/../myFamily.ged"
output_file = working_directory + "/../output.txt"

f = open(input_file)
results = open(output_file, "w")


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

f.close()
results.close()


### Store the results in data structures ###
individuals = {}
families = {}

parsing_indi = False
parsing_fam = False
curr_name = ""
curr = {}
with open(output_file, 'r') as filehandle:
    for line in filehandle:
        if "<--" in line:
            print(line)
            fields = line.strip("<-- ").strip("\n").split("|")
            # case 1: let's start parsing a new individual or family
            if fields[0] == '0':
                # first, save any previous info
                if curr != {} and parsing_fam:
                    families[curr_name] = curr
                    curr = {}
                    curr_name = ""
                    parsing_fam = False
                elif curr != {} and parsing_indi:
                    individuals[curr_name] = curr
                    curr = {}
                    curr_name = ""
                    parsing_indi = False
                # then, set up the new info
                if fields[1] == "INDI":
                    parsing_indi = True
                    curr_name = fields[3]
                elif fields[1] == "FAM":
                    parsing_fam = True
                    curr_name = fields[3]
            # case 2: let's add info to the individual or family
            elif (parsing_fam or parsing_indi) and fields[2] == "Y":
                curr[fields[1]] = fields[3]

# Add in the last added info             
if curr != {} and parsing_fam:
    families[curr_name] = curr
    curr = {}
    curr_name = ""
    parsing_fam = False
elif curr != {} and parsing_indi:
    individuals[curr_name] = curr
    curr = {}
    curr_name = ""
    parsing_indi = False
    
pprint(families)
pprint(individuals)

### Print table with individuals and families ###

# helper dict for converting string dates to date objects
convert_month = {
    "JAN" : 1,
    "FEB" : 2,
    "MAR" : 3,
    "APR" : 4,
    "MAY" : 5,
    "JUN" : 6,
    "JUL" : 7,
    "AUG" : 8,
    "SEP" : 9,
    "OCT" : 10,
    "NOV" : 11,
    "DEC" : 12
}

## individuals table
itable = PrettyTable()
itable.title = "Individuals"
itable.field_names = ["ID","Name","Gender","Birthday","Age","Alive","Death","Child","Spouse"]

for i in individuals:
    try:
        to_add = []
        info = individuals[i]

        ## Add info field by field
        to_add.append(i[1:-1]) # remove @ signs on beginning and end
        to_add.append(info['NAME'])
        to_add.append(info['SEX'])
        # convert birthdate to date object
        bd = info['DATE'].split()
        bd = date(int(bd[2]), convert_month[bd[1]], int(bd[0]))
        to_add.append(bd.isoformat())
        # compute age
        today = date.today()
        age = today.year - bd.year -((today.month, today.day) < (bd.month, bd.day))
        to_add.append(age)
        if('DEAT' in info and info['DEAT'] == 'Y'):
            to_add.append("False")
            to_add.append("TODO")
            ## TODO: Death date
        else:
            to_add.append("True")
            to_add.append("NA")

        if('FAMC' in info):
            temp = []
            for j in info['FAMC'].split(' '):
                temp.append(j[1:-1]) # remove @ signs on beginning and end
            to_add.append(temp)
        else:
            to_add.append("NA")

        if('FAMS' in info):
            temp = []
            for j in info['FAMS'].split(' '):
                temp.append(j[1:-1]) # remove @ signs on beginning and end
            to_add.append(temp)
        else:
            to_add.append("NA")    
        
        itable.add_row(to_add)
    except Exception:
        print("Error with individual " + i)
        print("Info: ", individuals[i])
        traceback.print_exc()
        print()

## families table
ftable = PrettyTable()
ftable.title = "Families"
ftable.field_names = ["ID","Married","Divorced","Husband ID","Husband Name","Wife ID","Wife Name","Children"]

for i in families:
    try:
        to_add = []
        info = families[i]

        ## Add info field by field
        to_add.append(i[1:-1]) # remove @ signs on beginning and end

        # format marriage date
        md = info['DATE'].split()
        md = date(int(md[2]), convert_month[md[1]], int(md[0]))
        to_add.append(md.isoformat())

        if('DIV' in info and info['DIV'] == 'Y'):
            to_add.append("TODO")
            ## TODO: Divorce date
        else:
            to_add.append("NA")
        
        to_add.append(info['HUSB'][1:-1]) # remove @ signs on beginning and end
        # get husband name
        to_add.append(individuals[info['HUSB']]['NAME'])

        to_add.append(info['WIFE'][1:-1]) # remove @ signs on beginning and end
        # get wife name
        to_add.append(individuals[info['WIFE']]['NAME'])

        if('CHIL' in info and info['CHIL'].strip() != ''):
            temp = []
            for j in info['CHIL'].split(' '):
                temp.append(j[1:-1]) # remove @ signs on beginning and end
            to_add.append(temp)
        else:
            to_add.append("NA")
         
        
        ftable.add_row(to_add)
    except Exception:
        print("Error with family " + i)
        print("Info: ", families[i])
        traceback.print_exc()
        print()

print(itable)
print(ftable)

