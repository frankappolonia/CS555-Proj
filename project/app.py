from json.encoder import INFINITY
import os
from pprint import pprint
from tkinter.font import families
from prettytable import PrettyTable
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import traceback
import itertools

# GLOBALS
working_directory = os.getcwd()

#input_file = working_directory + "/myFamily.ged"
#output_file = working_directory + "/output.txt"
input_file = working_directory + "./myFamily.ged"
output_file = working_directory + "./output.txt"
#input_file = working_directory + "/../myFamily.ged"
#output_file = working_directory + "/../output.txt"


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


## Parse Data
def parseData():
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


## Store the results in data structures
def storeInDataStructures():
    individuals = {}
    families = {}

    #validation for same name/birthdate
    nameBirthValidate = {}

    parsing_indi = False
    parsing_fam = False
    curr_name = ""
    curr = {}
    prev_line = ""
    with open(output_file, 'r') as filehandle:
        for line in filehandle:
            try:
                if "<--" in line:
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

                            #before adding invidual to individuals datastructure, verify the same name/birthdate combo is not already present
                            if curr['NAME'] in nameBirthValidate:
                                if curr['DATE'] == nameBirthValidate['NAME']:
                                    raise Exception("Error: duplicate indivudal found in ged file!")
                            else:
                                nameBirthValidate[curr['NAME']] = curr['DATE'] #add invidual name + birthday to duplicate validator 
                                
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
                        if fields[1] in curr:
                            if fields[1] == 'DATE':
                                curr[prev_line[1]] = fields[3]
                            if fields[1] == "FAMS":
                                curr[fields[1]].append(fields[3])
                            if fields[1] == 'CHIL':
                                curr[fields[1]].append(fields[3])
                        elif fields[1] == "FAMS":
                            curr[fields[1]] = [fields[3]]
                        elif fields[1] == 'CHIL':
                            curr[fields[1]] = [fields[3]]
                        else:
                            curr[fields[1]] = fields[3]

                    prev_line = fields
            except Exception as e:
                print(e)

    # Add in the last added info
    try:          
        if curr != {} and parsing_fam:
            families[curr_name] = curr
            curr = {}
            curr_name = ""
            parsing_fam = False

        elif curr != {} and parsing_indi:
            #before adding invidual to individuals datastructure, verify the same name/birthdate combo is not already present
            if curr['NAME'] in nameBirthValidate:
                if curr['DATE'] == nameBirthValidate['NAME']:
                    raise Exception("Error: duplicate indivudal found in ged file!")
            else:
                nameBirthValidate[curr['NAME']] = curr['DATE'] #add invidual name + birthday to duplicate validator 
                individuals[curr_name] = curr
                curr = {}
                curr_name = ""
                parsing_indi = False

    except Exception as e:
            print(e)
    
    return individuals, families


## individuals table
def createIndividualsTable(individuals):
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
            if('DEAT' in info and info['DEAT'] != 'N'):
                to_add.append("False")
                dd = info['DEAT'].split()
                dd = date(int(dd[2]), convert_month[dd[1]], int(dd[0]))
                to_add.append(dd.isoformat())
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
                for j in info['FAMS']:
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

    return itable


## families table
def createFamiliesTable(families, individuals):
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

            if('DIV' in info and info['DIV'] != 'N'):
                dd = info['DIV'].split()
                dd = date(int(dd[2]), convert_month[dd[1]], int(dd[0]))
                to_add.append(dd.isoformat())
            else:
                to_add.append("NA")
            
            to_add.append(info['HUSB'][1:-1]) # remove @ signs on beginning and end
            # get husband name
            to_add.append(individuals[info['HUSB']]['NAME'])

            to_add.append(info['WIFE'][1:-1]) # remove @ signs on beginning and end
            # get wife name
            to_add.append(individuals[info['WIFE']]['NAME'])

            if('CHIL' in info):
                temp = []
                for j in info['CHIL']:
                    temp.append(j[1:-1]) # remove @ signs on beginning and end
                # US 28 Order siblings by age
                def getTime(ind):
                    if ind[0] != '@':
                        ind = '@' + ind + '@'
                    bd = individuals[ind]['DATE'].split()
                    return date(int(bd[2]), convert_month[bd[1]], int(bd[0]))
                temp.sort(key=getTime)
                to_add.append(temp)
            else:
                to_add.append("NA")  
                        
            ftable.add_row(to_add)
        except Exception:
            print("Error with family " + i)
            print("Info: ", families[i])
            traceback.print_exc()
            print()
    return ftable


