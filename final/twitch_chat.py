import sys
import csv
import json
import requests

url = 'https://api.twitch.tv/v5/videos/'
headers = {'client-id':'xoa6ddhh5se2umdxt8iowx2in0155w', 'Accept':'application/vnd.twitchtv.v5+json'}

def main():
    video_id = sys.argv[1]
    count = 0
    params = {'cursor': ''}
    while True:
        r = requests.get(url+video_id+'/comments', headers=headers, params=params)
        if r.status_code==200:
            jsondata = r.json()
            #jsondata = json.loads(r.text)
            with open('chatlog_'+str((int(count/100)))+'.csv', 'a') as csvfile:
                fieldnames = ['id', 'offset_seconds', 'text']
                chatwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
                for comment in jsondata['comments']:
                    chatwriter.writerow({'id': comment['_id'],
                                         'offset_seconds': comment['content_offset_seconds'],
                                         'text': comment['message']['body']})
            count+=1
            if "_next" in jsondata:
                params={'cursor':jsondata['_next']}
            else:
                break




if __name__ == "__main__":
    main()
