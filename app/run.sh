#!/bin/bash
cd /app
/usr/local/bin/python -u main.py > /proc/1/fd/1 2>/proc/1/fd/2
