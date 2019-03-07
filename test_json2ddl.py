"""
Project moved to git@github.com:archgroove/json2ddl.git

Test json2ddl
"""

import unittest
from json2ddl import json_field_to_string

class TestJson2AthenaDDL(unittest.TestCase):
    """Test json2ddl"""

    def test_struct(self):
        """Test that a struct is generated correctly"""
        jsondata = {'metadata':
                        {'filename': 'something',
                         'info': 'something'
                        }
                    }
        expected = '`metadata` struct<filename:string, info:string>'
        string = ''
        for key, value in jsondata.items():
            string += json_field_to_string(key, value)
        self.assertEqual(expected, string)

    def test_nested_struct(self):
        """Test that a nested struct is generated correctly"""
        jsondata = {'metadata':
                        {'field1': 'something',
                         'field2': {'field3': 'something',
                                    'field4': 'something'}
                        }
                    }
        expected = '`metadata` struct<field1:string, field2:struct<field3:string, field4:string>>'
        string = ''
        for key, value in jsondata.items():
            string += json_field_to_string(key, value)
        self.assertEqual(expected, string)

    def test_struct_in_lst(self):
        """Test that we can generate a list of structs"""
        jsondata = {'metadata':
                        [{'field3': 'something', 'field4': 'something'},
                         {'field3': 'something', 'field4': 'something'}
                        ]
                    }
        expected = '`metadata` array<struct<field3:string, field4:string>>'
        string = ''
        for key, value in jsondata.items():
            string += json_field_to_string(key, value)
        self.assertEqual(expected, string)
