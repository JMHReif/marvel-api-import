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
url_prefix = 'http://gateway.marvel.com/'
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
            "results": []
    }

    print("Adding character data to file...")
    for num in range(1,callsNeeded):
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
            trimmedData['results'].append(element)

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

        for character in fileData['results']:
            charId = character['id']

            if entity == 'comics':
                entity_url = character['comics']['collectionURI']
                num_available = character['comics']['available']
                #print("Total comics for character: ", num_available)
            elif entity == 'events':
                entity_url = character['events']['collectionURI']
                num_available = character['events']['available']
                print("Total events for character: ", num_available)
            elif entity == 'series':
                entity_url = character['series']['collectionURI']
                num_available = character['series']['available']
                print("Total series for character: ", num_available)
            elif entity == 'stories':
                entity_url = character['stories']['collectionURI']
                num_available = character['stories']['available']
                print("Total stories for character: ", num_available)
            else:
                print('Entity does not exist!')
            
            callsNeeded = int(math.ceil(num_available / 100))
            print("CharId: ", charId, " Calls needed: ", callsNeeded)

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
    url_comic_params = '?orderBy=title&limit=100&offset='

    charData = read_character_file('comics')
    trimmedData = {
        "results": []
    }

    for character in charData['results']:
        callsNeeded = character['callsNeeded']
        if callsNeeded > 0:
            callCount = callCount + int(callsNeeded)
            if callCount < 3000:
                print("Adding comic data to file...")
                for num in range(1,callsNeeded):
                    url = character['entity_url'] + url_comic_params + str(skipVal)

                    data = call_marvel_api(url)
                    comics = data['results']

                    #trim unwanted data
                    for element in comics: 
                        del element['creators']['items']
                        del element['creators']['returned']
                        del element['characters']['items']
                        del element['characters']['returned']
                        del element['stories']['items']
                        del element['stories']['returned']
                        del element['events']['items']
                        del element['events']['returned']
                        trimmedData['results'].append(element)

                    #increment skip value
                    skipVal = skipVal + 100

                with open('comics.json', 'a') as comicsFile:
                    json.dump(trimmedData, comicsFile, indent=4)
                    #comicsFile.write("\n")
        
                print('Calls needed: ', callsNeeded, ' Call count: ', callCount)
            else:
                print("PAUSE! Halting processing to avoid call limit overage")
                print("Left off with character: ", character['id'], ' - ', character['name'])
                sys.exit(0)

#def read_creator_file(entity):
    #FIX!
    #build url based on file data
    #with open('comics.json', 'r') as comicFile:
        #fileData = json.load(comicFile)

        #for comic in fileData:
            #comicId = comic['id']

            #entity_url = comic['creators']['collectionURI']
            #num_available = comic['creators']['available']
            #print("Total creators for comic: ", num_available)

#def retrieve_creators():
    #FIX!
    #global url_prefix, callCount, skipVal

#def retrieve_series():
    #global url_prefix, callCount, skipVal
    #url_series_char = url_prefix + 'v1/public/characters/'

#def retrieve_stories():
    #global url_prefix, callCount, skipVal
    #url_stories_char = url_prefix + 'v1/public/characters/'

#def retrieve_events():
    #global url_prefix, callCount, skipVal
    #url_events_char = url_prefix + 'v1/public/characters/'

if __name__ == '__main__':
    globals()[sys.argv[1]]()