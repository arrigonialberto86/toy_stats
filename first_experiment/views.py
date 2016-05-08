from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
import twitter
import json
import pandas as pd
import time
from utils import retweet_statistics
from utils import factor_to_percentage
from utils import factor_to_histogram
from utils import wordcloud
from utils import fetch_jobs_data
from utils import unescape
from utils import latent_sem_analysis
from collections import Counter
import urllib2
from BeautifulSoup import BeautifulSoup
import math


def initialize_api():
	CONSUMER_KEY = 'fel1nI1kGC2NM8DWeq4T4XfI7'
	CONSUMER_SECRET = 'tXcI11QvAbTpEWczoaztWf6p07rSn6Es41TC9VK77JIhhzmA9B'
	OAUTH_TOKEN = '402812165-CgKuIrvRuqNFqbqjmPUDQgW0CkKXzC1PH0tKK0Xo'
	OAUTH_TOKEN_SECRET = '1ZeKp1ciDxIRVyN8GHtWYhzdzGyS2Hn4arrAUb7zu0A0v'
	auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
	 							CONSUMER_KEY, CONSUMER_SECRET)
	twitter_api = twitter.Twitter(auth=auth)
	return twitter_api

def index(request):
    return HttpResponse("Hello, world. Application home page")

def trial(request):
    template = loader.get_template('first_experiment/trial.html')
    context = { 'some_variable': 'I am some variable' }
    return HttpResponse(template.render(context, request))

def jobs(request):
    template = loader.get_template('first_experiment/jobs.html')
    context = { 'some_variable': 'I am some variable' }
    return HttpResponse(template.render(context,request))

def trends(request):
	twitter_api = initialize_api()
	if request.POST['country'] == 'Italy':
		ITALY_ID = 23424853
		trends = twitter_api.trends.place(_id=ITALY_ID)
		response = map(lambda t: t['query'].replace("%23","#").replace('%22',''),trends[0]['trends'])
		json_response = json.dumps([ [pos] for pos in response])
		return HttpResponse(json_response)
	elif request.POST['country'] == 'World':
		WORLD_ID = 1
		trends = twitter_api.trends.place(_id=WORLD_ID)
		response = map(lambda t: t['query'].replace("%23","#").replace('%22',''),trends[0]['trends'])
		json_response = json.dumps([ [pos] for pos in response])
		return HttpResponse(json_response)
	elif request.POST['country'] == 'USA':
		USA_ID = 23424977
		trends = twitter_api.trends.place(_id=USA_ID)
		response = map(lambda t: t['query'].replace("%23","#").replace('%22',''),trends[0]['trends'])
		json_response = json.dumps([ [pos] for pos in response])
		return HttpResponse(json_response)
	elif request.POST['country'] == 'Germany':
		GERMANY_ID = 23424829
		trends = twitter_api.trends.place(_id=GERMANY_ID)
		response = map(lambda t: t['query'].replace("%23","#").replace('%22',''),trends[0]['trends'])
		json_response = json.dumps([ [pos] for pos in response])
		return HttpResponse(json_response)
	elif request.POST['country'] == 'Milan':
		MILAN_ID = 718345
		trends = twitter_api.trends.place(_id=MILAN_ID)
		response = map(lambda t: t['query'].replace("%23","#").replace('%22',''),trends[0]['trends'])
		json_response = json.dumps([ [pos] for pos in response])
		return HttpResponse(json_response)
	else:
		return HttpResponse("Sorry, that country is not available")

