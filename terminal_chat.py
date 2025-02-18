import requests
import json
import config

def is_json(data):
    try:
        json.loads(data)
        return True
    except json.JSONDecodeError:
        return False

indexUrl = 'http://127.0.0.1:' + config.DEFAULT_PORT 
queryUrl = 'http://127.0.0.1:' + config.DEFAULT_PORT + '/api/query'
clearUrl = 'http://127.0.0.1:' + config.DEFAULT_PORT + '/api/query/clear'
cleanupUrl = 'http://127.0.0.1:' + config.DEFAULT_PORT + '/api/query/cleanup'

#used to store chat history for this user
id=config.DEFAULT_USERID

response = requests.get(indexUrl)
print(response.text)

status = True
while status:
    query = input('Enter your query: ')
    if query != "":        
        if query == "clear":
            data = {"id" : id}
            response = requests.post(clearUrl, json=data)
        elif query == "exit" or query == "bye" or query == "quit":
            data = {"id" : id}
            #response = requests.post(queryUrl, json=data)
            #clear the cache
            response = requests.post(cleanupUrl, json=data)
            status = False
        else:
            data = {"query": query, "id" : id}
            response = requests.post(queryUrl, json=data)
            rj = response.json()
            #print(rj)
            rjresp = rj["response"]
            if is_json(rjresp):
                answer = json.loads(rjresp)
                prettyJson = json.dumps(answer, indent=4)
                print(prettyJson)
            else:
                print(rjresp)
    else:
        data = {"query": query, "id" : id}
        response = requests.post(queryUrl, json=data)
        status = False
