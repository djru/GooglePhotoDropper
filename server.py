from flask import Flask, request
import json

def main():
    server = Flask(__name__)

    @server.route('/auth')
    def auth():
        with open('/tmp/photo_drop_auth.json', 'w+') as file:
            # https://stackoverflow.com/questions/11774265/how-do-you-get-a-query-string-on-flask
            file.write(json.dumps(request.args))
        return 'SUCCESS! you can close this tab now...'
    

    server.run('0.0.0.0')

if __name__ == "__main__":
    main()