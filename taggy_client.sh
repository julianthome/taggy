#!/bin/bash

# taggy - a nextcloud tag server
#
# The MIT License (MIT)
#
# Copyright (c) 2017 Julian Thome <julian.thome.de@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

USAGE="Usage: $0 <username> <password> <file> <tag>"

source ./taggy_client.cfg

USER="$1"
PW="$2"
FILE="$3"
TAG="$4"

[ -z "$USER" ] || [ -z "$PW" ] || [ -z "$FILE" ] || [ -z "$TAG" ] && {
    echo "malformed arguments"
    echo "$USAGE"
    exit 1
}

[ $# -ne 4 ] && {
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

curl -u "$USER:$PW" -T "$FILE" "http://$HOST:$PORT/$DAV_PATH/$USER/$FILENAME"

PAYLOAD="{\"user\":\"$USER\",\"pw\":\"$PW\",\"file\":\"files/$FILENAME\",\"tags\":[\"$TAG\"]}" 

curl -H "Content-Type: application/json" -X POST -d "$PAYLOAD" "http://$TAGGY_HOST:$TAGGY_PORT/tag"

exit 0
