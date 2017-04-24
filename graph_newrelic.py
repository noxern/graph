#!/usr/bin/env python

import newrelic.agent

import graph

app = newrelic.agent.WSGIApplicationWrapper(graph.__hug_wsgi__)
