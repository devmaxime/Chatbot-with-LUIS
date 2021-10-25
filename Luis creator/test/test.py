import unittest
from pandas import read_json
import json
with open("config.json") as f: #Retrieving config from config.json
    _CONFIG = json.load(f)

class TestStringMethods(unittest.TestCase):

    def test_config(self):
        self.assertEqual(len(_CONFIG), 9)

    def test_trainTestSize(self):
        frames = read_json(_CONFIG.get('framesPath'))
        self.assertGreaterEqual(len(frames), _CONFIG.get('testSize') + _CONFIG.get('trainSize'))
