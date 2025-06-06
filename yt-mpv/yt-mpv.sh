#!/bin/sh

yt-dlp --proxy "192.168.8.101:18080"  --no-check-certificates -o -  -f $2  $1 | mpv -