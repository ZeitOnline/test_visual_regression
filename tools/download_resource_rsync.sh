#!/bin/bash

host=friedbert.staging.zeit.de

path=$1
path=${path##http://xml.zeit.de/}
path=${path%%/}
targetdir=$(dirname $path)

mkdir -p $targetdir
rsync -av $host:/var/cms/work/$path $targetdir
rsync -av $host:/var/cms/work/$path.meta $targetdir
