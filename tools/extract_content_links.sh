#!/bin/bash

path=$1
path=${path##http://xml.zeit.de/}
path=${path%%/}

sed -ne '/base-id/s/.*base-id="\([^"]*\)".*/\1/p' $path
sed -ne '/uniqueId/s/.*uniqueId="\([^"]*\)".*/\1/p' $path
sed -ne '/href/s/.*href="\([^"]*\)".*/\1/p' $path
sed -ne '/referenced_cp/s/.*<referenced_cp>\([^<]*\)<\/referenced_cp>/\1/p' $path