## US29 - gets all deceased family members
def getDeceased(individualsTable):
    deceased = []
    for row in individualsTable:
        if (row.get_string(fields=["Alive"]).find('False')) != -1:
            val = (row.get_string(fields=["Name"])).strip()
            val="".join(c for c in val if c.isalnum())
            deceased.append(val[15:])
    return deceased


## US02 - find marriage before birth errors
def marriageBeforeBirthErrors(individuals, families):
    errors = []
    for f in families:
        if families[f]["HUSB"] in individuals and families[f]["WIFE"] in individuals:
            marr = (datetime.strptime(families[f]["DATE"], "%d %b %Y"))
            b1 = (datetime.strptime(individuals[families[f]["HUSB"]]["DATE"], "%d %b %Y"))
            b2 = (datetime.strptime(individuals[families[f]["WIFE"]]["DATE"], "%d %b %Y"))
            if marr < b1:
                h_id = families[f]["HUSB"]
                errors.append(f"Error: Husband {h_id} of family {f} has a birth date after their marriage date")
            if marr < b2:
                w_id = families[f]["WIFE"]
                errors.append(f"Error: Wife {w_id} of family {f} has a birth date after their marriage date")
    return errors


## US03 - find death before birth errors
def deathBeforeBirthErrors(individuals):
    errors = []
    for i in individuals:
        if "DEAT" in individuals[i]:
            birth = (datetime.strptime(individuals[i]["DATE"], "%d %b %Y"))
            death = (datetime.strptime(individuals[i]["DEAT"], "%d %b %Y"))
            if death < birth:
                errors.append(f"Error: Individual {i} has a birth date after their death date")
    return errors

## US01	Dates before current date
# Dates (birth, marriage, divorce, death) should not be after the current date
def datesBeforeCurrentDateErrors(individuals, families):
    errors = []
    today = datetime.today()
    for i in individuals:
        birth = (datetime.strptime(individuals[i]["DATE"], "%d %b %Y"))
        if (today < birth):
            errors.append(f"Error: Individual {i} has a birth date after current date")
        if "DEAT" in individuals[i]:
            death = (datetime.strptime(individuals[i]["DEAT"], "%d %b %Y"))
            if (today < death):
                errors.append(f"Error: Individual {i} has a death date after current date")

    for f in families:
        marriage = (datetime.strptime(families[f]["DATE"], "%d %b %Y"))
        if (today < marriage):
            errors.append(f"Error: Family {f} has a marriage date after current date")
        if "DIV" in families[f]:
            divorce = (datetime.strptime(families[f]["DIV"], "%d %b %Y"))
            if (today < divorce):
                errors.append(f"Error: Family {f} has a divorce date after current date")
    return errors
        

## US04	Marriage before divorce
# Marriage should occur before divorce of spouses, and divorce can only occur after marriage
def marriageBeforeDivorceErrors(families):
    errors = []
    for f in families:
        if "DIV" in families[f]:
            marr = (datetime.strptime(families[f]["DATE"], "%d %b %Y"))
            div  = (datetime.strptime(families[f]["DIV"], "%d %b %Y"))
            if div < marr:
                errors.append(f"Error: Family {f} has a divorce date before their marriage date")
    return errors

