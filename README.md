# graph
A Python tool for generating IMDb rating graphs of TV series using [OMDb API](http://www.omdbapi.com), [IMDb](http://www.imdb.com) and [Plotly](https://plot.ly).

### Usage
```
usage: graph.py [-h] -title TITLE -username USERNAME -password PASSWORD

optional arguments:
  -h, --help          show this help message and exit
  -title TITLE        The title of the TV series
  -username USERNAME  The username of your Plotly account
  -password PASSWORD  The password of your Plotly account
```

### Example input
```
$ python graph.py -title 'Breaking Bad' -username johndoe -password Tr0ub4dor&3
```

### Example output
![Graph](graph.png)
