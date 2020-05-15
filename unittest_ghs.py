import unittest

import ghs


MULTIPLES_LIST = [
    {
        "error_level": 1,
        "type": "Error55_type",
        "desc": "description two",
        "line": 4,
        "file_path": "/src/file1.py",
    },
    {
        "error_level": 2,
        "type": "Error_type",
        "desc": "description",
        "line": 4,
        "file_path": "/src/file2.py",
    },
    {
        "error_level": 2,
        "type": "Error_type",
        "desc": "description",
        "line": 4,
        "file_path": "/src/file2.py",
    },
    {
        "error_level": 55,
        "type": "Error_type",
        "desc": "description",
        "line": 4,
        "file_path": "/src/file3.py",
    },
    {
        "error_level": 2,
        "type": "Error_type",
        "desc": "description",
        "line": 4,
        "file_path": "/src/file4.py",
    },
]

RESULT_LIST = [
    {
        "error_level": 1,
        "type": "Error55_type",
        "desc": "description two",
        "line": 4,
        "file_path": "/src/file1.py",
    },
    {
        "error_level": 2,
        "type": "Error_type",
        "desc": "description",
        "line": 4,
        "file_path": "/src/file2.py",
    },
    {
        "error_level": 55,
        "type": "Error_type",
        "desc": "description",
        "line": 4,
        "file_path": "/src/file3.py",
    },
    {
        "error_level": 2,
        "type": "Error_type",
        "desc": "description",
        "line": 4,
        "file_path": "/src/file4.py",
    },
]


class TestBasicFuncitons(unittest.TestCase):

    def test_email_regex(self):
        self.assertTrue(ghs._find_e_mail("hallo@gmail.com"))
        self.assertFalse(ghs._find_e_mail("not@asd"))
        self.assertFalse(ghs._find_e_mail("www.jump.com"))

    def test_list_filter(self):
        self.assertListEqual(ghs.filter_duplicates(MULTIPLES_LIST), RESULT_LIST)

if __name__ == "__main__":
    unittest.main(verbosity=2)