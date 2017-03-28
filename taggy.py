#!/usr/bin/env python3

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

    db = mariadb.connect(user=dbuser, password=dbpass, database=dbname)
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
    global dbuser, dbpass, dbname, taggy_host, taggy_port, dav_auth_path
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
    taggy_host = config["taggy_host"]
    taggy_port = config["taggy_port"]
    dav_auth_path = config["dav_auth_path"]


if len(sys.argv) < 2:
    sys.exit('Usage: %s <cfg>' % sys.argv[0])

read_config(sys.argv[1])
print('start with dbuser: %s, dbname: %s, taggy_host: %s, taggy_port: %s' %
      (dbuser, dbname, taggy_host, taggy_port))

run(host=taggy_host, port=taggy_port, debug=False)

