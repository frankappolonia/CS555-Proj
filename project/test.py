import unittest
from app import *

class SprintTests(unittest.TestCase):
    i1 = {
        '@I1@': {'NAME': 'Matthew /Appolonia/', 'SEX': 'M', 'DATE': '8 DEC 1965', 'DEAT': '6 MAR 2022', 'FAMS': ['@F1@'], 'FAMC': '@F2@'}, 
        '@I2@': {'NAME': 'Catherine /Arace/', 'SEX': 'F', 'DATE': '4 AUG 1975', 'DEAT': '13 JUL 2017', 'FAMS': ['@F1@'], 'FAMC': '@F3@'}, 
        '@I3@': {'FAMC': '@F1@', 'NAME': 'Sandra /Arace/', 'SEX': 'F', 'DATE': '12 JUN 1993', 'FAMS': ['@F3@']}
    }

    f1 = {
        '@F1@': {'HUSB': '@I1@', 'WIFE': '@I2@', 'CHIL': '@I3@', 'DATE': '10 MAR 1990', 'DIV': '26 JUL 2004'}
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

  
if __name__ == '__main__':
    unittest.main()