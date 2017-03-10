import numpy as np
import pandas as pd

import time

import socketio
import eventlet
from flask import Flask, render_template, send_from_directory

from GetData import get_duration, get_published_hour, get_num_words_in_title, get_published_day_of_week, get_words

sio = socketio.Server()
app = Flask(__name__, static_url_path='')

app.config['DEBUG'] = True # enable hot reload


"""

Data Preposseccing

"""

#collect data
df = pd.read_csv('data/yifu_feb_feb_videos.csv',quotechar='"',escapechar="\\")
#df = df.drop('Unnamed: 0',1)
df = df.dropna(0)

#log transform views
#df['views_original'] = df["views"]
df["views"] = np.log1p(df["views"])

#formatting
df['published_at'] = pd.to_datetime(df['published_at'])
df['category_id'] = df['category_id'].apply(str)

#adding new columns
df['published_hour'] = df['published_at'].dt.hour
df['published_day_of_week'] = df['published_at'].dt.dayofweek

df['#words_in_title'] = df['title'].map(lambda title: len(title.split()))

total_videos = len(df)

def count_caps(title):
    cnt = 0
    for word in title.split():
        if word.isupper():
            cnt+=1
    return cnt

def grab_one_category_data(id):
    if id == '0':
        return df
    return df[df['category_id'] == id]

d_20 = grab_one_category_data('20.0')

d_pre = {
'20':{
    'duration': get_duration(d_20),
    'hour':get_published_hour(d_20),
    'week':get_published_day_of_week(d_20),
    'words_in_title':get_num_words_in_title(d_20),
    'words':get_words(d_20)
},
'22':{
    'duration': get_duration(grab_one_category_data('22.0')),
    'hour':get_published_hour(grab_one_category_data('22.0')),
    'week':get_published_day_of_week(grab_one_category_data('22.0')),
    'words_in_title':get_num_words_in_title(grab_one_category_data('22.0')),
    'words':get_words(grab_one_category_data('22.0'))
},
'24':{
    'duration': get_duration(grab_one_category_data('24.0')),
    'hour':get_published_hour(grab_one_category_data('24.0')),
    'week':get_published_day_of_week(grab_one_category_data('24.0')),
    'words_in_title':get_num_words_in_title(grab_one_category_data('24.0')),
    'words':get_words(grab_one_category_data('24.0'))
}
}
@app.route('/')
def index():
    """Serve the client-side application."""
    return render_template('index.html')

@sio.on('connect')
def connect(sid, environ):
    print('connect ', sid)

@sio.on('request_data')
def request_data(sid, data):
    d = grab_one_category_data(data['data']+'.0')
    sio.emit('percentage_data', {'videos':len(d),'total':total_videos})
    if data['data'] == '20' or data['data'] == '22' or data['data'] == '24':
        sio.emit('duration_data', d_pre[data['data']]['duration'])
        #sio.emit('hour_data', d_pre[data['data']]['hour'])
        sio.emit('week_data', d_pre[data['data']]['week'])
        sio.emit('#words_in_title_data', d_pre[data['data']]['words_in_title'])
        sio.emit('words_data', d_pre[data['data']]['words'])
    else:
        sio.emit('duration_data', get_duration(d))
        #sio.emit('hour_data', get_published_hour(d))
        sio.emit('week_data', get_published_day_of_week(d))
        sio.emit('#words_in_title_data', get_num_words_in_title(d))
        sio.emit('words_data', get_words(d))
@sio.on('search_videos')
def search_videos(sid, data):
    d = grab_one_category_data(data['category']+'.0')
    d_res = d[d['title'].str.contains(data['search_word'],case=False)]
    d_res.sort(['views'])
    sio.emit('return_search_res', {'title':d_res['title'].values.tolist(),'video_id':d_res['video_youtube_id'].values.tolist()})

@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    # wrap Flask application with socketio's middleware
    app = socketio.Middleware(sio, app)

    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 3008)), app)
