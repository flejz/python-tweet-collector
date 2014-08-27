#libs
import requests #requests lib to rest apis
import base64 #base 64 encoder decores
import json #json par ser
import thread #thread controller
import os #operatinoal system libs
import arcpy #arcgis python scripts
import datetime as dateutils
import time
import shutil, errno

#libs twitter
import oauth2 as oauth
import urllib2 as urllib
from urllib import urlencode as urlencode

from xml.dom import minidom #xml parser

#utils
class Utils:

    def copyanything(self, src, dst):
        try:
            shutil.copytree(src, dst)
        except OSError as exc: # python >2.5
            if exc.errno == errno.ENOTDIR:
                shutil.copy(src, dst)
            else: raise

    def normalizeDateNames(self, dateString):

        dayGiven  = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
        dayBrasil = ['Dom','Seg','Ter','Qua','Qui','Sex','Sab']

        for index in range(len(dayGiven)):
            dateString = str.replace(dateString, dayGiven[index], dayBrasil[index])

        monthGiven  = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        monthBrasil = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']

        for index in range(len(monthGiven)):
            dateString = str.replace(dateString, monthGiven[index], monthBrasil[index])

        return dateString;

    def tryStr(self, value):
        try:
            return str(value)
        except:
            return ''

    def tryFloat(self, value):
        try:
            return float(value)
        except:
            return 0

    def tryInt(self, value):
        try:
            return int(value)
        except:
            return 0

#class
class Twitter:

    #constructor
    def __init__(self, auth):
        #oauth vars
        self.api_key = auth['api_key']
        self.api_secret = auth['api_secret']
        self.access_token_key = auth['access_token_key']
        self.access_token_secret = auth['access_token_secret']


    #requesting
    def request(self, url, method='GET'):
        #creating the oauth
        oauth_api   = oauth.Consumer(key=self.api_key         , secret=self.api_secret)
        oauth_token = oauth.Token   (key=self.access_token_key, secret=self.access_token_secret)

        #creating the request
        req = oauth.Request.from_consumer_and_token(oauth_api,
                                                   token=oauth_token,
                                                   http_method=method,
                                                   http_url=url, 
                                                   parameters=[])

        #signing in
        req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), oauth_api, oauth_token)

        #getting the new url
        url = req.to_url()

        #creating the opener director
        http_handler  = urllib.HTTPHandler(debuglevel=0)
        https_handler = urllib.HTTPSHandler(debuglevel=0)

        opener = urllib.OpenerDirector()
        opener.add_handler(http_handler)
        opener.add_handler(https_handler)

        #returning the stream
        return opener.open(url, None)

    #tracking
    def track(self, tags):

        #the query parameters
        query_params = {
            'include_entities': 0,
            'stall_warning': 'true',
            'track': tags}
    
        #twitter url
        #url = "https://stream.twitter.com/1.1/statuses/sample.json"
        url = 'https://stream.twitter.com/1.1/statuses/filter.json?' + urlencode(query_params)

        #returns the response
        response = self.request(url)
        return response

