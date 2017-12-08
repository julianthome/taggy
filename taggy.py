#!/usr/bin/env python3

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

from bottle import run, post, request, response, get, route

import subprocess
import mysql.connector as mariadb
import sys
import json
from subprocess import call
import requests

dbuser = ""
dbpass = ""
dbname = ""
taggy_host = ""
taggy_port = ""
dav_auth_path = ""

def dbchange(storage, ftotag, tag):

    db = mariadb.connect(user=dbuser, password=dbpass, database=dbname, host=dbhost, port=dbport)
    cursor = db.cursor()

    cursor.execute("SELECT name,id FROM oc_systemtag")

    tagdict = {}
    tagset = set()

    for name, id in cursor:
        tagdict[str(name, 'utf-8')] = str(id)
        tagset.add(str(name, 'utf-8'))
        print("name:" + str(name, 'utf-8') + ", id:" + str(id))
        print(tagdict)

    tid = -1
    if tag in tagset:
        tid = tagdict[tag]
        print("tag " + tag + " is already in set " + tid)
    else:
        cursor.execute("insert into oc_systemtag(name) values (%s)", (tag,))
        db.commit()
        cursor.execute("select id from oc_systemtag where name = %s", (tag,))
        tid = cursor.fetchone()[0]

    print("storage " + storage)
    cursor.execute(
        "select numeric_id from oc_storages where id = %s", (storage,))

    sid = cursor.fetchone()[0]

    print("sid " + str(sid))

    cursor.execute("select fileid from oc_filecache where storage = %s \
                   and path = %s", (str(sid), str(ftotag),))

    fid = cursor.fetchone()[0]

    print("sid " + str(sid) + " fid " + str(fid))

    cursor.execute("select * from oc_systemtag_object_mapping where objectid \
                   = %s and systemtagid = %s", (str(fid), str(tid),))

    if cursor.rowcount > 0:
        print('systemtag already there')
    else:
        cursor.fetchall()
        print("no systemtag connection")
        try:
            cursor.execute("insert into oc_systemtag_object_mapping(objectid,\
                           objecttype,systemtagid) values (%s,'files',%s)",
                           (str(fid), str(tid),))
        except mariadb.Error as error:
            print(str(error))
        finally:
            db.commit()

    cursor.close()
    db.close()


def authenticate(user, password):
    r = requests.get(dav_auth_path,
                     auth=(user, password))
    if r.status_code == 200:
        return True
    return False


@route('/tag', method='POST')
def tag():
    data = request.json
    print('data')
    print(data)
    storage = "home::" + data['user']
    fil = data['file']
    tags = data['tags']
    user = data['user']
    pw = data['pw']
    if authenticate(user, pw):
        print("storage " + storage + " fil " + fil + " tag " + str(tags))
        for tag in tags:
            dbchange(storage, fil, tag)
    else:
        print("authentication error")


def read_config(cfg):
    global dbuser, dbpass, dbname, dbhost, dbport, taggy_host, taggy_port, dav_auth_path
    print('read file %s' % cfg)
    try:
        cfg = open(cfg, 'r')
    except:
        print('cannot read file %s' % cfg)
        sys.exit(-1)
    scfg = str(cfg.read())
    config = json.loads(scfg)
    dbuser = config["dbuser"]
    dbpass = config["dbpass"]
    dbname = config["dbname"]
    dbhost = config["dbhost"]
    dbport = config["dbport"]
    taggy_host = config["taggy_host"]
    taggy_port = config["taggy_port"]
    dav_auth_path = config["dav_auth_path"]


if len(sys.argv) < 2:
    sys.exit('Usage: %s <cfg>' % sys.argv[0])

read_config(sys.argv[1])
print('start with dbuser: %s, dbname: %s, dbhost: %s, dbport: %s, taggy_host: %s, taggy_port: %s' %
      (dbuser, dbname, dbhost, dbport, taggy_host, taggy_port))

run(host=taggy_host, port=taggy_port, debug=False)

