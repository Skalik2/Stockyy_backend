#!/bin/sh

nohup flask run > flask.log 2>&1 &

echo $! > flask.pid 

echo "Flask uruchomiony w tle. Logi: flask.log, PID: $(cat flask.pid)"