#esri class
class ESRI:

    #constantsre
    fields = ['USER_GEO_ENABLED','USER_ID','USER_SCREEN_NAME','USER_NAME','TWEET_ID','TWEET_CREATED_AT','TWEET_FAVORITE_COUNT', 'TWEET_RETWEET_COUNT','TWEET_TEXT','PLACE_NAME','CREATED_AT','SHAPE@']

    #attributes
    featureClass = None
    featureClassPath = None

    featureCursor = None

    #adds all the tweets
    def add(self, tweet, hashtag):

        twitterCreatedAt = dateutils.datetime.strptime(utils.normalizeDateNames(str(tweet['created_at'])), '%a %b %d %H:%M:%S +0000 %Y')
            
        if tweet['coordinates']: 
            coordinatesPoint = arcpy.Point(tweet['coordinates']['coordinates'][0] , tweet['coordinates']['coordinates'][1] )
        else:
            coordinatesPoint = arcpy.Point(0 , 0)

        place = ''
        if (tweet['place'] != None):
            place = utils.tryStr(tweet['place']['country']) + ' - ' + utils.tryStr(tweet['place']['full_name'])

        row = (
            tweet['user']['geo_enabled'],
            utils.tryStr(tweet['user']['id_str']),
            utils.tryStr(tweet['user']['screen_name']),
            utils.tryStr(tweet['user']['name']),
            utils.tryStr(tweet['id_str']),
            twitterCreatedAt,
            utils.tryStr(tweet['favorite_count']),
            utils.tryStr(tweet['retweet_count']),
            #utils.tryStr(tweet['source']),
            utils.tryStr(tweet['text']),
            place,
            dateutils.datetime.now(),
            coordinatesPoint #coordinates
        )
            
        try:
            #inserting
            msg = str(self.featureCursor.insertRow(row))
            if (msg == 'erro'):
                hashtag['error'] += 1
        except:
            pass

        #erro
        if (hashtag['done'] % 2 == 0):

            #deleting the cursor
            del self.featureCursor

            #creating the feature class cursor
            #self.featureCursor = arcpy.InsertCursor(self.featureClassPath)
            self.featureCursor = arcpy.da.InsertCursor(self.featureClassPath, self.fields)

    #creates the feature class
    def create(self, track):
        
        #local vars
        default_gdb_fullpath = os.getcwd() + r'\twitter.gdb'

        file_gdb_path = os.getcwd() 
        file_gdb_name = track + '.gdb' #+ '_' + dateutils.datetime.now().strftime('%d%m%Y_%H%M') + ".gdb"
        file_gdb_fullpath = file_gdb_path + '\\' + file_gdb_name

        if (os.path.exists(file_gdb_fullpath) == False):

            try:
                shutil.copytree(default_gdb_fullpath, file_gdb_fullpath)
            except OSError as exc: # python >2.5
                if exc.errno == errno.ENOTDIR:
                    #copy
                    shutil.copy(src, dst)
                else: 
                    #removes the tree
                    shutil.rmtree(file_gdb_fullpath)

                    # Execute CreateFileGDB
                    arcpy.CreateFileGDB_management(file_gdb_path, file_gdb_name)
                    
                    # Process: Create Feature Class
                    self.featureClass = arcpy.CreateFeatureclass_management(file_gdb_fullpath, 'tweets', "POINT", default_gdb_fullpath + r'\tweets')

        #setting the feature class
        self.featureClassPath = file_gdb_fullpath + '\\tweets'

        #Creating the feature class cursor
        #self.featureCursor = arcpy.InsertCursor(self.featureClassPath)
        self.featureCursor = arcpy.da.InsertCursor(self.featureClassPath, self.fields)

class Manager():

    #constructor
    def __init__(self):
        #reads config
        self.readConfig()    
        
        #for each hashtag
        for hashtag in hashtags:
            #creates the thread
            try:
               hashtag['thread'] = thread.start_new_thread( self.do, (hashtag, ) )
            except:
               print "Erro: Nao foi possivel iniciar a thread"

        #creates the thread
        while True:
            time.sleep(0.1)
            self.refresh()
        

    #refreshs
    def refresh(self):

        #console information
        clear = lambda: os.system('cls')
        clear()

        # for each hashtag
        for hashtag in hashtags:
            print 'Processo: ' + str(hashtag['thread'])
            print 'Buscando: ' + hashtag['value'] + ' | Ok: ' + str(hashtag['done'])+ ' | Nao OK: ' + str(hashtag['undone'])+ ' | Erro: ' + str(hashtag['error'])
            print ''

    #reads the config file
    def readConfig(self):
        #reading the config file
        dom = minidom.parse('config.xml');

        #for each query element
        for element in dom.getElementsByTagName('track'):

            #appending the hashtags
            hashtags.append({
                'value': str(element.getAttribute('value')),
                'thread': 0,
                'done': 0,
                'undone': 0,
                'error': 0,
                'auth':{
                    'api_key'             : str(element.getAttribute('api-key')),
                    'api_secret'          : str(element.getAttribute('api-secret')),
                    'access_token_key'    : str(element.getAttribute('access-key')),
                    'access_token_secret' : str(element.getAttribute('access-secret')),
                }
            })
    #do
    def do(self, hashtag):

        #tracks
        track = hashtag['value']

        esri = ESRI();
        esri.create(track);

        #reads the config file
        tracking = Twitter(hashtag['auth']).track(str(track))

        #for each line in tracking
        for line in tracking:

            try:

                #parsing the tweet
                tweet = json.loads(line)

                #validates the place or coordinates
                if tweet['place'] == None and tweet['coordinates'] == None:
                    hashtag['undone'] += 1
                else:
                    hashtag['done'] += 1

                    #adds
                    esri.add(tweet, hashtag)
                
            except:
                pass

            
#vars
global hashtags , utils
hashtags = []
utils = Utils()

#initializer
if __name__ == "__main__":

    #manages the threads
    Manager()
