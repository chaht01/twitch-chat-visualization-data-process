import sys
import csv
import json
import requests
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
secret_file = os.path.join(BASE_DIR, 'secrets.json')

with open(secret_file) as f:
    secrets = json.loads(f.read())


def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise error_msg

CLIENT_KEY = get_secret("SECRET_KEY")


url = 'https://api.twitch.tv/v5/videos/'
headers = {'client-id':CLIENT_KEY, 'Accept':'application/vnd.twitchtv.v5+json'}

def main():
    video_id = sys.argv[1]
    count = 0
    params = {'cursor': ''}
    while True:
        r = requests.get(url+video_id+'/comments', headers=headers, params=params)
        jsondata = json.loads(r.text)
        with open('chatlog_'+str((int(count/100)))+'.csv', 'a') as csvfile:
            fieldnames = ['created_at', 'commenter', 'text']
            chatwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for comment in jsondata['comments']:
                chatwriter.writerow({'created_at':comment['created_at'], 'commenter':comment['commenter']['display_name'], 'text':comment['message']['body']})
        count+=1
        if "_next" in jsondata:
            params={'cursor':jsondata['_next']}
        else:
            break




if __name__ == "__main__":
    main()
