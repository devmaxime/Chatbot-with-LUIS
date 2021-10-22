# Chatbot-with-LUIS
A chatbot that use an azure cognitif service called LUIS to interpret the message of the user.

## How does it works ?

You have two app : Luis creator and Bot. You have to run the luis creator first than the bot.
1. Luis creator is an python application that logging to your luis account, initialize a luis application, prepare data and upload conversation examples into the luis app. Once it's done, it trains the luis application and publish it.
2. Bot is an node.js application that is creating an API for the bot. You can can use Bot Framework Emulator to try the API.

## How to use Luis creator
1. You have to create an `authoring.json` file into `Luis creator/auth/`. It must contains your `authoringKey` and your `authoringEndpoint`.</br>
Here is an example of the `authoring.json` file :
```
{
    "authoringKey" : "yourkey",
    "authoringEndpoint" : "yourendpoint"
}
```
2. You must create an virtual environnement and install the `requirements.txt` file.
</br>Once your virtual environnement is activate, you can use `pip install -r requirements.txt`.
3. You can now execute the `main.py` python file.

## How to use Bot
1. You must create an `.env` file at the root of the Bot folder.
</br> I must contains your luis application AppId, APIKey and APIEndpoint. You must also add your instrumentation key from your Insight ressource.
</br>Here is an example of the `.env` file :
```
LuisAppId="yourLuisAppId"
LuisAPIKey="yourLuisApiKey"
LuisAPIHostName="yourLuisApiHostName"
InstrumentationKey="yourInstrumentationKey"
```
2. You must install the packages declared in `package.json` by using the `npm install` command.
3. You can now start the NodeJs API by using the `npm start` command.

## How to test
1. Open Bot Framework Emulator
2. Click on `Open Bot`
3. In `Bot URL`, enter your bot url. If you are testing in localhost, you must enter `http://localhost:3978/api/messages`.
4. You can now talk with the bot.

# What to expect from the bot ?
The Luis creator must have train a luis app that contains more than 500 examples. You must have an ml entity with 5 parameters : `or_city`, `dst_city`, `budget`, `str_date`, `end_date`.
The luis app must being able to extract those parameters from a sentence like the following one : 
```
Hello, I'm looking to book a flight to Paris from Marseille. I want to travel on 26 august 2021 and come back on 28 august 2021. My budget is $2500.
```
- The bot must call the luis app on the first sentence and ask a serie of questions if some parameters are missing from the luis app's response.
- At the end of the conversation, you must confirm if the bot got the correct information. If you answer `no`, the NodeJs application will create a Trace to the telemetry which contains all the informations about the conversation.
- In your Insight application, you can add a rule that alert you if the bot receives too much `no` for a given period.

![Screenshot](/Blob/screenshot.png)
