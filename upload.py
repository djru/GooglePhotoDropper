import time
import os
import pathlib
import sys
import json
import requests

print(time.time())

path = pathlib.Path(__file__).parent.absolute()
lock = os.path.join(path, '.lock')

if not os.path.exists(os.path.join(path, 'creds.json')):
    print('creds not present, skipping')
    sys.exit()

if os.path.exists(lock):
    print('upload still happening, will skip this round')
    sys.exit()

with open(lock, 'w+'):
    pass

try:
    with open(os.path.join(path, 'creds.json'), 'r') as file:
        creds = json.load(file)
    if 'loc' not in creds or 'access_token' not in creds:
        print('creds are invalid')
        sys.exit()

    upload_dir = creds.get('loc')
    bearer = {'Authorization': 'Bearer ' + creds.get('access_token')}
    print(creds)


    # https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
    files = [f for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))]
    images = [os.path.join(upload_dir, f) for f in files if '.jpg' in f or '.jpeg' in f or '.png' in f or '.gif' in f]
    print(images)



    for i in images:
        
        # https://stackoverflow.com/questions/45868120/python-post-request-with-bearer-token
        # https://stackoverflow.com/questions/39614675/sending-raw-data-in-python-requests
        head = {**bearer,
        'Content-type': 'application/octet-stream',
        'X-Goog-Upload-Content-Type': mime,
        'X-Goog-Upload-Protocol': 'raw'
        }
        mime = 'image/' + i.split('.')[-1].replace('jpg', 'jpeg')


        with open(i, 'rb') as image_file:
            # https://developers.google.com/photos/library/guides/upload-media
            resp = requests.post('https://photoslibrary.googleapis.com/v1/uploads', data=image_file, headers=head)
            token = resp.text


            payload = {
                "newMediaItems": [
                    {
                        "description": i,
                        "simpleMediaItem": {
                            "fileName": i,
                            "uploadToken": token
                        }
                    }
                ]
            }
            resp = requests.post('https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate', json=payload, headers=bearer)
            
            try:
                print(resp.json())
            except:
                print(resp.text)
            
            os.remove(i)
                
except Exception as e:
    print(e)
finally:
    os.remove(lock)


