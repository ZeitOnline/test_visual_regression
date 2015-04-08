#!/bin/bash

# To download a resource from the CMS vivi, call this script with an path as
# argument. This path should _not_ begin with a '/' and ist a subpath of
# /cms/work.
# To download resource and meta resource of the homepage call:
# ./vivi_download.sh index

dav_host='http://cms-backend.zeit.de:9000';
target='../src/zeit/web/core/data/'$1

if [[ $1 == */ ]]; then
	target=${target%?}
fi

mkdir -p $target
rm -R $target

curl ${dav_host}/cms/work/$1 > $target 2> /dev/null

outcurl=$(curl -X PROPFIND --header "depth:1" ${dav_host}/cms/work/$1 2> /dev/null |xsltproc meta_dav2xml.xslt -)

echo $outcurl |  xmllint --format - > $target.meta

if [[ $1 == */ ]]; then
	rm -R $target
fi
