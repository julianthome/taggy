#!/bin/bash

USAGE="Usage: $0 <username> <password> <file> <tag>"

source ./taggy_client.cfg

USER="$1"
PW="$2"
FILE="$3"
TAG="$4"


[ "$#"-ne 4 ] && {
    echo "Wrong number of arguments"
    echo "$USAGE"
    exit 1
}

[ ! -f "$FILE" ] && {
    echo "file \"$FILE\" does not exist"
    exit 1
}

[ -z "$TAG" ] && {
    echo "tag definition \"$TAG\" is empty"
    exit 1
}

[[ ! $TAG =~ ^[0-9a-zA-Z]{1,40}$ ]] && {
    echo "malformed tag"
    exit 1
}

FILENAME="$(basename $FILE)"

curl -u "$USER:$PW" -T "$FILE" "http://$HOST:4080/$DAV_PATH/$USER/$FILENAME"

PAYLOAD="{\"user\":\"$USER\",\"pw\":\"$PW\",\"file\":\"$DAV_PATH/files/$FILENAME\",\"tags\":[\"$TAG\"]}" 

curl -H "Content-Type: application/json" -X POST -d "$PAYLOAD" "http://$TAGGY_HOST:$TAGGY_PORT/tag"

exit 0
