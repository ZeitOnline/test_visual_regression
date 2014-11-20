#!/bin/bash

# Use this to sync content from friedbert machines to your local storage.
# It syncs content that was modified 21 days ago.
# usage: bash ./content_sync.sh ~/mysyncfolder

# You will need an acocunt on our cms-backend and on friedbert-prod01 to use
# this. 

if [ $# -eq 0 ]; then
    echo usage: $0 [path to sync directory]
    exit
fi

ssh cms-backend.zeit.de cat /tmp/last-modified.res | rsync -avz --files-from - friedbert-prod01.zeit.de:/ $1
