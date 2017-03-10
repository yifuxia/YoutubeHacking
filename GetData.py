import numpy as np
import pandas as pd
import scipy
from sklearn.feature_extraction.text import CountVectorizer

def get_duration(df,data_portion=0.95):
    duration_mean_views = df.groupby(['duration'],as_index=False).mean()[['duration','views']]
    duration = duration_mean_views['duration']
    views = duration_mean_views['views']
    rft = np.fft.rfft(views)
    rft[8:] = 0   # Note, rft.shape = 21
    y_smooth = np.fft.irfft(rft)

    cnt = df.groupby(['duration'],as_index=False).count()['views'].values

    #reformat data
    res = []
    for i in xrange(len(duration.values[:int(data_portion*duration.shape[0])].tolist())):
    	d = {'duration':duration.values[:int(data_portion*duration.shape[0])].tolist()[i], 'views':y_smooth[:(data_portion*duration.shape[0])].tolist()[i],'counts':cnt[:int(data_portion*duration.shape[0])].tolist()[i]}
    	res.append(d)
    return res

def get_published_hour(df):
    hour_mean_views = df.groupby(['published_hour'],as_index=False).mean()[['published_hour','views']]
    res=[]
    for i in xrange(len(hour_mean_views['published_hour'].values.tolist())):
        d = {'published_hour': hour_mean_views['published_hour'].values.tolist()[i], 'views':hour_mean_views['views'].values.tolist()[i]}
        res.append(d)
    return res

def get_published_day_of_week(df):
    day_of_week_mean_views = df.groupby(['published_day_of_week'],as_index=False).mean()[['published_day_of_week','views']]
    cnt = df.groupby(['published_day_of_week'],as_index=False).count()['views'].values
    res=[]
    for i in xrange(len(day_of_week_mean_views['published_day_of_week'].values.tolist())):
		d = {'published_day_of_week': day_of_week_mean_views['published_day_of_week'].values.tolist()[i], 'views':day_of_week_mean_views['views'].values.tolist()[i],'counts':cnt.tolist()[i]}
		res.append(d)
    return res
def get_num_words_in_title(df):
    title_words_mean_views = df.groupby(['#words_in_title'],as_index=False).mean()[['#words_in_title','views']]
    cnt = df.groupby(['#words_in_title'],as_index=False).count()['views'].values
    res=[]
    for i in xrange(len(title_words_mean_views['#words_in_title'].values.tolist())):
		d = {'#words_in_title': title_words_mean_views['#words_in_title'].values.tolist()[i], 'views':title_words_mean_views['views'].values.tolist()[i],'counts':cnt.tolist()[i]}
		res.append(d)
    return res

"""def get_num_links(df):
    bins = np.linspace(df['#links'].min(), df['#links'].max(), 100)
    groups = df[['#links','views']].groupby(pd.cut(df['#links'], bins),as_index=False)
    tmp_res = groups.mean()[np.isfinite(groups.mean()['#links'])]
    res=[]
    for i in xrange(len(tmp_res['#links'].values.tolist())):
        d = {'num_links': tmp_res['#links'].values.tolist()[i], 'views':tmp_res['views'].values.tolist()[i]}
        res.append(d) 
    return res"""

def get_words(df,num=20):
    vectorizer = CountVectorizer(analyzer = "word",   \
                                 tokenizer = None,    \
                                 preprocessor = None, \
                                 stop_words = 'english',   \
                                 max_features = 1000) 

    title_vec = vectorizer.fit_transform(df['title'].tolist()).toarray()

    weighted_features = []
    for i in xrange(len(title_vec)):
        weighted_features.append(title_vec[i]*df['views'].tolist()[i])
        print 'in process...'+str(i)
    word_rating_dict = np.sum(weighted_features,axis=0)*1.0 / np.sum(title_vec,axis=0)
    vocab = vectorizer.get_feature_names()
    wordRating =[]
    dist = np.sum(title_vec, axis=0)
    for i in xrange(len(vocab)):
        wordRating.append((vocab[i],round(word_rating_dict[i],3),dist[i]))
    wordRating_sorted_by_count = wordRating[:]
    wordRating_sorted_by_count.sort(key = lambda (a,b,c):-c)
    wordRating_sorted_by_score = wordRating[:]
    wordRating_sorted_by_score.sort(key = lambda (a,b,c):-b)
    print 'done!_______________'
    res_count = []
    res_score = []
    for i in xrange(num):
    	d_count = {'word': wordRating_sorted_by_count[i][0],'count' :wordRating_sorted_by_count[i][2]}
    	d_score = {'word': wordRating_sorted_by_score[i][0],'score' :wordRating_sorted_by_score[i][1], 'count' : wordRating_sorted_by_score[i][2]}
    	res_count.append(d_count)
    	res_score.append(d_score)
    return {'freq_words': res_count, 'view_friendly_words': res_score}

