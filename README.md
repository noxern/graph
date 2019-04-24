# graph
A Python 3.7 API for generating rating graphs of TV series using [IMDb](https://www.imdb.com) and [Plotly](https://plot.ly).

With bonus integrations for [Heroku](https://devcenter.heroku.com/articles/getting-started-with-python#introduction), [New Relic](https://devcenter.heroku.com/articles/newrelic) and [Slack](https://api.slack.com/slash-commands).

### Config

Create an `.env` file with the following variables:
- `PLOTLY_USERNAME`
- `PLOTLY_API_KEY`

### Setup

0. Run `pipenv install` to set up a virtual environment and install the dependencies.

### Running
0. Run `pipenv run gunicorn graph:__hug_wsgi__ --reload` to start a server in reload mode.

### Endpoints

The documentation for the API is returned as JSON on every 404 request:
 
`$ curl http://localhost:8000 | jq`

```json
{
  "handlers": {
    "/graph": {
      "GET": {
        "usage": "Returns an IMDb ratings graph of the given TV series",
        "examples": [
          "/graph?title=Breaking%20Bad"
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
        "usage": "Returns JSON containing an attachment with an image url for the Slack integration",
        "examples": [
          "/slack?text=Breaking%20Bad"
        ],
        "outputs": {
          "format": "JSON (Javascript Serialized Object Notation)",
          "content_type": "application/json; charset=utf-8"
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
