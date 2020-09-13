import os
import pathlib
import sys
import subprocess
import server
import signal
import time
from multiprocessing import Process
import webbrowser
import random
import uuid
import requests
import json
import urllib.parse

CLIENT_ID = '616621932811-in59kvi1eao9mfncbdfg64pa4k0mvj8t.apps.googleusercontent.com'
# secrets are not actually secret in installed apps and that's fine
# https://stackoverflow.com/questions/20725062/oauth-secrets-and-desktop-application
CLIENT_SECRET = 'C3I5aPZrFKKOPuaKUVGSeuAt'
# https://developers.google.com/photos/library/guides/authorization
SCOPES = urllib.parse.quote('https://www.googleapis.com/auth/photoslibrary')
# https://stackoverflow.com/questions/8905864/url-encoding-in-python
REDIRECT_URL = urllib.parse.quote('http://localhost:5000/auth')
CODE_CHALLENGE = str(uuid.uuid4())
STATE = str(int(1000000000* random.random()))

def main():

    print("\n\n\n1. CRON SETUP")
    print('We are going to set up a cron job to run the uploader script every 1 minute')
    print('(please select allow if prompted)\n\n\n')
    input('Press any key to continue...')


    path = pathlib.Path(__file__).parent.absolute()
    python_path = sys.executable
    upload_path = os.path.join(path, 'upload.py')

    # https://unix.stackexchange.com/questions/297374/add-something-to-crontab-programmatically-over-ssh
    cron_command = f'''echo "$(echo '* * * * * {python_path} {upload_path} > /tmp/google_photo_drop.log' ; crontab -l | grep -v '{python_path} {upload_path}')" | crontab -'''

    subprocess.run(cron_command, shell=True)

    print("\n\n\n2. Token Fetch")
    print('Next, we are going to get you a token from google photos using OAuth.')
    print('To do that, we will briefly open a local web server and direct you to the google oauth flow')
    print('\n\n\n')
    input('Press any key to continue...')


    p = Process(target=server.main)
    p.start()
    pid = p.pid


    # https://developers.google.com/identity/protocols/oauth2
    # https://developers.google.com/identity/protocols/oauth2/native-app#create-code-challenge
    endpoint = f'https://accounts.google.com/o/oauth2/v2/auth?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URL}&response_type=code&scope={SCOPES}&code_challenge={CODE_CHALLENGE}&code_challenge_method=plain&state={STATE}'


    webbrowser.open(endpoint)

    auth = None
    now = time.time()
    subprocess.run('rm /tmp/photo_drop_auth.json', shell=True)
    subprocess.run(f'rm {os.path.join(path, "creds.json")}', shell=True)
    try:
        while True:
            # https://www.guru99.com/python-check-if-file-exists.html
            if os.path.exists('/tmp/photo_drop_auth.json'):
                with open('/tmp/photo_drop_auth.json', 'r') as file:
                    # https://stackoverflow.com/questions/39719689/what-is-the-difference-between-json-load-and-json-loads-functions
                    auth = json.load(file)
                    os.remove('/tmp/photo_drop_auth.json')
                    break
            if time.time() > now + 90:
                break
            time.sleep(1)
    except:
        pass
    finally:
        os.kill(pid, signal.SIGINT)

    if not auth:
        print('\n\n\nLOOKS LIKE THE FETCH TIMED OUT! PLEASE TRY AGAIN...\n\n\n')
        sys.exit()

    if auth.get('state') != STATE:
        print('\n\n\nTHERE WAS AN ISSUE FETCHING YOUR TOKEN! PLEASE TRY AGAIN...\n\n\n')
        sys.exit()

    endpoint = 'https://oauth2.googleapis.com/token'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': 'http://localhost:5000/auth',
        'grant_type': 'authorization_code',
        'code': auth.get("code"),
        'code_verifier': CODE_CHALLENGE
    }

    # https://www.kite.com/python/examples/1607/requests-send-a-post-request-with-form-data
    req = requests.post(endpoint, data)
    creds = None
    try:
        creds = req.json()
    except:
        print('\n\n\nLOOKS LIKE THE CREDS ARE INVALID! PLEASE TRY AGAIN...\n\n\n')
        sys.exit()

    if 'access_token' not in creds:
        print('\n\n\nLOOKS LIKE THE CREDS ARE INVALID! PLEASE TRY AGAIN...\n\n\n')
        sys.exit()

    print("\n\n\n3. DRIVE LOCATION")
    print('Enter a location for your drop dir')
    p = input('Location (defaults to ~/Desktop/GooglePhotoDrop): ')
    p = p.replace('_', '')
    if len(p) == 0:
        p = '~/Desktop/GooglePhotoDrop'
    p = os.path.expanduser(p)

    if os.path.exists(p):
        print(f'path {p} already exists, so we will use this existing dir')
    else:
        print(f'creating {p}...')
        try:
            os.makedirs(p)
        except:
            print(F'\n\n\nPATH {p} COULD NOT BE CREATED! PLEASE TRY AGAIN...\n\n\n')
            sys.exit()

    if not os.path.exists(p):
        print(F'\n\n\nPATH {p} COULD NOT BE CREATED! PLEASE TRY AGAIN...\n\n\n')
        sys.exit()



    with open(os.path.join(path, 'creds.json'), 'w+') as file:
        creds['loc'] = p
        file.write(json.dumps(creds))
        
if __name__ == "__main__":
    main()