__author__ = 'tanggaolin'

import PyConst
import pymysql
from PIL import Image
import imagehash
import time

src_pic_path = '/opt/lampp/htdocs/wall_offer/wp/'

def printLog(str):
    log = open(PyConst.ERROR_LOG, 'a')
    log.write(time.strftime('%Y-%m-%d %H:%M:%S |') + str + '\n')
    log.close()
    print(str)

def getImageHash(imagename):

    imageF = Image.open(imagename)
    h = str(imagehash.dhash(imageF, 12))
    if h == '000000000000000000000000000000000000':
        h = 'phash_'+str(imagehash.phash(imageF))
    return h

def getImageHashMain():

    conn = pymysql.connect(host='s1.cobo', user='cobo', passwd='cobocobo', db='cobo_wallpaper', port=3306, charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    sql = 'select * from wallpaper where d_hash12 is NULL and state = 0 and upload_user is not null'
    cursor.execute(sql)
    wallpaper = cursor.fetchall()

    for item in wallpaper:
        src_pic_file = src_pic_path + item['dir'] + '/' + item['image_name']
        print src_pic_file
        d_hash12 = getImageHash(src_pic_file)

        try:
            sql = 'update wallpaper set d_hash12 = %s,state = 1 where id = %s'
            cursor.execute(sql, (d_hash12, item['id']))
            conn.commit()
            print 'update wallpaper d_hash12 : ' + d_hash12
        except IOError, e:
            msg = "syncWallLib. %s" % e
            printLog(msg)

    print 'get image_hash done'
    cursor.close()
    conn.close()

def getImageHashByFile(dir, image_name, save_user):

    src_pic_file = src_pic_path + dir + '/' + image_name
    d_hash12 = getImageHash(src_pic_file)

    conn = pymysql.connect(host='s1.cobo', user='cobo', passwd='cobocobo', db='cobo_wallpaper', port=3306, charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    sql = 'update wallpaper set d_hash12 = %s, state = 1, upload_user = %s where dir = %s and image_name = %s'
    cursor.execute(sql, (d_hash12, save_user, dir, image_name))
    print (d_hash12, save_user, dir, image_name)
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":

    getImageHashMain()
