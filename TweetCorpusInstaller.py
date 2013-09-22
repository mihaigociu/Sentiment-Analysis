from twython import Twython
from twython.exceptions import TwythonError
import re
import csv
import time
import os
from os import path
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# using - http://sananalytics.com/lab/twitter-sentiment/
# converted into the new twitter api

# download tweet sentiments from twitter
# and save the date based on the sentiment
# t = TweetCorpusInstaller()
# init the tweeter api
# t.initTwython()
# install the twitter corups
# this will take around 18 hours dew to twitter api limits - 300 requests per hour
# t.install('twittercorups')

# you can process the data downlowded into text docs which will only contain the relevant words to each category
# t.processSentiments('twittercorups/positive.csv', 'twittercorups/positive.txt')
# t.processSentiments('twittercorups/negative.csv', 'twittercorups/negative.txt')
# t.processSentiments('twittercorups/neutral.csv', 'twittercorups/neutral.txt')
# t.processSentiments('twittercorups/irrelevant.csv', 'twittercorups/irrelevant.txt')
class TweetCorpusInstaller(object):


    def __init__(self):
        print 'TweetCorpusInstaller'
#         we'll use these to filter words which are not relevant
        self.tweetCorpusStopWords = ['sandwich', 'ice', 'cream', 'itunes', 'Words', 'facebook', 'windows', 'iphones', 'ios5', 'ios6', 'ios7', 'ios', 'ipads', 'ipads' 'apple', 'google', 'phone', 'iphone', 'steve', 'microsoft', 'twitter', 'app', 'apps', 'siri', 'mac', 'macbook', 'ipad', 'android', 'nexus', 'galaxy', 'smartphone', 'this']
#         a dict to sort the categories of our sentiments
        self.categories = {}

#     init the Twython api and set up the tweeter credentials
    def initTwython(self):
        APP_KEY = 'Your_API_KEY'
        APP_SECRET = 'YOUR_API_SECRET'
        twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
        ACCESS_TOKEN = twitter.obtain_access_token()
        self.twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
        
#     clean - tokenize a tweet and return its items as a list
    def tweetToList(self, tweet):
        t = self.removetags(str(tweet))
        return self.removeStopWords(self.tokenize(t))
        
#    remove tags and urls from a tweet
    def removetags(self, tweet):
#         remove hashtags and at mentions
        s = re.sub(r'\@\w+|\#\w+', "", tweet)
#         remove urls
        s = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', s)
#         remove all punct
        return re.sub(r'[^\w\s]','',s)
        
        
#     tokenize a tweet
    def tokenize(self, tweet):
        return word_tokenize(tweet)
    
#     remove stop words from a tweet
    def removeStopWords(self, words):
        return [w.lower() for w in words if not w in stopwords.words('english') and len(w) >= 3 and not w in self.tweetCorpusStopWords]
    
#     return a tweet object (or False) based on id
    def getTweet(self, tweetid):
        try:
            status = self.twitter.show_status(id=tweetid)
        except TwythonError:
            print tweetid, 'Twitter API returned a 404 (Not Found)'
            return False
        else:
            return { 'text': str( status['text'] ), 'date': status['created_at'] }
    
#     load a csv file and process its data - tweet id's, topics and sentiments to a list
#     we'll call this function to load the original data we want to get from twitter
    def readCSVcorpus(self, filename ):
        fp = open(filename, 'rb')
        reader = csv.reader( fp, delimiter=',', quotechar='"' )
        tweetslist = [ row for row in reader ]
        fp.close()
        return tweetslist 
    
#     when we are done, we'll use this funciton to save the data into 
#     coresponding csv files for each of the categories
    def saveCSVCorpus(self, dir):
        for cat in self.categories:
            f = dir + '/' + cat + '.csv'
            fp = open( f, 'wb' )
            writer = csv.writer( fp, delimiter=',', quotechar='"', escapechar='\\', quoting=csv.QUOTE_ALL )
            writer.writerow( ['Topic','Sentiment','Id','Date','Text', 'Words' ] )
            tweets = self.categories[cat]
            for item in tweets:
                writer.writerow( item )
                print '--> Saving: ', item[2], '::', item[4]
            fp.close()
        
#     add a tweet into one of the sentiments categories
    def addToCategories(self, item):        
        tweet = self.getTweet(item[2])
        if tweet != False:
            cat = item[1]
            tokens = self.tweetToList(tweet['text'])
            o = [item[0], item[1], item[2], tweet['date'], tweet['text'], tokens]
            if cat in self.categories:
                self.categories[cat].append(o) 
            else:
                self.categories[cat] = [o]
            print '--> addToCategories', item[1], "--> ", tweet['text'], ' :: ', tokens

            
#     return the time left for the whole tweet batch fo be completed
    def get_time_left_str( self, cur_idx, fetch_list_len, download_pause ):
        tweets_left = fetch_list_len - cur_idx
        total_seconds = tweets_left * download_pause    
        str_hr = int( total_seconds / 3600 )
        str_min = int((total_seconds - str_hr*3600) / 60)
        str_sec = total_seconds - str_hr*3600 - str_min*60
        return '%dh %dm %ds' % (str_hr, str_min, str_sec)

#     a loop with pause to download the tweets and save them into a file
#     note this will take around 18 hours since you can only download around 350
#     tweets per hour (twitter api limits)
    def install(self, dir):
        fetch_list = self.readCSVcorpus(dir +'/TweetcorpusInstall.csv')
        # stay within rate limits
        max_tweets_per_hr  = 300
        download_pause_sec = 3600 / max_tweets_per_hr
        
        # ensure raw data directory exists
        if not os.path.exists( dir ):
            os.mkdir( dir )
        
        # download tweets
        for idx in range(0 ,len(fetch_list)):
            # current item
            item = fetch_list[idx]
            
#             load the tweet and save it to the right file
            self.addToCategories(item)
                        
            # print status
            trem = self.get_time_left_str( idx, len(fetch_list), download_pause_sec )
            print '--> downloading tweet #%s (%d of %d) (%s left)' % \
                (item[2], idx+1, len(fetch_list), trem)          
             
#             # stay in Twitter API rate limits 
            print '    pausing %d sec to obey Twitter API rate limits' % \
                (download_pause_sec) 
            time.sleep( download_pause_sec )
            
#         save the data into the corpus files
        self.saveCSVCorpus(dir)
        
        print '--> Tweet Corpus Installation Completed <--'
        return
        
#     once we saved the complete data we can minimize it 
#     and save only the clean lists into our corups
    def processSentiments(self, source, destination):
        fp = open(source, 'rb')
        reader = csv.reader( fp, delimiter=',', quotechar='"' )
        f =  destination
        writer = open( f, 'wb' )
        for row in reader:
            o  = self.tweetToList(row[5])
            if len(o) > 0:
                s = ','.join(o)
                writer.write( s + '\n')
        writer.close()
        fp.close()

        
