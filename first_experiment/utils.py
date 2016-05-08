def retweet_statistics(tweets):
    '''
    tweets is a Panda dataframe having 'text column'
    '''
    list_of_original_tweets = [element for element in tweets['text'].values if not element.startswith('RT')]
    list_of_retweets = [element for element in tweets['text'].values if element.startswith('RT')]
    return len(list_of_original_tweets), len(list_of_retweets)

def factor_to_histogram(df,col_name):
    '''
    Input is a column of a pandas df
    '''
    dc = df[col_name].value_counts().to_dict()
    [{'Name':user[0],'y':user[1]} for user in sorted(dc.items(), key=lambda x: x[1], reverse=True)]  

def factor_to_percentage(df,col_name):
    '''
    Input is a column of a pandas df (for highcharts graph libraries)
    '''
    dc = df[col_name].value_counts().to_dict()
    sum_values = sum(dc.values())
    return [ { 'name':k, 'y': round(float(dc[k])/sum_values*100,2)} for k in dc.keys()]

def wordcloud(tweets):
    from wordcloud import WordCloud, STOPWORDS#, ImageColorGenerator
    import os

    text = " ".join(tweets['text'].values.astype(str))
    no_urls_no_tags = " ".join([word for word in text.split()
                                    if 'http' not in word
                                        and not word.startswith('@')
                                        and word != 'RT'
                                    ])

    wc = WordCloud(background_color="white", font_path="/Library/Fonts/Verdana.ttf", stopwords=STOPWORDS, width=1000,
                          height=1000)
    wc.generate(no_urls_no_tags)
    #plt.imshow(wc)
    #plt.axis("off")
    base_path = os.path.dirname(os.path.abspath(__file__))
    wc.to_file(base_path+'/static/first_experiment/wc.png')
    print 'file saved successfully'

def fetch_jobs_data(job_name,location):
    import xmltodict 
    import json
    import urllib2
    from BeautifulSoup import BeautifulSoup

    job_name,location = job_name.replace(' ','%20'),location.replace(' ','%20')
    url = ("http://api.indeed.com/ads/apisearch?publisher=2302422541489410&"
        "q={0}&l={1}&sort=&radius=&st=&jt=&start=0&limit=25&fromage=&filter=&"
        "latlong=1&co=us&chnl=&userip=1.2.3.4&useragent=Mozilla/%2F4.0%28Firefox%29&v=2".format(job_name,location))
    request = urllib2.Request(url)
    u = urllib2.urlopen(request)
    r = xmltodict.parse(u.read())
    jobs_dict = return_jobs_dict(r)

    results = []
    companies = []
    locations = []
    for idx,job in enumerate(r['response']['results']['result']):
        request = urllib2.Request(job['url'])
        html = urllib2.urlopen(request).read()
        parsed_html = BeautifulSoup(html)
        summary = parsed_html.find("span", {"id": "job_summary"}).text
        if summary != '':
            results.append(summary)
            companies.append(parsed_html.find("span", {"class": "company"}).text)
            locations.append(parsed_html.find("span", {"class": "location"}).text)

    return results,companies,locations,jobs_dict

def unescape(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&amp;", "&")
    return s

def return_jobs_dict(xml_sr):
    '''
    Return pandas df from indeed search results
    xml_sr is an xml search results object
    '''
    import pandas as pd

    pd.set_option('display.expand_frame_repr', True)
    dataset = xml_sr['response']['results']['result']
    jobs = pd.DataFrame()
    jobs['Job title'] = map(lambda job: job['jobtitle'], dataset)
    jobs['Company'] = map(lambda job: job['company'], dataset)
    jobs['Location'] = map(lambda job: job['formattedLocation'], dataset)
    jobs['Country'] = map(lambda job: job['country'], dataset)
    jobs['Posting date'] = map(lambda job: job['formattedRelativeTime'], dataset)
    jobs['URL'] = map(lambda job: '<a href=\"{0}\">Open</a>'.format(job['url']), dataset)
    jobs['Wordcloud'] = map(lambda job: '<button data-url=\"{0}\" data-toggle="modal" data-target=".bs-example-modal-lg" class=\"btn btn-default wordcloud_btn \">Click</button>'.format(job['url']), dataset)
    jobs['Latitude'] = map(lambda job: job['latitude'], dataset)
    jobs['Longitude'] = map(lambda job: job['longitude'], dataset)
    return jobs

def latent_sem_analysis(results,companies):
    import sklearn
    from sklearn.decomposition import TruncatedSVD
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import Normalizer
    import pandas as pd
    import warnings
    # Suppress warnings from pandas library
    warnings.filterwarnings("ignore", category=DeprecationWarning,
    module="pandas", lineno=570)

    vectorizer = TfidfVectorizer(min_df=2,stop_words = 'english')
    dtm = vectorizer.fit_transform(results)

    #print("n_samples: %d, n_features: %d" % dtm.shape)

    # Fit LSA
    lsa = TruncatedSVD(2, algorithm = 'arpack')
    dtm_lsa = lsa.fit_transform(dtm)
    dtm_lsa = Normalizer(copy=False).fit_transform(dtm_lsa)
    pd.DataFrame(lsa.components_,index = ["component_1","component_2"],columns = vectorizer.get_feature_names())

    xs = [w[0] for w in dtm_lsa]
    ys = [w[1] for w in dtm_lsa]

    scatter_plot_data = [{'Name':companies[idx],'x':x,'y':ys[idx]} for idx,x in enumerate(xs)]
    return scatter_plot_data
















