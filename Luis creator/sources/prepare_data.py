import pandas as pd
class Prepare():
    def __init__(self, trainSize: int, frames, testSize: int = 0):
        self.initializeDataFrame(trainSize, frames, testSize)
        self.correctDataFrame()

    def addThousand(self, x):
        """
        If the params is less than 100. Multiply it by 1000.
        """
        if x < 100:
            x = x * 1000
        return x

    def initializeDataFrame(self, trainSize, raw, testSize = 0):
        """
        Extract from a json file all the needed data and put it in a dataframe.
        """
        if(testSize == 0):       
            sample = raw.loc[:trainSize - 1] #If size = 10, we want from 0:9
        elif(testSize > 0):
            sample = raw.loc[trainSize:trainSize + testSize - 1] #Same

        self.prepared_sample = pd.DataFrame(columns=['text', 'or_city', 'dst_city', 'budget', 'str_date', 'end_date'])

        for i in range(0,len(sample)): #Similar to switch
            if(testSize > 0): #Quick fix since the index doesn't start at 0. See line 22.
                i = i + trainSize
            _text = sample.loc[i].turns[0]['text']
            _dst_city = _or_city = _str_date = _end_date = 'none'
            _budget = 0

            if 'dst_city' in raw.loc[i].turns[0]['labels']['frames'][0]['info']:
                _dst_city = raw.loc[i].turns[0]['labels']['frames'][0]['info']['dst_city'][0]['val']

            if 'or_city' in raw.loc[i].turns[0]['labels']['frames'][0]['info']:
                _or_city = raw.loc[i].turns[0]['labels']['frames'][0]['info']['or_city'][0]['val']

            if 'budget' in raw.loc[i].turns[0]['labels']['frames'][0]['info']:
                TEMP = raw.loc[i].turns[0]['labels']['frames'][0]['info']['budget'][0]['val']
                try:
                    _budget = float(TEMP)
                except:
                    _budget = '0'

            if 'str_date' in raw.loc[i].turns[0]['labels']['frames'][0]['info']:
                _str_date = raw.loc[i].turns[0]['labels']['frames'][0]['info']['str_date'][0]['val']

            if 'end_date' in raw.loc[i].turns[0]['labels']['frames'][0]['info']:
                _end_date = raw.loc[i].turns[0]['labels']['frames'][0]['info']['end_date'][0]['val']
                
            _new_row = {'text': _text, 'dst_city': _dst_city, 'or_city': _or_city, 'budget': _budget, 'str_date': _str_date, 'end_date': _end_date}
            self.prepared_sample = self.prepared_sample.append(_new_row, ignore_index=True)
        
    def correctDataFrame(self):
        """
        Apply manual corrections. Convert budget to integer (not type but real integer). Convert text to lower case.
        """
        self.prepared_sample['budget'] = self.prepared_sample['budget'].astype(str).astype(float)
        self.prepared_sample['budget'] = self.prepared_sample['budget'].transform(self.addThousand)
        self.prepared_sample['budget'] = self.prepared_sample['budget'].astype(int).astype(object) 

        self.prepared_sample['text'] = self.prepared_sample['text'].str.lower()
        self.prepared_sample['or_city'] = self.prepared_sample['or_city'].str.lower()
        self.prepared_sample['dst_city'] = self.prepared_sample['dst_city'].str.lower()           

    def createLabel(self, intentName, row):
        """
        Convert a dataframe into a usable luis json label according to the required architecture.
        """
        _position = [] #or_city	dst_city	budget	str_date	end_date
        args = ['or_city',	'dst_city',	'budget',	'str_date',	'end_date']
        #print(row.text)
        
        for arg in args: #Loop for each args
            r_arg = str(row[arg])
            if(r_arg != 'none'): #Check if arg is not None
                _start = row.text.find(r_arg)
                if(_start == -1 or r_arg == '0'): #if error finding the word
                    _position.append([0, 0])
                else:
                    _end = _start + len(r_arg)
                    _position.append([_start, _end])
            else:
                _position.append([0, 0])


        _label = {
            "text": row.text,
            "intentName": intentName,
            "entityLabels": [
                {
                    "startCharIndex": 0,
                    "endCharIndex": len(row.text) - 1,
                    "entityName": "ticketBooking",
                    "children": [
                        {
                        "startCharIndex": _position[0][0],
                        "endCharIndex": _position[0][1],
                        "entityName": "or_city",
                        },
                        {
                        "startCharIndex": _position[1][0],
                        "endCharIndex": _position[1][1],
                        "entityName": "dst_city",
                        },
                        {
                        "startCharIndex": _position[2][0],
                        "endCharIndex": _position[2][1],
                        "entityName": "budget",
                        },
                        {
                        "startCharIndex": _position[3][0],
                        "endCharIndex": _position[3][1],
                        "entityName": "str_date",
                        },
                        {
                        "startCharIndex": _position[4][0],
                        "endCharIndex": _position[4][1],
                        "entityName": "end_date",
                        }
                    ]
                }
            ]
        }
        
        _toRemove = [] #Delete empty childrens

        for index, _pos in  enumerate(_position):
            
            if(_pos == [0, 0]):
                #print(_label['entityLabels'][0]['children'][index]['entityName'])
                _toRemove.append(_label['entityLabels'][0]['children'][index]['entityName'])
                
        for rem in _toRemove:
            #print(rem)
            for i in range(0, len(_label['entityLabels'][0]['children'])):
                if _label['entityLabels'][0]['children'][i]["entityName"] == rem:
                    _label['entityLabels'][0]['children'].pop(i)
                    break
      
        return _label