def query(request):
	twitter_api = initialize_api()
	q = request.POST['query']
	count = 10000000
	search_results = twitter_api.search.tweets(q=q, count=count)
	statuses_data = search_results['statuses']

	# Create the dataframe we will use
	tweets = pd.DataFrame()
	tweets['created_at'] = map(lambda tweet: time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')), statuses_data)
	tweets['user'] = map(lambda tweet: tweet['user']['screen_name'], statuses_data)
	tweets['user_followers_count'] = map(lambda tweet: tweet['user']['followers_count'], statuses_data)
	tweets['text'] = map(lambda tweet: tweet['text'].encode('utf-8'), statuses_data)
	tweets['lang'] = map(lambda tweet: tweet['lang'], statuses_data)
	tweets['Location'] = map(lambda tweet: tweet['place']['country'] if tweet['place'] != None else None, statuses_data)
	tweets['retweet_count'] = map(lambda tweet: tweet['retweet_count'], statuses_data)
	tweets['favorite_count'] = map(lambda tweet: tweet['favorite_count'], statuses_data)
	#tweets.to_pickle('/Users/arrigoni/Documents/twitter_experiment/first_experiment/supporting_data/panda_pd.pickle')
	pd.set_option('max_colwidth',-1)
	df_html = tweets[['user','text','created_at','lang']].to_html( index_names=False, classes='table query_table_pd table-hover')
	retweet_stats = retweet_statistics(tweets)
	languages = factor_to_percentage(tweets,'lang')
	users = factor_to_percentage(tweets,'user')
	location = factor_to_percentage(tweets,'Location')
	#wordcloud(tweets)
	return HttpResponse(json.dumps({'dataframe':df_html,'retweet_stats':retweet_stats, 
		'languages':json.dumps(languages), 'users': json.dumps(users), 'location':json.dumps(location)}))

def query_alt(request):
	import os
	base_path = os.path.dirname(os.path.abspath(__file__))
	tweets = pd.read_pickle(base_path+'/supporting_data/panda_pd.pickle')
	pd.set_option('max_colwidth',-1)
	df_html = tweets[['user','text','created_at','lang']].to_html( index_names=False, classes='table query_table_pd table-hover')
	retweet_stats = retweet_statistics(tweets)
	languages = factor_to_percentage(tweets,'lang')
	users = factor_to_percentage(tweets,'user')
	location = factor_to_percentage(tweets,'Location')
	return HttpResponse(json.dumps({'dataframe':df_html,'retweet_stats':retweet_stats, 
		'languages':json.dumps(languages), 'users': json.dumps(users), 'location':json.dumps(location)}))


def jobs_search(request):
	jobs_name = request.POST['jobs_name']
	jobs_location = request.POST['jobs_location']
	results,companies,locations,jobs_dict = fetch_jobs_data(jobs_name,jobs_location)
	lsa_results = latent_sem_analysis(results,companies)

	import pandas as pd
	pd.set_option('max_colwidth',-1)
	return HttpResponse(json.dumps({'results':results,'companies':companies, 
		'locations':locations, 'lsa_results':lsa_results, 
		'jobs_dict': jobs_dict.drop(['Latitude', 'Longitude'], axis=1).to_html(classes='table jobs_table_pd table-hover', 
			index=False, escape=False)}))


def jobs_wordcloud(request):
	job_url = request.POST['job_url']
	request = urllib2.Request(job_url)
	html = urllib2.urlopen(request).read()
	parsed_html = BeautifulSoup(html)
	text = parsed_html.find("span", {"id": "job_summary"}).text

	no_urls = [word.replace(".","").replace(",","").replace(":","") for word in text.split() 
	                               if 'http' not in word]
	stops = [
	    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',  'your',
	    'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she',
	    'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
	    'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that',
	    'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
	    'have', 'has', 'had',  'having', 'do', 'does', 'did', 'doing', 'a', 'an',
	    'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of',
	    'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
	    'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
	    'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
	    'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any',
	    'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
	    'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can',
	    'will', 'just', 'don', 'should', 'now', 'id', 'var', 'function', 'js', 'd',
	    'script', '\'script', 'fjs', 'document','job','work',1,2,3,4,5,6,7,8,9,10,
	    '_','-',',','.','/','\\','skills','strong','must','experience','like','candidate',
	    'candidates','people','across','and/or','you','New York','San Francisco', 'Los Angeles',
	    'Boston','San Diego','company'
	]

	words = [x for x in no_urls if x not in stops]
	counts = Counter(words)
	counts_sorted = sorted(counts.items(), key=lambda pair: pair[1], reverse=True)
	#c = [ {'text':k[0],'weight':k[1]} for k in counts_sorted]
	#c = [[k[0],math.pow(k[1],3)] for k in counts_sorted][1:50]
	c = [ [k[0],round(k[1]/float(max(dict(counts_sorted).values()))*100,1)] for k in counts_sorted][1:50]
	return HttpResponse(json.dumps(c))