## US05 - find death before marriage errors
def deathBeforeMarriageErrors(individuals, families):
    errors = []
    for f in families:
        if families[f]["HUSB"] in individuals and families[f]["WIFE"] in individuals:
            marr = (datetime.strptime(families[f]["DATE"], "%d %b %Y"))
            if "DEAT" in individuals[families[f]["HUSB"]]:
                d1 = (datetime.strptime(individuals[families[f]["HUSB"]]["DEAT"], "%d %b %Y"))
                if d1 < marr:
                    h_id = families[f]["HUSB"]
                    errors.append(f"Error: Husband {h_id} of family {f} has a death date before their marriage date")
            if "DEAT" in individuals[families[f]["WIFE"]]:
                d2 = (datetime.strptime(individuals[families[f]["WIFE"]]["DEAT"], "%d %b %Y"))
                if d2 < marr:
                    h_id = families[f]["WIFE"]
                    errors.append(f"Error: Wife {h_id} of family {f} has a death date before their marriage date")
    return errors


## US06 - find death before divorce errors
def deathBeforeDivorceErrors(individuals, families):
    errors = []
    for f in families:
        if families[f]["HUSB"] in individuals and families[f]["WIFE"] in individuals:
            if "DIV" in families[f]:
                div = (datetime.strptime(families[f]["DIV"], "%d %b %Y"))
                if "DEAT" in individuals[families[f]["HUSB"]]:
                    d1 = (datetime.strptime(individuals[families[f]["HUSB"]]["DEAT"], "%d %b %Y"))
                    if d1 < div:
                        h_id = families[f]["HUSB"]
                        errors.append(f"Error: Husband {h_id} of family {f} has a death date before their divorce date")
                if "DEAT" in individuals[families[f]["WIFE"]]:
                    d2 = (datetime.strptime(individuals[families[f]["WIFE"]]["DEAT"], "%d %b %Y"))
                    if d2 < div:
                        h_id = families[f]["WIFE"]
                        errors.append(f"Error: Wife {h_id} of family {f} has a death date before their divorce date")
    return errors


#US10
def marriageAfter14(individuals, families):
    
    format = '%d %b %Y'
    invalidMarriages = []

    for fam in families:
        marriageDate = int(str(datetime.strptime(families[fam]['DATE'], format))[:4])
        husbandBirth = int(str(datetime.strptime(individuals[families[fam]['HUSB']]['DATE'], format))[:4])
        wifeBirth = int(str(datetime.strptime(individuals[families[fam]['WIFE']]['DATE'], format))[:4])

        if marriageDate-wifeBirth < 14 or marriageDate-husbandBirth < 14:
            invalidMarriages.append(fam)
    return invalidMarriages

#US07
def ageLessThan150(individuals):
    invalidPeople = []
    for p in individuals:
        person = individuals[p]

        bd = person['DATE'].split()
        bd = date(int(bd[2]), convert_month[bd[1]], int(bd[0]))
         # compute age
        today = date.today()
        age = today.year - bd.year -((today.month, today.day) < (bd.month, bd.day))

        if age > 150:
            invalidPeople.append(p)
    return invalidPeople

#US08
def birthBeforeMarriageOfParents(individuals, families):
    errors = []
    for f in families:
        if not ('CHIL' in families[f] and len(families[f]['CHIL']) > 0):
            continue
        marr = (datetime.strptime(families[f]["DATE"], "%d %b %Y"))
        if "DIV" in families[f]:
            div = (datetime.strptime(families[f]["DIV"], "%d %b %Y")) + relativedelta(months=9)
        for c in families[f]['CHIL']: 
            birth = (datetime.strptime(individuals[c]["DATE"], "%d %b %Y"))
            if birth < marr:
                errors.append(f"Error: Individual {c} of family {f} has a birth date before parents' marriage date")
            if "DIV" in families[f]:
                div = (datetime.strptime(families[f]["DIV"], "%d %b %Y")) + relativedelta(months=9)
                if birth > div:
                    errors.append(f"Error: Individual {c} of family {f} has a birth date more than nine months after parents' divorce date")
    return errors   
            

