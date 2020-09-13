import time
import os
import pathlib
import sys
import json
import requests
from setup import CLIENT_ID, CLIENT_SECRET

print(time.time())

path = pathlib.Path(__file__).parent.absolute()
lock = os.path.join(path, '.lock')


# need to make sure creds.json is there
if not os.path.exists(os.path.join(path, 'creds.json')):
    print('creds not present, skipping')
    sys.exit()

# if the lock is present, don't start another job
if os.path.exists(lock):
    print('upload still happening, will skip this round')
    sys.exit()

# create the lock
with open(lock, 'w+'):
    pass

try:
    # load the creds
    with open(os.path.join(path, 'creds.json'), 'r') as file:
        creds = json.load(file)
    
    # check to see if it's malformed
    if 'loc' not in creds or 'access_token' not in creds:
        print('creds are invalid')
        sys.exit()
    
    # refresh the token
    head = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': creds.get('refresh_token'),
        'grant_type': 'refresh_token'

    }
    resp = requests.post('https://oauth2.googleapis.com/token', data, headers=head)
    token = resp.json().get('access_token')
    print(resp.json())

    # make sure the refreshed token is valid
    if not token:
        print('failed to refresh your token')
        sys.exit()

    # update the loc for these new creds
    new_creds = resp.json()
    new_creds['loc'] = creds.get('loc')

    # store the new creds in the file
    with open(os.path.join(path, 'creds.json'), 'w') as file:
        file.write(json.dumps(new_creds))

    # now we have our location and token
    upload_dir = creds.get('loc')
    bearer = {'Authorization': 'Bearer ' + creds.get('access_token')}


    # get a list of files to upload
    # https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
    files = [f for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))]
    images = [os.path.join(upload_dir, f) for f in files if '.jpg' in f or '.jpeg' in f or '.png' in f or '.gif' in f]
    print(images)


    # iterate over them
    for i in images:
        # figure out the mime type
        mime = 'image/' + i.split('.')[-1].replace('jpg', 'jpeg')
        # https://stackoverflow.com/questions/45868120/python-post-request-with-bearer-token
        # https://stackoverflow.com/questions/39614675/sending-raw-data-in-python-requests
        head = {**bearer,
        'Content-type': 'application/octet-stream',
        'X-Goog-Upload-Content-Type': mime,
        'X-Goog-Upload-Protocol': 'raw'
        }

        # open the file AS BINARY
        with open(i, 'rb') as image_file:
            # first we upload the raw bits
            # https://developers.google.com/photos/library/guides/upload-media
            resp = requests.post('https://photoslibrary.googleapis.com/v1/uploads', data=image_file, headers=head)

            # google gives us back a token (so many tokens!)
            token = resp.text

            # now we create a "media item" which is google parlance for an image that shows up in a users library
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
            
            # delete this photo
            os.remove(i)
                
except Exception as e:
    print(e)
    raise
finally:
    # we are done, so remove the lock
    os.remove(lock)


