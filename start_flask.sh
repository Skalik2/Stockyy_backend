#!/bin/sh

nohup flask run 

echo $! > flask.pid

echo "Flask uruchomiony w tle. Logi: flask.log, PID: $(cat flask.pid)"