#US09
def birthAfterDeathOfParents(individuals, families):
    errors = []
    for f in families:
        if not ('CHIL' in families[f] and len(families[f]['CHIL']) > 0):
            continue
        d_husb, d_wife = [datetime(9999, 1, 1)]*2 # default values for when no death exists
        if "DEAT" in individuals[families[f]['HUSB']]:
            d_husb = (datetime.strptime(individuals[families[f]["HUSB"]]["DEAT"], "%d %b %Y")) + relativedelta(months=9)
        if "DEAT" in individuals[families[f]['WIFE']]:
            d_wife = (datetime.strptime(individuals[families[f]["WIFE"]]["DEAT"], "%d %b %Y"))        
        for c in families[f]['CHIL']:
            birth = (datetime.strptime(individuals[c]["DATE"], "%d %b %Y"))
            if birth > d_husb:
                errors.append(f"Error: Individual {c} of family {f} has a birth date more than nine months after father's death")
            if birth > d_wife:
                errors.append(f"Error: Individual {c} of family {f} has a birth date after mother's death")
    return errors   

# US13 - Siblings spacing
def siblingSpacingErrors(individuals, families):
    errors = []
    t1 = timedelta(days=2)
    t2 = timedelta(days=270)
    for fam in families:
        if(families[fam]['CHIL']):
            children = families[fam]['CHIL']
            dates = []
            for child in children:
                dates.append(datetime.strptime(individuals[child]["DATE"], "%d %b %Y"))
            while len(dates) > 1:
                for i in range(1, len(dates)):
                    d = abs(dates[i]-dates[0])
                    if(d > t1 and d < t2):
                        errors.append(f"Error: children in family {fam} are not spaced apart sufficiently")
                        break
                dates = dates[1:]
    return errors

# US14 - Multiple births <= 5
def multipleBirthsErrors(individuals, families):
    errors = []
    t1 = timedelta(days=2)
    for fam in families:
        if(families[fam]['CHIL']):
            children = families[fam]['CHIL']
            dates = []
            for child in children:
                dates.append(datetime.strptime(individuals[child]["DATE"], "%d %b %Y"))
            dates.sort()
            num = 1
            for i in range(1, len(dates)):
                d = abs(dates[i]-dates[i-1])
                if d < t1:
                    num+=1
                else:
                    if num > 5:
                        errors.append(f"Error: more than 5 children were born at once to family {fam}")
                        break
                    num = 1
    return errors

# US15 - Fewer than 15 siblings
def fewerThan15Siblings(families):
    famsWithTooManySiblings = []
    for fam in families:
        if len(families[fam]['CHIL']) > 15:
            famsWithTooManySiblings.append(fam)
    return famsWithTooManySiblings

# US16 - All male members should have same last name
def malesLastName(individuals, families):
    errorFams = []
    famKeys = {}

    for fam in families:
        famKeys[fam] = []
        for key in families[fam]:
            if key == 'HUSB':
                famKeys[fam].append(families[fam]['HUSB'])
                fullName = individuals[families[fam]['HUSB']]['NAME']
                lastName = fullName[fullName.index("/")+1:]
            elif key == 'CHIL':
                for k in families[fam]['CHIL']:
                    famKeys[fam].append(k)


    for fam in famKeys:
        currLastName = False
        for key in famKeys[fam]:
            if individuals[key]['SEX'] != 'M':
                continue
            name = individuals[key]['NAME']
            last = name[name.index("/")+1:]
            if not currLastName:
                currLastName = last
            elif last != currLastName:
                errorFams.append(fam)
                break
    return errorFams


