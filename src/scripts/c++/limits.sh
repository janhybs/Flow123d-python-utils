#!/bin/bash
# file: limits.sh

TT=1200
./main -m 100 -t $TT &
echo "PID = $!"

./main -m 100 -t $TT &
echo "PID = $!"

./main -m 100 -t $TT &
echo "PID = $!"

echo 'sleeping'
sleep $TT

exit 0