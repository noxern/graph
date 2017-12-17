#!/usr/bin/env python3.6

import logging
import random
import os
import uuid
from urllib.parse import quote

import falcon
import hug
import hug.types
import plotly.graph_objs as go
import plotly.plotly as py
import requests
from cachetools import func
from lxml import html

IMDB_URL = 'http://www.imdb.com'
GRAPH_URL = f'https://{os.environ.get("HEROKU_APP_NAME")}.herokuapp.com'

py.sign_in(os.environ['PLOTLY_USERNAME'], os.environ['PLOTLY_API_KEY'])

api = hug.API(__name__)


@func.ttl_cache(maxsize=32, ttl=3600)
def create_graph(title):
    results = dict()

    # find a candidate (with English as accept language to avoid geolocalized title names)
    search_res = requests.get(IMDB_URL + f'/find?q={title}&s=tt&ttype=tv', headers={'Accept-Language': 'en'})
    search_page = html.fromstring(search_res.text)
    candidate = search_page.xpath('//*[@class="findSection"]/table/tr[1]/td[2]/a')
    if not candidate: raise Exception(f'Oh no! No TV series was found with the name: {title}')

    tt_id = candidate[0].get("href").split("/")[2]
    title = candidate[0].text

    # get seasons
    seasons_res = requests.get(IMDB_URL + f'/title/{tt_id}/episodes/_ajax')
    seasons_page = html.fromstring(seasons_res.text)
    seasons = seasons_page.xpath('//*[@id="bySeason"]/option/@value')
    if not seasons: raise Exception(f'Oh no! No seasons were found for: {title}')

    for season in seasons:

        # get ratings
        ratings_res = requests.get(IMDB_URL + f'/title/{tt_id}/episodes/_ajax?season={season}')
        ratings_page = html.fromstring(ratings_res.text)
        rows = ratings_page.xpath('//*[@class="info"]')
        if not rows: raise Exception(f'Oh no! No ratings were found for: {title}')

        # parse ratings
        for row in rows:

            episode = int(row.find('.//*[@itemprop="episodeNumber"]').get('content'))
            if episode < 1: continue  # episode doesn't belong in a season (eg. special)

            ep_title = row.find('.//*[@itemprop="name"]').get('title')
            ep_link = IMDB_URL + row.find('.//*[@itemprop="name"]').get('href').split('?ref')[0]

            if row.find('.//*[@class="ipl-rating-star--placeholder"]') is not None: continue  # episode hasn't aired yet
            ep_rating = float(row.find('.//*[@class="ipl-rating-star__rating"]').text)
            ep_votes = int(row.find('.//*[@class="ipl-rating-star__total-votes"]').text[1:][:-1].replace(',', ''))

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


@hug.output_format.on_valid('image/png')
def format_as_png_when_valid(data, request=None, response=None):
    return data


@hug.get(output=format_as_png_when_valid, examples='title=Breaking%20Bad')
def graph(title: hug.types.text):
    """Returns an IMDb ratings graph of the given TV series"""
    return create_graph(title)


@hug.get(output_invalid=hug.output_format.text, examples='text=Breaking%20Bad',
         on_invalid=lambda x: 'Have you tried turning it off and on again? :troll:')
def slack(text: hug.types.text):
    """Returns JSON containing an attachment with an image url for the Slack integration"""
    title = text

    if text == 'top250':
        top250_res = requests.get(IMDB_URL + '/chart/toptv', headers={'Accept-Language': 'en'})
        top250_page = html.fromstring(top250_res.text)
        candidates = top250_page.xpath('//*[@data-caller-name="chart-top250tv"]//tr/td[2]/a')

        title = random.choice(candidates).text

    return dict(
        response_type='in_channel',
        attachments=[
            dict(image_url=GRAPH_URL + f'/graph?title={quote(title)}&uuid={uuid.uuid4()}')
        ]
    )


@hug.exception(Exception)
def handle_exception(exception):
    logging.exception('An exception with the following traceback occurred:')
    raise falcon.HTTPInternalServerError('error', str(exception))
