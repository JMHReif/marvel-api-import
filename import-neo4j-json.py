# import dependency packages
import sys
import hashlib
import math
from py2neo import Graph                       # install with `pip install py2neo`
import requests                                # `pip install requests`
from ratelimit import limits                   # `pip install ratelimit`
from datetime import datetime
import json

#variables
url_prefix = 'https://gateway.marvel.com:443/'
TWENTYFOUR_HOURS = 86400
callCount = 0
skipVal = 0

@limits(calls=3000, period=TWENTYFOUR_HOURS)
def call_marvel_api(url):
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime("%Y%m%d %H:%M:%S")
    public_api_key = '<your_public_API_key_here>'
    private_api_key = '<your_private_API_key_here>'
    hashVal = hashlib.md5((timestamp_str + private_api_key + public_api_key).encode('utf-8')).hexdigest()
    full_url = url + '&ts=' + timestamp_str + '&apikey=' + public_api_key + '&hash=' + hashVal

    #print('Full URL: ', full_url)
    r = requests.get(full_url)
    response = json.loads(r.content)

    if r.status_code != 200:
        raise Exception('API response: {}'.format(r.status_code))
    
    return response['data']

def retrieve_characters():
    global url_prefix, skipVal
    url_char_suffix = url_prefix + 'v1/public/characters?orderBy=name&limit=100&offset='
    
    #make initial call to retrieve stats
    url = url_char_suffix + str(skipVal) 
    data = call_marvel_api(url)

    #calc how many more times to call
    totalCharacters = data['total']
    print("Total characters: ", totalCharacters)
    callsNeeded = int(math.ceil(totalCharacters / 100))
    trimmedData = {
            "characters": []
    }

    print("Adding character data to file...")
    for num in range(callsNeeded):
        url = url_char_suffix + str(skipVal)
        data = call_marvel_api(url)

        #trim unwanted data
        characters = data['results']
        for element in characters: 
            del element['comics']['items']
            del element['comics']['returned']
            del element['series']['items']
            del element['series']['returned']
            del element['stories']['items']
            del element['stories']['returned']
            del element['events']['items']
            del element['events']['returned']
            trimmedData['characters'].append(element)

        #increment skip value
        skipVal = skipVal + 100
    
    with open('characters.json', 'a') as characterFile:
        json.dump(trimmedData, characterFile, indent=4)

    print('Call count: ', callsNeeded)

def read_character_file(entity):
    #build url based on file data
    with open('characters.json', 'r') as characterFile:
        fileData = json.load(characterFile)
        jsonObject = {
            "results": []
        }

        for character in fileData['characters']:
            charId = character['id']
            entity_url = character[entity]['collectionURI']
            num_available = character[entity]['available']
            
            if num_available > 0:
                callsNeeded = int(math.ceil(num_available / 100))
                #print("CharId: ", charId, " Calls needed: ", callsNeeded)

                details = {
                    "characterId": charId,
                    "entity": entity,
                    "entity_url": entity_url,
                    "num_available": num_available,
                    "callsNeeded": callsNeeded
                }
                jsonObject['results'].append(details)
    
    return jsonObject

def retrieve_comics():
    global url_prefix, callCount, skipVal
    url_comic = url_prefix + 'v1/public/characters/'
    url_suffix = '/comics?orderBy=title&limit=100&offset='

    charData = read_character_file('comics')

    characterNum = 0
    for character in charData['results']:
        skipVal = 0
        trimmedData = {
            "characterId": character['characterId'],
            "comicNumber": character['num_available'],
            "comics": []
        }
        callsNeeded = int(character['callsNeeded'])
        callCount = callCount + int(callsNeeded)

        if callCount < 3000:
            #print("Adding comic data to file...")
            for num in range(callsNeeded):
                url = url_comic + str(character['characterId']) + url_suffix + str(skipVal)

                data = call_marvel_api(url)
                comics = data['results']

                #trim unwanted data
                for element in comics: 
                    del element['textObjects']
                    del element['creators']['items']
                    del element['creators']['returned']
                    del element['characters']['items']
                    del element['characters']['returned']
                    del element['stories']['items']
                    del element['stories']['returned']
                    del element['events']['items']
                    del element['events']['returned']
                    trimmedData['comics'].append(element)

                #increment skip value
                skipVal = skipVal + 100

            with open('comics.json', 'a') as comicsFile:
                json.dump(trimmedData, comicsFile, indent=4)
                comicsFile.write("\n")
        
            print('Calls needed: ', callsNeeded, ' Call count: ', callCount)
        else:
            print("PAUSE! Halting processing to avoid call limit overage")
            print("Left off with character: ", character['characterId'])
            sys.exit(0)
        
        characterNum = characterNum + 1
        
    print('Number of characters called: ', characterNum)

# def read_creator_file(entity):
#     #FIX!!!
#     #build url based on file data
#     with open('characters.json', 'r') as characterFile:
#         fileData = json.load(characterFile)

#         for character in fileData:
#             charId = character['id']

#             entity_url = character['creators']['collectionURI']
#             num_available = character['creators']['available']
#             print("Total creators for character: ", num_available)

# def retrieve_creators():
#     #FIX!!!
#     global url_prefix, callCount, skipVal

# def retrieve_series():
#     global url_prefix, callCount, skipVal
#     url_series_char = url_prefix + 'v1/public/characters/'

# def retrieve_stories():
#     global url_prefix, callCount, skipVal
#     url_stories_char = url_prefix + 'v1/public/characters/'

# def retrieve_events():
#     global url_prefix, callCount, skipVal
#     url_events_char = url_prefix + 'v1/public/characters/'

if __name__ == '__main__':
    globals()[sys.argv[1]]()