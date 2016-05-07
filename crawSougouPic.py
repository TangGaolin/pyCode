__author__ = 'tanggaolin'

import urllib
import urllib2
import json
import requests
import pymysql
import time
import sys

platform = 'sougou'

Host = 'vs2.s4.cobo'
User = 'cobo'
Password = 'cobocobo'
Db = 'craw_wallpaper'

dev_msg = "&w=1080&h=1920&v=2.5.5.71399&dv=4.4.4&dn=N958St&dr=1080x1920&r=0021-0021&j=c89bb694171d706458b7b0a455647dde&i=936aa52af2cd74db347dbf6735863d8d&n=WIFI"

def printLog(msg):
    try:
        log = 'logs/'+time.strftime('%Y-%m-%d ')+'.log'
        with open(log, 'a') as logs:
            logs.write(time.strftime('%H:%M:%S ||') + msg+'\n')
    except:
        pass
    print(msg)



def getPicUrl(pic_id):

    url = "http://download.android.bizhi.sogou.com/download_1.1.php?id=" + pic_id + dev_msg
    try:
        r = requests.get(url)
        return r.url
    except:
        printLog('getPicUrl error:' + pic_id)
        return False

def getKeyWords():
    conn = pymysql.connect(host=Host, user=User, passwd=Password, db=Db, port=3306, charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    sql = 'select * from key_words where state = 0'
    cursor.execute(sql)
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

def updateKeyWordsState(id):

    conn = pymysql.connect(host=Host, user=User, passwd=Password, db=Db, port=3306, charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    sql = 'update key_words set state = 1 where id = %d' % int(id)
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()



def requestJson(word):

    url = "http://so.bizhi.sogou.com/androidquery?word=" + word + dev_msg
    url = url.encode('gbk')
    print url
    i_headers = {"User-Agent": "Mozilla%2F5.0%20(Linux%3B%20U%3B%20Android%204.1.1%3B%20zh-cn%3B%20MI%202%20Build%2FJRO03L)%20AppleWebKit%2F534.30%20(KHTML%2C%20like%20Gecko)%20Version%2F4.0%20Mobile%20Safari%2F534.30"}
    req = urllib2.Request(url,headers=i_headers)
    result = urllib2.urlopen(req,timeout=40).read()
    return json.loads(result)

def crawSougouPicMain():

    key_words = getKeyWords()

    if len(key_words) == 0:
        printLog('no key words')

    for key_word in key_words:
        print 'get ' + key_word['en_word'] + ' start~'

        print ''
        data_json = requestJson(key_word['zh_word'])
        print data_json

        for item in data_json['wallpaper']:
            if checkExitedDB(item['aa']):
                image_url = getPicUrl(item['aa'])
                print image_url
                if image_url is not False:
                    image_name = key_word['en_word'].replace(' ', '_') +'_'+item['aa']
                    saveDB(item['aa'], image_name, image_url)

        updateKeyWordsState(key_word['id'])
        print ''
        print 'get ' + key_word['en_word'] + ' done~'


def saveDB(wall_id, image_name, image_url):
    conn = pymysql.connect(host=Host, user=User, passwd=Password, db=Db, port=3306, charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    add_time = time.strftime("%Y-%m-%d %H:%M:%S")
    sql = 'insert into wallpapers set platform = %s, wall_id = %s, image_name = %s, image_url = %s, add_time = %s'
    cursor.execute(sql, (platform, wall_id, image_name, image_url, add_time))
    conn.commit()
    cursor.close()
    conn.close()
    print 'get ' + image_name + ' done ~'



def requestJsonByCate(cate_id,p):

    # print urllib.quote(word.decode(sys.stdin.encoding).encode('utf8'))
    dev_msg2 = '&t=1455728401&w=1080&h=1800&v=2.5.5.71399&dv=4.4.4&dn=M351&dr=1080x1800&r=0032-0032&j=fea6091587fd084df5f1f907e3b5a334&i=d41d8cd98f00b204e9800998ecf8427e&n=WIFI'
    url = "http://download.android.bizhi.sogou.com/list_1.2.php?cate_id=" + cate_id + "&p=" + str(p) + dev_msg2
    url = url.encode('gbk')
    print url
    try:
        i_headers = {"User-Agent": "Mozilla%2F5.0%20(Linux%3B%20U%3B%20Android%204.1.1%3B%20zh-cn%3B%20MI%202%20Build%2FJRO03L)%20AppleWebKit%2F534.30%20(KHTML%2C%20like%20Gecko)%20Version%2F4.0%20Mobile%20Safari%2F534.30"}
        req = urllib2.Request(url,headers=i_headers)
        result = urllib2.urlopen(req,timeout=20).read()
        return json.loads(result)
    except:
        return False


def checkExitedDB(wall_id):

    conn = pymysql.connect(host=Host, user=User, passwd=Password, db=Db, port=3306, charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    sql = 'select * from  wallpapers where platform = %s and wall_id = %s'
    cursor.execute(sql, (platform, wall_id))
    res = cursor.fetchall()
    cursor.close()
    conn.close()

    if len(res) == 0:
        return True
    else:
        print 'The wall_id  ' + wall_id + ' is exited~'
        return False


def crawSougouPicByCate(cate_name, cate_id):

    for p in range(1, 100):
        # print p
        data_json = requestJsonByCate(cate_id, p)
        print data_json

        if data_json is not False:
            if len(data_json['wallpaper']) == 0:
                break
            for item in data_json['wallpaper']:
                if checkExitedDB(item['aa']):
                    image_url = getPicUrl(item['aa'])
                    print image_url
                    if image_url is not False:
                        image_name = cate_name.replace(' ', '_') +'_'+item['aa']
                        saveDB(item['aa'], image_name, image_url)

    pass

if __name__ == "__main__":

    # crawSougouPicMain()

    # crawSougouPicByCate('cate_art', '226')
    # crawSougouPicByCate('cate_draw', '227')

    # crawSougouPicByCate('cate_simple', '233')
    # crawSougouPicByCate('cate_dreamscape', '235')
    # crawSougouPicByCate('cate_cool', '234')
    # crawSougouPicByCate('cate_tile', '238')

    # crawSougouPicByCate('cate_fresh', '228')
    # crawSougouPicByCate('cate_healing', '229')
    # crawSougouPicByCate('cate_fetish', '231')
    # crawSougouPicByCate('cate_sad', '230')
    # crawSougouPicByCate('cate_love', '232')

    # crawSougouPicByCate('cate_sexygirl', '206')
    # crawSougouPicByCate('cate_freshgirl', '207')
    # crawSougouPicByCate('cate_star', '108')
    # crawSougouPicByCate('cate_prettyboys', '210')
    # crawSougouPicByCate('cate_typeman', '209')
    #
    # crawSougouPicByCate('cate_cat', '211')
    # crawSougouPicByCate('cate_dog', '212')
    # crawSougouPicByCate('cate_cute', '213')
    # crawSougouPicByCate('cate_fish', '214')
    # crawSougouPicByCate('cate_wild', '215')

    crawSougouPicByCate('cate_cars', '221')
    crawSougouPicByCate('cate_food', '223')
    crawSougouPicByCate('cate_brand', '225')


    pass