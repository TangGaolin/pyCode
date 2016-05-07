__author__ = 'tanggaolin'

import urllib
import urllib2
import json
import requests
import pymysql
import time
import sys

platform = 'aibizhi'

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



def requestJson(url):

    i_headers = {"User-Agent": "Mozilla%2F5.0%20(Linux%3B%20U%3B%20Android%204.1.1%3B%20zh-cn%3B%20MI%202%20Build%2FJRO03L)%20AppleWebKit%2F534.30%20(KHTML%2C%20like%20Gecko)%20Version%2F4.0%20Mobile%20Safari%2F534.30"}
    req = urllib2.Request(url, headers=i_headers)
    result = urllib2.urlopen(req, timeout=40).read()
    return json.loads(result)



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


def crawAiBizhiMain(cate_url, cate_name):

    while 1:
        res = requestJson(cate_url)
        for item in res['data']:
            wall_id = str(item['file_id'])
            image_name = cate_name+'_'+wall_id
            image_url = item['image']['vip_original']

            if checkExitedDB(wall_id):
                saveDB(wall_id, image_name, image_url)
                print image_name + ' ' + wall_id + ' is  got ~'

        if res['link']['next'] == '':
            print cate_name + 'done ..'
            break
        cate_url = res['link']['next']

    pass


types = ['hot', 'new']

if __name__ == "__main__":

    tid = '3950'
    image_name = 'timeber'
    c_url = "http://api.lovebizhi.com/android_v3.php?a=category&spdy=1&device=Meizu%28M351%29&uuid=e37b31ada1fddfa52b8b1186f6ee2eae&mode=2&client_id=1001&device_id=62225131&model_id=100&size_id=0&channel_id=1&screen_width=1080&screen_height=1920&bizhi_width=1080&bizhi_height=1920&version_code=79&language=zh-CN&mac=&original=0&tid="+tid
    for type in types:
        craw_url = c_url + "&order=" + type
        crawAiBizhiMain(craw_url, image_name)
    pass