## US11 Marriage should not occur during marriage to another spouse
def noBigamy(families):
    errors = []
    for f in itertools.combinations(families,r=2): #examine pairs of families
        if families[f[0]]['HUSB'] != families[f[1]]['HUSB'] and families[f[0]]['WIFE'] != families[f[1]]['WIFE']:
            continue
        
        div1, div2 = [datetime(9999, 1, 1)]*2 # default values for when no divorce exists
        if 'DIV' in families[f[0]]:
            div1 = (datetime.strptime(families[f[0]]["DIV"], "%d %b %Y"))
        if 'DIV' in families[f[1]]:
            div2 = (datetime.strptime(families[f[1]]["DIV"], "%d %b %Y"))
        marr1 = (datetime.strptime(families[f[0]]["DATE"], "%d %b %Y"))
        marr2 = (datetime.strptime(families[f[1]]["DATE"], "%d %b %Y"))

        if marr1 > marr2 and div2 > marr1:
            errors.append(f"Error: Bigamy in families {f[0]} and {f[1]}")
            continue
        if marr2 > marr1 and div1 > marr2:
            errors.append(f"Error: Bigamy in families {f[0]} and {f[1]}")
    return errors
    


## US12 Mother should be less than 60 years older than her children
##  and father should be less than 80 years older than his children
def parentsNotTooOld(individuals, families):
    errors = []
    today = date.today()
    for f in families:
        husb_bd = individuals[families[f]['HUSB']]['DATE'].split()
        husb_bd = date(int(husb_bd[2]), convert_month[husb_bd[1]], int(husb_bd[0]))
        husb_age = today.year - husb_bd.year -((today.month, today.day) < (husb_bd.month, husb_bd.day))
        wife_bd = individuals[families[f]['WIFE']]['DATE'].split()
        wife_bd = date(int(wife_bd[2]), convert_month[wife_bd[1]], int(wife_bd[0]))
        wife_age = today.year - wife_bd.year -((today.month, today.day) < (wife_bd.month, wife_bd.day))
        for c in families[f]['CHIL']:
            chil_bd = individuals[c]['DATE'].split()
            chil_bd = date(int(chil_bd[2]), convert_month[chil_bd[1]], int(chil_bd[0]))
            chil_age = today.year - chil_bd.year -((today.month, today.day) < (chil_bd.month, chil_bd.day))
            if husb_age - chil_age > 80:
                errors.append(f"Error: {families[f]['HUSB']} is 80+ years older than child {c}")
            if wife_age - chil_age > 60:
                errors.append(f"Error: {families[f]['WIFE']} is 60+ years older than child {c}")
    return errors
    

#US19 first cousins should not marry
def noFirstCousinMarriage(families):
    badMarriages = []
    for key in families:
        husb = families[key]['HUSB']
        wife = families[key]['WIFE']
        for k in families:
            if husb in families[k]['CHIL'] and wife in families[k]['CHIL']:
                badMarriages.append([husb, wife])
                break
    return badMarriages

#US20 Aunts & Uncles must not marry nephews or nieces
def auntsUnclesMarryingNephews(families):
    badMarriages = []
    for key in families:
        #get sibilings
        siblings = families[key]['CHIL']
        if len(siblings) == 1 or len(siblings) == 0: 
            #if only child or no child, cant marry niece/nephew
            break

        children = []
        for k in siblings:
            for j in families:
                if k == families[j]['HUSB'] or families[j]['WIFE'] == k:
                    children += families[j]['CHIL']

        for l in families:
            if families[l]['HUSB'] in siblings or families[l]['WIFE'] in siblings:
                if families[l]['HUSB'] in children or families[l]['WIFE'] in children:
                    badMarriages.append([families[l]['HUSB'], families[l]['WIFE']])

    return badMarriages


