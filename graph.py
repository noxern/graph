#!/usr/bin/env python

import argparse
import sys

import plotly.graph_objs as go
import plotly.plotly as py
import six
from lxml.html import parse

parser = argparse.ArgumentParser()
parser.add_argument('title', help='The title of the TV series')
parser.add_argument('username', help='The username of your Plotly account')
parser.add_argument('password', help='The password of your Plotly account')
args = parser.parse_args()

# find a candidate
search_page = parse('http://www.imdb.com/find?q=%s&s=tt&ttype=tv' % args.title)
candidate = search_page.xpath('//*[@class="findSection"]/table/tr[1]/td[2]/a')
if not candidate: sys.exit('Oh no! No TV series was found with the name: %s' % args.title)

# get ratings
ratings_page = parse('http://www.imdb.com/title/%s/epdate' % candidate[0].get('href').split('/')[2])
rows = ratings_page.xpath('//*[@id="tn15content"]/table//tr[descendant::td]')
if not rows: sys.exit('Oh no! No ratings were found for: %s' % candidate[0].text)

# parse ratings
results = {}

for row in rows:

    # episode doesn't belong in a season (eg. epilogue, special, etc.)
    if '.' not in row[0].text:
        continue

    # episode hasn't aired yet
    if len(row) != 5:
        continue

    season, episode = map(int, row[0].text.split('.'))
    title = row[1][0].text
    link = 'http://www.imdb.com' + row[1][0].get('href')
    rating = float(row[2].text)
    votes = int(row[3].text.replace(',', ''))

    results.setdefault(season, []).append(rating)

# create graph data
data = []
episodes = 0

for season, ratings in six.iteritems(results):
    data.append(go.Scatter(
        name='S' + str(season),
        x=list(range(episodes+1, episodes+len(ratings)+1)),
        y=ratings,
        marker=dict(size=5)
    ))

    episodes += len(ratings)

# set up layout
layout = go.Layout(
    title='<b>IMDb ratings of %s episodes</b>' % candidate[0].text,
    yaxis=dict(title='Rating', range=[0, 10.1], tickmode='linear', tick0=0,
               dtick=2.5, tickformat='.1f', tickprefix=' ' * 10),
    xaxis=dict(title='Episode', range=[0, episodes+1], tickmode='array',
               tickvals=[1, episodes], showgrid=False),
    margin=go.Margin(l=100, pad=10),
    showlegend=False,
    width=1200,
    height=400
)

# sign in to plot.ly and output png
try:
    py.sign_in(args.username, args.password)
    fig = go.Figure(data=data, layout=layout)
    py.image.save_as(fig, filename='graph.png')
except Exception:
    sys.exit('Oh no! Something has gone wrong.')
