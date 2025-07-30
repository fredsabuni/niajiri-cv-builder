import unittest
from models.cv_data import CVData

class TestCVData(unittest.TestCase):
    def setUp(self):
        self.cv = CVData()

    def test_add_personal_info(self):
        self.cv.add_personal_info("Lillian Madeje", "hello@niajiri.com", "0712009111", "Mbezi, Dar es Salaam")
        self.assertEqual(self.cv.personal_info["name"], "Lillian Madeje")
        self.assertEqual(self.cv.personal_info["email"], "hello@niajiri.com")
        self.assertEqual(self.cv.personal_info["phone"], "0712009111")
        self.assertEqual(self.cv.personal_info["address"], "Mbezi, Dar es Salaam")

    def test_add_education(self):
        self.cv.add_education("MIT", "BSc Computer Science", "2020", "Graduated with honors")
        self.assertEqual(len(self.cv.education), 1)
        self.assertEqual(self.cv.education[0]["institution"], "MIT")
        self.assertEqual(self.cv.education[0]["degree"], "BSc Computer Science")
        self.assertEqual(self.cv.education[0]["year"], "2020")
        self.assertEqual(self.cv.education[0]["details"], "Graduated with honors")

    def test_to_dict(self):
        self.cv.add_personal_info("Lillian Madeje", "hello@niajiri.com", "0712009111", "Mbezi, Dar es Salaam")
        self.cv.add_skill("Python")
        result = self.cv.to_dict()
        self.assertEqual(result["personal_info"]["name"], "Lillian Madeje")
        self.assertEqual(result["skills"], ["Python"])

if __name__ == "__main__":
    unittest.main()