#US17 No marriages to descendants
def noMarriageToDescendants(families):
    badMarriages = []
    visited = []
    for key in families:
        husband = families[key]['HUSB']
        wife = families[key]['WIFE']
        descendants = families[key]['CHIL']
        while descendants:
            d, descendants = descendants[0], descendants[1:]
            if d not in visited:
                if d == families[key]['HUSB'] or d == families[key]['WIFE']:
                    badMarriages.append(f"Error: Marriage to descendant in family {key} between {families[key]['HUSB']} and {families[key]['WIFE']}")
                for fam in families:
                    if d == families[fam]['WIFE'] or d == families[fam]['HUSB']:
                        descendants+=families[fam]['CHIL']
                        if husband == families[fam]['HUSB'] or wife == families[fam]['WIFE']:
                            badMarriages.append(f"Error: Marriage to descendant in family {key} between {families[key]['HUSB']} and {families[key]['WIFE']}")
            visited.append(d)
    return list(set(badMarriages))


#US 18 Siblings should not marry
def noMarriageToSiblings(families):
    badMarriages = []
    for key in families:
        children = families[key]['CHIL']
        if len(children) > 1:
            for fam in families:
                husb = families[fam]['HUSB']
                wife = families[fam]['WIFE']
                if husb in children and wife in children and husb != wife:
                    badMarriages.append(f"Error: Marriage between siblings {husb} and {wife} in family {fam}")
    return badMarriages

#US 21 Husband in family should be male and wife in family should be female
def correctGender(individuals, families):
    errors = []
    for fam in families:
        husb = families[fam]['HUSB']
        wife = families[fam]['WIFE']
        if individuals[husb]['SEX'] != 'M':
            errors.append(f"Error: Husband {husb} in family {fam} not of male sex")
        if individuals[wife]['SEX'] != 'F':
            errors.append(f"Error: Wife {wife} in family {fam} not of female sex")
    return errors

        


## find errors
def findErrors(individuals, families):
    errors = []
    errors += marriageBeforeBirthErrors(individuals, families)
    errors += deathBeforeBirthErrors(individuals)
    errors += datesBeforeCurrentDateErrors(individuals, families)
    errors += marriageBeforeDivorceErrors(families)
    errors += deathBeforeMarriageErrors(individuals, families)
    errors += deathBeforeDivorceErrors(individuals, families)
    errors += birthBeforeMarriageOfParents(individuals, families)
    errors += birthAfterDeathOfParents(individuals, families)
    errors += siblingSpacingErrors(individuals, families)
    errors += multipleBirthsErrors(individuals, families)
    errors += fewerThan15Siblings(families)
    errors += malesLastName(individuals, families)
    errors += noBigamy(families)
    errors += parentsNotTooOld(individuals, families)
    errors += noFirstCousinMarriage(families)
    errors += auntsUnclesMarryingNephews(families)
    errors += noMarriageToDescendants(families)
    errors += noMarriageToSiblings(families)
    errors += correctGender(individuals, families)
    return errors

