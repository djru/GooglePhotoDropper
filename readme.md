# Google Photo Drop
## Automatically Upload Photos in a Folder to Google Photos

## How it works
Photo Drop creates a cron job that checks on your directory every one minute. If it detects anything with the extension .jpg, .jpeg, .png or .gif, it will upload it to your google photos account and DELETE IT.

## Why does it delete the photos?
I wrote this to be a quick and easy way to get photos from my macbook (mostly memes I save from reddit) into Google Photos. Uploading and then deleting them is the use case I was trying to solve for. If you want a full service sync solution, use dropbox or something designed for sync...

## How do I know this is safe?
Well it's open source and the code is pretty simple. Feel free to dig into it yourself.


## Setup

1. Clone the repo
2. Run `pip intall -r google_photo_drop/requirements.txt`
3. Run `python google_photo_drop/setup.py` (requires python >=3.7)
4. When prompted, give the app permission to create the cron job
5. When prompted, log in with Google
6. When prompted, enter a default location for your folder
7. IF YOU ARE ON MAC OS CATALINA: for most folder locations (including `~/Desktop/*`), you will need to give cron full disk access, which is annoying. Sorry, but Apple hates power users...
8. Go to `System Preferences > Security & Privacy > Privacy > Full Disk Access`
9. Click the padlock to make a change
10. Hit the `+` button
11. Hit `⌘ + ⇧ + g` (command + shift + g) and enter `/user/sbin`
12. Select `cron` and then click `Open`
