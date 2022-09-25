import logging
import random
import threading
import uuid
from urllib.parse import quote

import falcon
import hug
import hug.types
import plotly.graph_objects as go
import requests
import requests_html
from cachetools import func

IMDB_URL = 'https://www.imdb.com'

session = requests_html.HTMLSession()

api = hug.API(__name__)


@func.ttl_cache(maxsize=32, ttl=3600)
def create_graph(title):
    results = dict()

    # find a candidate (with English as accept language to avoid geolocalized title names)
    search_res = session.get(IMDB_URL + f'/find?q={title}&s=tt&ttype=tv', headers={'Accept-Language': 'en'})
    candidate = search_res.html.find('.findResult .result_text a', first=True)
    if not candidate: raise Exception(f'Oh no! No TV series was found with the name: {title}')

    tt_id = candidate.search('/title/{}/')[0]
    title = candidate.text

    # get seasons
    seasons_res = session.get(IMDB_URL + f'/title/{tt_id}/episodes/_ajax')
    seasons = [s.attrs['value'] for s in seasons_res.html.find('#bySeason option')]
    if not seasons: raise Exception(f'Oh no! No seasons were found for: {title}')

    for season in seasons:

        # get ratings
        ratings_res = session.get(IMDB_URL + f'/title/{tt_id}/episodes/_ajax?season={season}')
        rows = ratings_res.html.find('.info')
        if not rows: raise Exception(f'Oh no! No ratings were found for: {title}')

        # parse ratings
        for row in rows:

            ep_number = int(row.find('[itemprop="episodeNumber"]', first=True).attrs['content'])
            if ep_number < 1: continue  # episode doesn't belong in a season (eg. special)

            if not row.find('.ipl-rating-widget'): continue  # episode hasn't aired yet
            if row.find('.ipl-rating-star--placeholder'): continue  # episode hasn't been rated yet
            ep_rating = float(row.find('.ipl-rating-star__rating', first=True).text)

            results.setdefault(season, []).append(ep_rating)

    # create graph data
    data = []
    episodes = 0

    for season, ratings in results.items():
        data.append(go.Scatter(
            name='S' + str(season),
            x=list(range(episodes + 1, episodes + len(ratings) + 1)),
            y=ratings,
            mode='lines+markers',
            marker=dict(size=5)
        ))

        episodes += len(ratings)

    # set up layout
    layout = go.Layout(
        title=f'<b>IMDb ratings of {title} episodes</b>',
        title_x=0.5,
        yaxis=dict(title='Rating', range=[0, 10.1], tickmode='linear', tick0=0,
                   dtick=2.5, tickformat='.1f', ticksuffix='   ', ticks='',
                   showgrid=True),
        xaxis=dict(title='Episode', range=[0, episodes + 1], tickmode='array',
                   tickvals=[1, episodes], tickcolor='white', showgrid=False),
        template='simple_white',
        margin=go.layout.Margin(l=100),
        showlegend=False,
        width=1200,
        height=400
    )

    fig = go.Figure(data=data, layout=layout)
    output = fig.to_image(format='png')

    return output


@hug.output_format.on_valid('image/png')
def format_as_png_when_valid(data):
    return data


@hug.get(output=format_as_png_when_valid, examples='title=Breaking%20Bad')
def graph(title: hug.types.text):
    """Returns an IMDb ratings graph of the given TV series"""
    return create_graph(title)


@hug.get(output_invalid=hug.output_format.text, examples='text=Breaking%20Bad&response_url=callback',
         on_invalid=lambda x: 'Have you tried turning it off and on again? :troll:')
def slack(text: hug.types.text, response_url: hug.types.text, request=None):
    """Sends a delayed response to callback url for Slack integration"""
    title = text

    if text == 'top250':
        top250_res = session.get(IMDB_URL + '/chart/toptv', headers={'Accept-Language': 'en'})
        candidates = top250_res.html.find('.chart .titleColumn a')

        title = random.choice(candidates).text

    t = threading.Thread(target=slack_post, args=(response_url, request.prefix, title))
    t.start()

    return dict(
        response_type='in_channel',
        text='I will get right on that! :construction_worker:'
    )


@hug.not_found(output=hug.output_format.json)
def not_found(documentation: hug.directives.documentation):
    return documentation


@hug.exception(Exception)
def handle_exception(exception):
    logging.exception('An exception with the following traceback occurred:')
    raise falcon.HTTPInternalServerError('error', str(exception))


def slack_post(response_url, prefix, title):
    create_graph(title)

    requests.post(response_url, json=dict(
        response_type='in_channel',
        replace_original=True,
        attachments=[
            dict(image_url=prefix + f'/graph?title={quote(title)}&uuid={uuid.uuid4()}')
        ]
    ))
