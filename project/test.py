from multiprocessing.dummy import Array
import unittest
from app import *

class SprintTests(unittest.TestCase):
    i1 = {
        '@I1@': {'NAME': 'Matthew /Appolonia/', 'SEX': 'M', 'DATE': '8 DEC 1965', 'DEAT': '6 MAR 2022', 'FAMS': ['@F1@'], 'FAMC': '@F2@'}, 
        '@I2@': {'NAME': 'Catherine /Arace/', 'SEX': 'F', 'DATE': '4 AUG 1975', 'DEAT': '13 JUL 2017', 'FAMS': ['@F1@'], 'FAMC': '@F3@'}, 
        '@I3@': {'FAMC': '@F1@', 'NAME': 'Sandra /Arace/', 'SEX': 'F', 'DATE': '12 JUN 1993', 'FAMS': ['@F3@']}
    }

    f1 = {
        '@F1@': {'HUSB': '@I1@', 'WIFE': '@I2@', 'CHIL': ['@I3@'], 'DATE': '10 MAR 1990', 'DIV': '26 JUL 2004'}
    }

    def test1_sprint2(self):
        e = deathBeforeMarriageErrors(self.i1, self.f1)
        self.assertEqual(e, [])

    def test2_sprint2(self):
        self.f1["@F1@"]["DATE"] = "10 MAR 2022"
        e = deathBeforeMarriageErrors(self.i1, self.f1)
        self.assertEqual(len(e), 2)
        self.assertTrue("I1" in e[0])
        self.assertTrue("I2" in e[1])
        self.f1["@F1@"]["DATE"] = "10 MAR 1990"

    def test3_sprint2(self):
        e = deathBeforeDivorceErrors(self.i1, self.f1)
        self.assertEqual(e, [])

    def test4_sprint2(self):
        self.f1["@F1@"]["DIV"] = "26 JUL 2024"
        e = deathBeforeDivorceErrors(self.i1, self.f1)
        self.assertEqual(len(e), 2)
        self.assertTrue("I1" in e[0])
        self.assertTrue("I2" in e[1])
        self.f1["@F1@"]["DIV"] = "26 JUL 2004"

    
    def test5_sprint2(self):
        #US07
        import os
        working_directory = os.getcwd()
        input_file = working_directory + "./myFamily.ged"
        output_file = working_directory + "./output.txt"
        parseData()
        storedData = storeInDataStructures()
        individuals, families = storedData

        # create data table
        individualsTable = createIndividualsTable(individuals)

        data = ageLessThan150(individuals)
        self.assertEqual(data, [])

    def test6_sprint2(self):
        #US10
        import os
        working_directory = os.getcwd()
        input_file = working_directory + "./myFamily.ged"
        output_file = working_directory + "./output.txt"
        parseData()
        storedData = storeInDataStructures()
        individuals, families = storedData
    

        data = marriageAfter14(individuals, families)

        self.assertEqual(data, [])

    def test7_sprint2(self):
        e = birthBeforeMarriageOfParents(self.i1, self.f1)
        self.assertEqual(e, [])

    def test8_sprint2(self):
        e = birthAfterDeathOfParents(self.i1, self.f1)
        self.assertEqual(e, [])

    def test9_sprint3(self):
        e = siblingSpacingErrors(self.i1, self.f1)
        self.assertEqual(e, [])

    def test10_sprint3(self):
        e = multipleBirthsErrors(self.i1, self.f1)
        self.assertEqual(e, [])

    def test11_sprint3(self):
        #US 15
        e = fewerThan15Siblings(self.f1)
        self.assertEqual(isinstance(e, list), True)

    def test12_sprint3(self):
        #US 16
        e = malesLastName(self.i1, self.f1)
        self.assertEqual(isinstance(e, list), True)

    def test13_sprint3(self):
        #US 11
        e = noBigamy(self.f1)
        self.assertEqual(len(e), 0)

    def test14_sprint3(self):
        #US 12
        e = parentsNotTooOld(self.i1, self.f1)
        self.assertEqual(e, [])
        
    def test15_sprint4(self):
        #US 19
        e = noFirstCousinMarriage(self.f1)
        self.assertEqual(e, [])

    def test16_sprint4(self):
        #US 19
        e = auntsUnclesMarryingNephews(self.f1)
        self.assertEqual(e, [])
    
    def test17_sprint4(self):
        #US 17
        e = noMarriageToDescendants(self.f1)
        self.assertEqual(e, [])

    def test18_sprint4(self):
        #US 17
        e = noMarriageToSiblings(self.f1)
        self.assertEqual(e, [])

    def test19_sprint4(self):
        #US 21
        e = correctGender(self.i1, self.f1)
        self.assertEqual(e, [])

    def test20_sprint4(self):
        #US 28
        e = createFamiliesTable(self.f1, self.i1)
        # assert no errors
        
if __name__ == '__main__':
    unittest.main()
