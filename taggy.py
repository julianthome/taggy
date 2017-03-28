#!/usr/bin/python3

from bottle import run, post, request, response, get, route

import subprocess
import mysql.connector as mariadb
import sys
import json
from subprocess import call

dbuser = ""
dbpass = ""
dbname = ""
taggy_host = ""
taggy_port = ""


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

    cursor.execute(
        "select fileid from oc_filecache where storage = %s and path = %s", (str(sid), str(ftotag),))

    fid = cursor.fetchone()[0]

    print("sid " + str(sid) + " fid " + str(fid))

    cursor.execute(
        "select * from oc_systemtag_object_mapping where objectid = %s and systemtagid = %s", (str(fid), str(tid),))

    if cursor.rowcount > 0:
        print('systemtag already there')
    else:
        cursor.fetchall()
        print("no systemtag connection")
        try:
            cursor.execute(
                "insert into oc_systemtag_object_mapping(objectid,objecttype,systemtagid) values (%s,'files',%s)", (str(fid), str(tid),))
        except mariadb.Error as error:
            print(str(error))
        finally:
            db.commit()

    cursor.close()
    db.close()


@route('/tag', method='POST')
def recipe_save():
    data = request.json
    print('data')
    print(data)
    storage = "home::" + data['storage']
    fil = data['file']
    tags = data['tags']

    print("storage " + storage + " fil " + fil + " tag " + str(tags))
    for tag in tags:
        dbchange(storage, fil, tag)


def read_config(cfg):
    global dbuser, dbpass, dbname, taggy_host, taggy_port
    print('read file %s' % cfg)
    try:
        cfg = open(cfg, 'r')
    except:
        print('cannot read file %s' % cfg)
        sys.exit(-1)
    scfg = str(cfg.read())
    data = json.loads(scfg)
    dbuser = data["dbuser"]
    dbpass = data["dbpass"]
    dbname = data["dbname"]
    taggy_host = data["taggy_host"]
    taggy_port = data["taggy_port"]


if len(sys.argv) < 2:
    sys.exit('Usage: %s <cfg>' % sys.argv[0])


read_config(sys.argv[1])
print('start with dbuser: %s, dbname: %s, taggy_host: %s, taggy_port: %s' %
      (dbuser, dbname, taggy_host, taggy_port))
run(host=taggy_host, port=taggy_port, debug=False)

sys.exit(0)
