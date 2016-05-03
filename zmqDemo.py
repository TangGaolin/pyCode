#!/usr/bin/env python

__author__ = 'Emmett'

import time
import zmq

import setproctitle

import cutPics
import createYouLikeJson
import createAlbumJson
import autoDiffSynctoUpyun
import createCategoryJson
import createSeriesJson

from multiprocessing import Pool
import json
import PyConst


MSG_TYPE_CUT_PICS = "cut_pics"
MSG_TYPE_CREATE_JSON = "create_json"
MSG_TYPE_CREATE_YOULIKE = "create_youlike_json"
MSG_TYPE_CREATE_ALBUM = "create_album_json"
MSG_TYPE_CREATE_SERIES = "create_series_json"
MSG_TYPE_CREATE_CATEGORY = "create_category_json"
MSG_TYPE_CUT_SERIES_PICS = "cut_series_pics"

MSG_TYPE_SYNC_DATA = "sync_data"


def printLog(str):
    log = open(PyConst.GOODS_DAEMON_LOG, 'a')
    log.write(time.strftime('%Y-%m-%d %H:%M:%S :') + str + '\n')
    log.close()
    print(str)

def runCutPics(picName):
    cutPics.resize(picName)

def runCutSeriesPics(picName):
    cutPics.resizeSeriesCover(picName)

def runCreateAlbumJSON(date):
    createAlbumJson.createAlbumJsonMain(date)


def runCreateSeriesJSON(date):
    createSeriesJson.createSeriesJsonMain(date)

def runCreateYouLikeJSON(date):
    createYouLikeJson.createYouLikeJson(date)

def runCreateCategoryJSON(some):
    createCategoryJson.createJsonByCate()

def runSyncDdata(some):
    autoDiffSynctoUpyun.sync()



def getReturnMsg(staus, msg=None):
    rv = {"err": staus, "msg":msg}
    return json.dumps(rv)

def runLoop():

    setproctitle.setproctitle("goodstore_daemon")

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5556")

    pool = Pool(processes=2)

    while True:
        #  Wait for next request from client
        message = socket.recv()

        printLog(message)
        try:
            messagedict = json.loads(message)
            type = messagedict['type']
            body = messagedict['body']

            if type == MSG_TYPE_CUT_PICS:
                result = pool.apply_async(runCutPics, [body])
            if type == MSG_TYPE_CUT_SERIES_PICS:
                result = pool.apply_async(runCutSeriesPics, [body])
            if type == MSG_TYPE_CREATE_YOULIKE:
                result = pool.apply_async(runCreateYouLikeJSON, [body])
            if type == MSG_TYPE_CREATE_ALBUM:
                result = pool.apply_async(runCreateAlbumJSON, [body])
            if type == MSG_TYPE_CREATE_SERIES:
                result = pool.apply_async(runCreateSeriesJSON, [body])
            if type == MSG_TYPE_CREATE_CATEGORY:
                result = pool.apply_async(runCreateCategoryJSON, [body])

            if type == MSG_TYPE_SYNC_DATA:
                result = pool.apply_async(runSyncDdata, [body])

            #  Send reply back to client
            socket.send(getReturnMsg(0))
        except:
            socket.send(getReturnMsg(-1, "message format error"))

if __name__ == "__main__":
    runLoop()

