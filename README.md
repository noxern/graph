# graph
A Python 3.6 API for generating IMDb rating graphs of TV series using [IMDb](http://www.imdb.com) and [Plotly](https://plot.ly).

Bonus: [Heroku integration](https://devcenter.heroku.com/articles/getting-started-with-python#introduction)

Bonus: [Slack integration](https://api.slack.com/custom-integrations/outgoing-webhooks)

### Config

Environmental variables:
- `PLOTLY_USERNAME`
- `PLOTLY_API_KEY`
- (Optional) [`HEROKU_APP_NAME`](https://devcenter.heroku.com/articles/dyno-metadata#usage)

### Setup

0. (Optional) Run `virtualenv -p python3.6 venv` to set up a Python 3.6 virtual environment.
0. (Optional) Run `source venv/bin/activate` to activate it.
0. Run `pip install -r requirements.txt` to install the dependencies.

### Running
0. Run `gunicorn graph:__hug_wsgi__ --reload` to start a server in reload mode.
0. Navigate to http://localhost:8000 to access the API.

### Endpoints

The documentation for the API are returned as JSON on every 404 request. For example on localhost:

```json
{
    "404": "The API call you tried to make was not defined. Here's a definition of the API to help you get going :)",
    "documentation": {
        "handlers": {
            "/graph": {
                "GET": {
                    "usage": "Returns an IMDb ratings graph of the given TV series",
                    "examples": [
                        "http://localhost:8000/graph?title=Breaking%20Bad"
                    ],
                    "outputs": {
                        "format": null,
                        "content_type": "image/png"
                    },
                    "inputs": {
                        "title": {
                            "type": "Basic text / string value"
                        }
                    }
                }
            },
            "/slack": {
                "GET": {
                    "examples": [
                        "http://localhost:8000/slack?text=Breaking%20Bad"
                    ],
                    "outputs": {
                        "format": "JSON (Javascript Serialized Object Notation)",
                        "content_type": "application/json"
                    },
                    "inputs": {
                        "text": {
                            "type": "Basic text / string value"
                        }
                    }
                }
            }
        }
    }
}
```

### Example

#### Request
```text
GET /graph?title=Breaking%20Bad
```

#### Response
```text
HTTP/1.1 200 OK
Content-Type: image/png
```

![Graph](graph.png)
