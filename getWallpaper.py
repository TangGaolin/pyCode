__author__ = 'tanggaolin'

import pymysql
import urllib2
import time
import os

wall_path = '/mnt/nas/wallpapers/craw_wallpaper/wallpapers/'
log = 'logs/error.log'

Host = 'vs2.s4.cobo'
User = 'cobo'
Password = 'cobocobo'
Db = 'craw_wallpaper'


def printLog(msg):
    try:
        with open(log, 'a') as logs:
            logs.write(time.strftime('%Y-%m-%d %H:%M:%S :') + msg+'\n')
    except:
        pass
    print(msg)


def getWallpaperUrl():

    conn = pymysql.connect(host=Host, user=User, passwd=Password, db=Db, port=3306, charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    sql = 'select * from wallpapers where state = 0'
    cursor.execute(sql)
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res


def downWallpaper(url, image_path):

    print url
    try:
        req = urllib2.Request(url)
        data = urllib2.urlopen(req, timeout=20).read()
        f = open(image_path, 'wb')
        f.write(data)
        f.close()
        print 'get '+image_path+' is successful!'
        return True
    except Exception, e:
        printLog('get '+image_path+' is error')
        print e
        return False

def getWallpaperMain():

    conn = pymysql.connect(host=Host, user=User, passwd=Password, db=Db, port=3306, charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    urls = getWallpaperUrl()

    for item in urls:
        image_name = item['image_name']
        platform = item['platform']
        dir_path = wall_path + platform
        if os.path.isdir(dir_path) is False:
            os.mkdir(dir_path)
        else:
            pass

        res = downWallpaper(item['image_url'], dir_path + '/' + image_name+'.jpg')

        if res is True:
            sql = 'update wallpapers set state = 1 where id = %d' % item['id']
            cursor.execute(sql)
            conn.commit()
        else:
            sql = 'update wallpapers set state = -1 where id = %d' % item['id']
            cursor.execute(sql)
            conn.commit()

    cursor.close()
    conn.close()




if __name__ == "__main__":
    getWallpaperMain()
