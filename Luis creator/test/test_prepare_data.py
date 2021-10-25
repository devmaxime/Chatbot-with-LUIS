import unittest
import os

from sources.prepare_data import Prepare

from pandas import read_json

from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from msrest.authentication import CognitiveServicesCredentials

import json
with open("config.json") as f: #Retrieving config from config.json
    _CONFIG = json.load(f)

class TestStringMethods(unittest.TestCase):

    def test_frames(self):
        self.assertTrue(os.path.exists(_CONFIG.get('framesPath')))

    def test_initializeDataFrame(self):
        frames = read_json(_CONFIG.get('framesPath'))
        Data = Prepare(1, frames)

        testUtterance = Data.createLabel('intentTest', Data.prepared_sample.iloc[0])
        trueUtterance = {"text": "i'd like to book a trip to atlantis from caprica on saturday, august 13, 2016 for 8 adults. i have a tight budget of 1700.", "intentName": "intentTest", "entityLabels": [{"startCharIndex": 0, "endCharIndex": 121, "entityName": "ticketBooking", "children": [{"startCharIndex": 41, "endCharIndex": 48, "entityName": "or_city"}, {"startCharIndex": 27, "endCharIndex": 35, "entityName": "dst_city"}, {"startCharIndex": 117, "endCharIndex": 121, "entityName": "budget"}, {"startCharIndex": 62, "endCharIndex": 71, "entityName": "str_date"}]}]}

        self.assertEqual(testUtterance, trueUtterance)