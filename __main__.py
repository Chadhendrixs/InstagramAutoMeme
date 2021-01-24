import os
import json
import time
import requests
from PIL import Image
from instabot import Bot
from secrets import IGlogin
import atexit


#Global is gross, but currently easier. May change.
usedUrl = []
bot = Bot()

#Exit handler to log out of account.
def exitHandler():
    global bot
    bot.logout()

#Login function. Using API login instead of regular bot login, due to current issue with instabot.
#use_cookies and use_uuid are helpful for faster logins, but leads to bugs with instabot.
#Make sure to update the username and password in `secrets.py`
def login():
    global bot
    try:
        bot.api.login(username = IGlogin.user, password = IGlogin.password, use_cookie=False, use_uuid=False)
    except Exception as e:
        print("ERROR!")
        print(e)
        print("---")
        print("Login error! Please make sure you have an internet connection!")

#Daily cache of reddit URLs. Clear after a day, but carry over the last 25.
def cache():
    global usedUrl
    if len(usedUrl) == 96:
        freshUrl = []
        for x in range(25):
            freshUrl.append(usedUrl[-(-x+25)])
        usedUrl = freshUrl
    return

#Json data structure:
#          data
#        children
#      1, 2, ..., 25
#          data
#    url, over_18, ...

#Grab image URL, add it to Cache.
#Change 'dankmemes' to whatever subreddit you want.
def getImage():
    global usedUrl
    try:
        json_raw = requests.get("https://www.reddit.com/r/dankmemes/new/.json", headers = {'User-agent': '15MinuteMeme'}).json()
    except Exception:
        usedUrl.append("!!ERROR!!")
        return
    json_data = json_raw['data']['children']
    for number in range(len(json_data)):
        json_post = json_data[number]['data']
        if json_post['url'] in usedUrl: #Json data checks
            pass
        elif "https://i.redd.it/" not in json_post['url']:
            pass
        elif json_post['over_18']:
            pass
        elif "jpg" not in json_post['url'].split('.'):
            if "png" not in json_post['url'].split('.'):
                pass
            else:
                usedUrl.append(json_post['url'])
                break
        else:
            usedUrl.append(json_post['url'])
            break
    return

#Convert png to jpg
def convert(file):
    filename = file.replace(".png", ".jpg")
    im = Image.open(file)
    im = im.convert("RGB")
    im.save(filename)
    os.remove(file)
    return filename

#Download image
def download():
    global usedUrl
    url = usedUrl[-1]
    if url == "!!ERROR!!":
        return False
    file = url.replace("https://i.redd.it/", "")
    f = open(file, 'wb')
    f.write(requests.get(url).content)
    f.close()
    if file.split('.')[-1] != "jpg":
        file = convert(file)
    return file

#Upload and delete
#Change captions to whatever you want.
def upload(file):
    global bot
    try:
        bot.api.upload_photo(file, caption="#meme #memes #15minutememes", force_resize=True)
    except Exception as e:
        print("ERROR!")
        print(e)
        print("---")
        print("Upload error! Please make sure you have an internet connection!")
        return
    try:
        os.remove(file + '.REMOVE_ME')
    except Exception:
        os.remove(file + '.CONVERTED.jpg.REMOVE_ME')
        os.remove(file)
    return

#Main loop. This will create the exit handler to logout, and then login.
#It will then check/clear cache, get a new image, download and upload, then wait 15 minutes.
def main():
    atexit.register(exitHandler)
    login()
    while True:
        cache()
        getImage()
        file = download()
        if file == False:
            print("Bot error! No connection or upload failed!")
        else:
            upload(file)
        time.sleep((15*60)) #(time in minutes*60)

main()
