__author__ = 'tanggaolin'

#coding=UTF-8

import json
import codecs
import PyConst
import time
import traceback

import pymysql


RESOLUTIONS = ["w1080", "w720", "w540", "w480"]

def printLog(str):

    print str
    log = open(PyConst.CREATE_JSON_LOG, 'a')
    log.write(time.strftime('%Y-%m-%d %H:%M:%S :') + str + '\n')
    log.close()

def getImgBySize(size, img_url):

    if size == "w1080":
        resize = '400x400'
    elif size == "w720":
        resize = '320x320'
    elif size == "w540":
        resize = '240x240'
    elif size == "w480":
        resize = '210x210'

    return img_url.replace('290x290', resize)

def checkPrice(price):
    return round(price) if price > 10 else float(price)

def createItemsBySeries(series_id):

    conn = pymysql.connect(host=PyConst.HOST, user=PyConst.USER, passwd=PyConst.PWD, db=PyConst.DB, port=PyConst.sqlPort, charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    sql = '''
        select a.good_id,title,img,dis_price,ori_price,tmall,postfree,own_url
        from (select good_id from series_good where series_id = '%s') as a
        join (select * from goods where own_url is not null and own_url <> "error_id" and own_url <> 1) as b
        on a.good_id = b.good_id
        order by modify_time ASC
    ''' % series_id

    print sql

    cursor.execute(sql)
    data = cursor.fetchall()

    sql2 = "select title from series where series_id = '%s'" % series_id

    cursor.execute(sql2)
    series_info = cursor.fetchone()

    series_dict = {}

    try:
        for size in RESOLUTIONS:
            dictList = []
            for item in data:
                img = getImgBySize(size, item['img'])
                itemDict = {
                    'id': item['good_id'],
                    'title': item['title'],
                    'item_url': item['own_url'],
                    'img': img,
                    'dis_price': checkPrice(float(item['dis_price'])),
                    'ori_price': checkPrice(float(item['ori_price'])),
                    'tmall': item['tmall'],
                    'postfree': item['postfree']
                }
                dictList.append(itemDict)

            series_dict = {'id': series_id, 'title': series_info['title']}
            jsonDict = {"len": len(dictList), "data": dictList, 'info': series_dict}

            jsonStr = json.dumps(jsonDict, ensure_ascii=False)

            with codecs.open(PyConst.SERIES_JSON_PATH + size + '/' + series_id + ".json", "w", encoding='utf8') as jswrite:
                jswrite.write(jsonStr)

            printLog(series_id + ' ' + size +' is created~')
    except Exception, e:
        exstr = traceback.format_exc()
        print exstr

    return series_dict

def getSeriesList(date):

    conn = pymysql.connect(host=PyConst.HOST, user=PyConst.USER, passwd=PyConst.PWD, db=PyConst.DB, port=PyConst.sqlPort, charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    sql = "select series_no,series_id from series_no where pick_date='%s'" % date
    cursor.execute(sql)
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return data

def createSeriesJsonMain(date):

    series_list = getSeriesList(date)
    print series_list

    id = series_list[0]['series_no']
    data = []
    for item in series_list:
        series_dict = createItemsBySeries(item['series_id'])
        data.append(series_dict)

    jsonDict = {'id': id, 'date': date, 'data': data, 'len': len(data)}
    jsonStr = json.dumps(jsonDict, ensure_ascii=False)
    # print jsonStr
    with codecs.open(PyConst.SERIESLIST_JSON_PATH + 'serieslist_' + str(id) +".json", "w", encoding='utf8') as jswrite:
        jswrite.write(jsonStr)


    return True

if __name__ == "__main__":
    createSeriesJsonMain('20151215')



