#!/bin/bash

# To download a resource from the CMS vivi, call this script with an path as
# argument. This path should _not_ begin with a '/' and ist a subpath of /cms/work/.
# To download resource and meta resource of the homepage call:
# ./download_resource.sh index

dav_host='http://cms-backend.zeit.de:9000';

if [[ $1 == /* ]]; then
	echo "ERROR: path should _not_ begin with a '/' ’cause it‘s a subpath of /cms/work/"
	exit 128
fi

curl ${dav_host}/cms/work/$1 > resource 2> /dev/null

outcurl=$(curl -X PROPFIND --header "depth:1" ${dav_host}/cms/work/$1 2> /dev/null |xsltproc meta_dav2xml.xslt -)

echo $outcurl |  xmllint --format - > resource.meta
