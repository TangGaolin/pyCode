__author__ = 'Emmett'


import commands
import os
import sys
import PyConst
import math


sizes = [1080, 720, 540, 480]


def moveRes(pic):

    srcPic = os.path.join(PyConst.GOOD_COVER_DIR, pic)
    picName = pic.replace(".png", ".jpg")
    picName = picName.replace(".jpeg", ".jpg")
    print(picName)

    os.chdir(PyConst.S_PIC_DIR + "/w1080")
    cutCommond = "convert -resize 1080x1920! -quality 80 " + srcPic + " " + picName
    status, output = commands.getstatusoutput(cutCommond)

    return picName

def doResize(pic, raw_path, to_path):

    for size in sizes:
        dir = os.path.join(to_path, "w" + str(size))
        if os.path.isdir(dir) == False:
            os.mkdir(dir)
        os.chdir(dir)
        cutCommond = "convert -resize " + str(size) + " -quality 80 " + raw_path + pic + " " + pic

        print cutCommond
        status, output = commands.getstatusoutput(cutCommond)


def doResizeForThumbnail(pic, size, quality):

    dir = os.path.join(PyConst.S_PIC_DIR, "s" + size)
    if os.path.isdir(dir) == False:
        os.mkdir(dir)
    os.chdir(dir)
    cutCommond = "convert -resize " + str(math.ceil(int(size) / 3)) + " -quality "+quality+" " + PyConst.S_PIC_DIR + "/w1080/" + pic + " " + pic
    print cutCommond
    status, output = commands.getstatusoutput(cutCommond)


def resize(pic):

    doResize(pic, PyConst.GOOD_COVER_DIR, PyConst.S_PIC_DIR)

    doResizeForThumbnail(pic, "1080", '30')
    doResizeForThumbnail(pic, "720", '30')


def resizeSeriesCover(pic):

    doResize(pic, PyConst.SERIES_COVER_DIR, PyConst.S_SERIES_PIC_DIR)

    pass

if __name__ == "__main__":

    if len(sys.argv) == 2:
        resize(sys.argv[1])
    resizeSeriesCover('201512101449739449.jpg')
    pass





