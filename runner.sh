#!/bin/sh

pbpaste > results.txt
source .venv/bin/activate
cat results.txt | python3 -m main | more