## main
if __name__ == "__main__":
    # parse data
    parseData()

    # store data
    storedData = storeInDataStructures()
    individuals, families = storedData

    print(families)
    print(individuals)
    # create data table
    individualsTable = createIndividualsTable(individuals)
    familiesTable = createFamiliesTable(families, individuals)

    # print table with individuals and families
    print(individualsTable)
    print(familiesTable)

    # check for errors
    errors = findErrors(individuals, families)
    print("\nErrors:" + (" None" if errors == [] else ""))
    for error in errors:
        print(f" - {error}")
    print()

    '''
    SPRINT 1
    -------------------------------------------------------
    #US29
    deceased = getDeceased(individualsTable)
    print("\nDeceased:", deceased)

    #US02
    marriagesb4birth = marriageBeforeBirthErrors(individuals, families)
    #US03
    deathsb4birth = deathBeforeBirthErrors(individuals)

    #US01
    datesb4currdate = datesBeforeCurrentDateErrors(individuals, families)
    #US04
    marriagesb4divorce = marriageBeforeDivorceErrors(families)
    '''

    '''
    SPRINT 2
    -------------------------------------------------------
    #US05
    deathsb4marriage = deathBeforeMarriageErrors(individuals, families)
    #US06
    deathsb4divorce = deathBeforeDivorceErrors(individuals, families)

    #US10
    invalidMarriages = marriageAfter14(individuals, families)
    #US07
    invalidAges = ageLessThan150(individuals)

    #US08
    birthsb4parentmarriage = birthBeforeMarriageOfParents(individuals, families)
    #US09
    birthsafterparentdeaths = birthAfterDeathOfParents(individuals, families)
    '''

    '''
    SPRINT 3
    -------------------------------------------------------
    
    #US13
    sibling_spacing_errors = siblingSpacingErrors(individuals, families)
    #US14
    multiple_births_errors = multipleBirthsErrors(individuals, families)
    #US15
    too_many_siblings = fewerThan15Siblings(families)
    #US16
    male_last_names = malesLastName(individuals, families)
    #US11
    bigamy = noBigamy(families)
    #US12
    parents_too_old = parentsNotTooOld(individuals, families)
    '''

    '''
    SPRINT 4
    -------------------------------------------------------------
    '''
    #US17
    marriagesToDescendants = noMarriageToDescendants(families)
    #US18
    marraigesToSiblings = noMarriageToSiblings(families)
    #US19 
    cousinsMarried = noFirstCousinMarriage(families)
    #US20
    auntsMarryingNieces = auntsUnclesMarryingNephews(families)
    #US21
    correctGenderInMarriage = correctGender(individuals, families)

    

    '''
    File output for sprint turn in
    -------------------------------------------------------
    '''
    # output for sprint turn in
    output = open("sprint4results.txt", "w")
    output.write(str(individualsTable))
    output.write(str(familiesTable))

    '''
    #Sprint 1
    output.write('\n US29: ' + str(deceased))
    output.write('\n US23: ' + "All persons names and birthdates are unique")
    output.write('\n US02: marriages before birth: ' + str(marriagesb4birth))
    output.write('\n US03: deaths before birth: ' + str(deathsb4birth))
    output.write('\n US01: dates before current date: ' + str(datesb4currdate))
    output.write('\n US04: marriages before divorce ' + str(marriagesb4divorce))
    '''

    '''
    #Sprint 2
    output.write('\n US05: deaths before marriages ' + str(deathsb4marriage))
    output.write('\n US06: deaths before divorces ' + str(deathsb4divorce))
    output.write('\n US10: marriages before 14: ' + str(invalidMarriages))
    output.write('\n US07: ages > 150: ' + str(invalidAges))
    output.write('\n US08: births before parents marriage ' + str(birthsb4parentmarriage))
    output.write('\n US09: births after parents death ' + str(birthsafterparentdeaths))
    '''

    ''' 
    #Sprint 3
    output.write('\n US13: sibling spacing errors: ' + str(sibling_spacing_errors))
    output.write('\n US14: multiple births errors: ' + str(multiple_births_errors))
    output.write('\n US15: fewer than 15 siblings errors: ' + str(too_many_siblings))
    output.write('\n US16: males with different last name errors: ' + str(male_last_names))
    output.write('\n US11: bigamy: ' + str(bigamy))
    output.write('\n US12: parents too much older than children: ' + str(parents_too_old))
    '''
    

    #Sprint 4
    output.write('\n US17: no marriage to descendants: ' + str(marriagesToDescendants))
    output.write('\n US18: siblings should not marry: ' + str(marraigesToSiblings))
    output.write('\n US19: first cousins should not marry: ' + str(cousinsMarried))
    output.write('\n US20: aunts/uncles shouldnt marry nieces/nephews: ' + str(auntsMarryingNieces))
    output.write('\n US21: Husband should be male and Wife should be female: ' + str(correctGenderInMarriage))

    output.close()





