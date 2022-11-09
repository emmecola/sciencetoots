#!/usr/bin/python3
"""This script listens to public tweets mentioning "Send to @ScienceToots",
it checks if the tweets are replies to another tweet or thread and sends the
replied tweets/threads to Mastodon via @sciencetoots@mstdn.science. An archive
of the tweet IDs already sent prevents the bot from sending multiple times the same
tweet/thread. Images are also included in the messages sent to Mastodon.
"""

# Import modules
import tweepy
import os
import re

# My keys
CONSUMER_KEY = "XXXXXXXXXXXXXXXXXXXXXXX"
CONSUMER_SECRET = "XXXXXXXXXXXXXXXXXXXXXXX"
ACCESS_TOKEN = "XXXXXXXXXXXXXXXXXXXXXXX"
ACCESS_TOKEN_SECRET = "XXXXXXXXXXXXXXXXXXXXXXX"

# My variables
archive_file = '/sciencetoots/archive.txt'
temp_file = '/sciencetoots/temp.txt'
media_folder = '/sciencetoots/media'
keyword = 'Send to @ScienceToots'

# Authenticate
auth = tweepy.OAuth1UserHandler(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

def checkArchive(thread,archive_file):
    tweet_id=thread[-1]["id"]
    with open(archive_file) as file:
        archive = [line.rstrip() for line in file]
    if str(tweet_id) in archive:
        return False
    else:
        o = open(archive_file,'a')
        o.write(str(tweet_id)+"\n")
        o.close()
        return True

def checkAuthor(thread):
    user = thread[-1]["user"]
    for T in thread:
        if T["user"] == user:
            pass
        else:
            return False
    return True

def prepareFirstTweet(T):
    header = T["author"]+ " wrote this:\n\n"
    footer = "\n\nOriginal tweet: https://twitter.com/twitter/statuses/" + str(T["id"])
    return header,footer
    
def writeTweet(idx,T,temp_file,replied_id):
    if idx==0:
        header,footer = prepareFirstTweet(T)
        replyto_string=''
        visibility='public'
    else:
        header,footer = ['','']
        replyto_string='-r '+str(replied_id)+' '
        visibility='unlisted'
    with open(temp_file,'w') as f:
        f.write(header+T["text"]+footer)
    return replyto_string,visibility

def writeMedia(T,media_folder):
    media_string = ''
    for idx,M in enumerate(T["media"]):
        os.popen("wget " + M + " -O " + media_folder + "/" + str(idx))
        media_string = media_string + "-m " + media_folder + "/" + str(idx) + " "
    return media_string

def toot(temp_file,replyto_string,media_string,visibility):
    command_string = "cat " + temp_file + " | toot post -v " + visibility + " " + replyto_string + media_string
    toot_id=os.popen(command_string).read().strip().split('/')[-1]
    return toot_id

def cleanMedia(media_folder):
    os.popen("rm -rf " + media_folder + "/*")

def sendToMastodon(thread):
    replied_id=''
    for idx,T in enumerate(reversed(thread)):        
        replyto_string,visibility = writeTweet(idx,T,temp_file,replied_id)       
        media_string = writeMedia(T,media_folder)
        replied_id=toot(temp_file,replyto_string,media_string,visibility)
        cleanMedia(media_folder)

def getMedia(tweet):
    media_list = list()
    if hasattr(tweet, 'extended_entities'):
        if 'media' in tweet.extended_entities:
            for M in tweet.extended_entities['media']:
                media_list.append(M['media_url_https'])
        else:
            pass
    else:
        pass
    return media_list

def cleanMediaURL(text):
    return re.sub(r'https://t.co/[\w]*',"",text)

class ScienceToot(tweepy.Stream):
    
    def on_status(self, status):
        thread = list()
        valid = 1
        replied_to = status.in_reply_to_status_id
        while replied_to is not None:
            try:
                replied_tweet = api.get_status(replied_to,tweet_mode='extended')
                if replied_tweet.user.protected == True:
                    valid = 0
                    break
            except:
                valid = 0
                break
            media_list = getMedia(replied_tweet)
            thread.append({'id': replied_tweet.id,
                           'user': replied_tweet.user.screen_name,
                           'author': replied_tweet.author.name,
                           'text': replied_tweet.full_text,
                           'media': media_list})
            replied_to = replied_tweet.in_reply_to_status_id
        if len(thread)>0 and valid==1 and checkAuthor(thread) and checkArchive(thread,archive_file):
            sendToMastodon(thread)

def main():
     
    # Initialize instance of the subclass
    mystream = ScienceToot(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_TOKEN,ACCESS_TOKEN_SECRET)

    # Filter realtime Tweets by keyword
    mystream.filter(track=[keyword])

if __name__ == "__main__":
    main()

