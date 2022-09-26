# graph
A Python 3 API for generating rating graphs of TV series using [IMDb](https://www.imdb.com) and [Plotly](https://plotly.com/python/).

With bonus integrations for [Fly.io](https://fly.io/docs/languages-and-frameworks/python/) and [Slack](https://api.slack.com/interactivity/slash-commands).

### Config

Set the following environment variables:
- `PLOTLY_USERNAME`
- `PLOTLY_API_KEY`

### Setup

0. Run `poetry install` to set up a virtual environment and install the dependencies.

### Running
0. Run `poetry run gunicorn graph:__hug_wsgi__ --reload` to start a server in reload mode.

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
        "usage": "Sends a delayed response to callback url for Slack integration",
        "examples": [
          "/slack?text=Breaking%20Bad&response_url=callback"
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
