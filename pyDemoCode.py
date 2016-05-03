__author__ = 'tanggaolin'


__author__ = 'Emmett'

import pymysql
import PyConst
import time
import commands
import paramiko

Host = '58.96.186.110'
User = 'cobo'
Pwd = 'cobouser'
db = 'wallpaper_mgr'
sql_port = 3306

sizes = ['1080', '720', '540', '480']

def printLog(msg):
    try:
        with open(PyConst.SYNC_THEME_DATA_LOG, 'a') as logs:
            logs.write(time.strftime('%Y-%m-%d %H:%M:%S :') + msg+'\n')
    except:
        pass
    print(msg)

def uploadFileWith(filePath, yunPath):

    scpcmd = 'scp ' + filePath + ' ' + PyConst.COBO_HK_WP_PATH + yunPath

    print scpcmd
    s, out = commands.getstatusoutput(scpcmd)
    if (s == 0):
        print "scp " + filePath + " done "
    else:
        printLog('foreign:error:'+filePath)
        return False
    return True

def getCatecoverData():

    conn = pymysql.connect(host=Host, user=User, passwd=Pwd, db=db, port=sql_port, charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    sql = 'select cate_cover from wall_cate where state = 0'
    cursor.execute(sql)
    pics = cursor.fetchall()
    cursor.close()
    conn.close()
    return pics

def syncCatecover():

    pic_sizes = ['3x3_w160', '3x3_w240', '3x3_w360',  '3x3_w320', '3x3_w480', '3x3_w720']
    pics = getCatecoverData()

    if len(pics) == 0:
        print 'no pic sync~'
        return
    conn = pymysql.connect(host=Host, user=User, passwd=Pwd, db=db, port=sql_port, charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    for pic in pics:
        for size in pic_sizes:
            pic_path = PyConst.WALL_FOREIGN_CATE_COVER_PATH + size + '/' + pic['cate_cover']
            uploadFileWith(pic_path, "wp_cover/wall_cate_cover/" + pic_path[len(PyConst.WALL_FOREIGN_CATE_COVER_PATH):])

        sql = 'update wall_cate set state = %d where cate_cover = "%s" ' % (1, pic['cate_cover'])
        print sql
        cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

def getAlbumPicsData():

    conn = pymysql.connect(host=Host, user=User, passwd=Pwd, db=db, port=sql_port, charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    sql = 'select album_key,album_banner,album_icon,album_ring from wall_album where state = 0'
    cursor.execute(sql)
    pics = cursor.fetchall()
    cursor.close()
    conn.close()

    return pics

def syncAlbumPics():

    pic_sizes = ['3x3_w1080', '3x3_w720', '3x3_w540', '3x3_w480']
    pics = getAlbumPicsData()

    if len(pics) == 0:
        print 'no pic sync~'
        return

    conn = pymysql.connect(host=Host, user=User, passwd=Pwd, db=db, port=sql_port, charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    for pic in pics:
        for size in pic_sizes:
            album_banner_path = PyConst.WALL_FOREIGN_ALBUM_COVER_PATH + size + '/' + pic['album_banner']
            album_icon_path = PyConst.WALL_FOREIGN_ALBUM_COVER_PATH + size + '/' + pic['album_icon']
            album_ring_path = PyConst.WALL_FOREIGN_ALBUM_COVER_PATH + 'album_ring' + '/' + pic['album_ring']
            uploadFileWith(album_banner_path, "wp_cover/wall_album_pic/" + album_banner_path[len(PyConst.WALL_FOREIGN_ALBUM_COVER_PATH):])
            uploadFileWith(album_icon_path, "wp_cover/wall_album_pic/" + album_icon_path[len(PyConst.WALL_FOREIGN_ALBUM_COVER_PATH):])
            uploadFileWith(album_ring_path, "wp_cover/wall_album_pic/" + album_ring_path[len(PyConst.WALL_FOREIGN_ALBUM_COVER_PATH):])

        sql = 'update wall_album set state = %d where album_key = "%s"' % (1, pic['album_key'])
        print sql
        cursor.execute(sql)

    conn.commit()
    cursor.close()
    conn.close()


def createWpJSONInHK():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('58.96.186.110', 22, 'cobo', 'cobouser', timeout=5)

        cmds = [
                'cd /home/cobo/code/launcher_wp/ && python createWpAlbumJson.py >> create.log',
                'cd /home/cobo/code/launcher_wp/ && python createWpCategoryJson.py >> create.log',
                'cd /home/cobo/code/launcher_wp/ && python createWpJsonList.py >> create.log'
                ]
        for cmd in cmds:
            print cmd
            stdin, stdout, stderr = ssh.exec_command(cmd)
        ssh.close()
    except :
        printLog('create wp json in HK error')

if __name__ == "__main__":
    # syncCatecover()
    # syncAlbumPics()

    createWpJSONInHK()
