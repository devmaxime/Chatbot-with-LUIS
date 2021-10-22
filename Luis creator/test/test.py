import unittest
import os
import json
with open("config.json") as f: #Retrieving config from config.json
    CONFIG = json.load(f)

class TestStringMethods(unittest.TestCase):

    def test_config(self):
        self.assertEqual(len(CONFIG), 8)
