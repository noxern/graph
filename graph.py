#!/usr/bin/env python3.6

import os

import falcon
import hug
import hug.types
import plotly.graph_objs as go
import plotly.plotly as py
import requests
from lxml import html

IMDB_URL = 'http://www.imdb.com'

py.sign_in(os.environ['PLOTLY_USERNAME'], os.environ['PLOTLY_API_KEY'])

api = hug.API(__name__)


@hug.output_format.on_valid('image/png')
def format_as_png_when_valid(data, request=None, response=None):
    return data

@hug.get()
def slack(text: hug.types.text):
    show = text
    return {
        'response_type': 'in_channel',
        'text': f'Graph for {show}',
        'attachments': [{
          'image_url': f'https://tvgraph.herokuapp.com/graph?title={show}'
        }]
    }



@hug.get(output=format_as_png_when_valid, examples='title=Breaking%20Bad')
def graph(title: hug.types.text):
    """Returns an IMDb ratings graph of the given TV series"""

    # find a candidate (with English as accept language to avoid geolocalized title names)
    search_res = requests.get(IMDB_URL + f'/find?q={title}&s=tt&ttype=tv', headers={'Accept-Language': 'en'})
    search_page = html.fromstring(search_res.text)
    candidate = search_page.xpath('//*[@class="findSection"]/table/tr[1]/td[2]/a')
    if not candidate: raise Exception(f'Oh no! No TV series was found with the name: {title}')

    tt_id = candidate[0].get("href").split("/")[2]
    title = candidate[0].text

    # get ratings
    ratings_res = requests.get(IMDB_URL + f'/title/{tt_id}/epdate')
    ratings_page = html.fromstring(ratings_res.text)
    rows = ratings_page.xpath('//*[@id="tn15content"]/table//tr[descendant::td]')
    if not rows: raise Exception(f'Oh no! No ratings were found for: {title}')

    # parse ratings
    results = {}

    for row in rows:

        if '.' not in row[0].text: continue  # episode doesn't belong in a season (eg. special)
        if len(row) != 5: continue           # episode hasn't aired yet

        season, episode = map(int, row[0].text.split('.'))
        ep_title = row[1][0].text
        ep_link = IMDB_URL + row[1][0].get('href')
        ep_rating = float(row[2].text)
        ep_votes = int(row[3].text.replace(',', ''))

        results.setdefault(season, []).append(ep_rating)

    # create graph data
    data = []
    episodes = 0

    for season, ratings in results.items():
        data.append(go.Scatter(
            name='S' + str(season),
            x=list(range(episodes + 1, episodes + len(ratings) + 1)),
            y=ratings,
            marker=dict(size=5)
        ))

        episodes += len(ratings)

    # set up layout
    layout = go.Layout(
        title=f'<b>IMDb ratings of {title} episodes</b>',
        yaxis=dict(title='Rating', range=[0, 10.1], tickmode='linear', tick0=0,
                   dtick=2.5, tickformat='.1f', tickprefix=' ' * 10),
        xaxis=dict(title='Episode', range=[0, episodes + 1], tickmode='array',
                   tickvals=[1, episodes], showgrid=False),
        margin=go.Margin(l=100, pad=10),
        showlegend=False,
        width=1200,
        height=400
    )

    fig = go.Figure(data=data, layout=layout)
    output = py.image.get(fig)

    return output


@hug.exception(Exception)
def handle_exception(exception):
    raise falcon.HTTPInternalServerError('error', str(exception))
