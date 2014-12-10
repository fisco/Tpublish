import configparser
import datetime
import os
import pickle
import re
import subprocess
import tweepy

os.chdir(os.path.dirname(os.path.realpath(__file__)))
if not (os.path.isdir('_files')):
    os.makedirs('_files')

config = configparser.ConfigParser()
config.read('config.ini')
# Handle items in configuration file:
try:
    twitter_consumer_key = config['Twitter']['consumer_key']
    twitter_consumer_secret = config['Twitter']['consumer_secret']
    twitter_auth_access_key = config['Twitter']['auth_access_key']
    twitter_auth_access_secret = config['Twitter']['auth_access_secret']
except:
    print('You have an error in config.ini.')
    exit()

auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
auth.set_access_token(twitter_auth_access_key, twitter_auth_access_secret)
tweepy_api = tweepy.API(auth)

public_tweets = tweepy_api.user_timeline(count=1000)
try:
    f = open('tweets.pickle', 'rb')
    old_tweet_list = pickle.load(f)
    f.close()
    list_of_current_ids = [x.id for x in public_tweets]
    old_tweet_residual_list = [x for x in old_tweet_list if x.id not in list_of_current_ids]
    public_tweets = old_tweet_residual_list + public_tweets
    os.remove('tweets.pickle')
except:
    print('Existing tweet list not stored.')
f = open('tweets.pickle', 'wb')
pickle.dump(public_tweets, f, -1)
f.close()

# WEBSITEUPDATES
publishable_list = [x for x in public_tweets if re.match(r"^#WebSiteUpdate", x.text) ]
publishable_list.sort(key=lambda x: x.created_at, reverse=True)
html_snippet = '<div class="TPublish" style="margin-top: 2em; text-align: center;">'
last_date = ''
for tweet in publishable_list:
    current_date = tweet.created_at.strftime("%d %B %Y")
    text = tweet.text[14:]
    url = re.search('(https?://[^ ]+)', text)
    if not current_date == last_date:
        html_snippet += '<h4>' + re.sub('^0', '', tweet.created_at.strftime("%d %B %Y")) + '</h4>'
    text = re.sub('^:', '', text)
    text = re.sub(' #', ' ', text)
    text = re.sub('(https?://[^ ]+)', '', text)
    text = re.sub(': *$', '', text)
    html_snippet += '<p><a href="' + url.group(1) + '">' + text.strip() + '</a></p>'
    last_date = current_date
html_snippet += '</div>'
f = open('_files/websiteupdates.html', "w")
f.write(html_snippet)
f.close()
os.chdir('/home/fisco/Documents/Dropbox/jekyll/davidfisco.com/www/_site/')
full_text = open('index.html', 'r').read()
open('index.html', 'w').write(re.sub(r'(<!-- BEGIN TPUBLISH WEBSITEUPDATES -->).*(<!-- END TPUBLISH WEBSITEUPDATES -->)', r'\1' + html_snippet + r'\2', full_text, flags=re.DOTALL))
subprocess.call('git add .', shell=True)
subprocess.call('git commit -am "Website update from tpublish.py."', shell=True)
subprocess.call('. ~/.keychain/`/bin/hostname`-sh; git push -u origin master:gh-pages', shell=True)
