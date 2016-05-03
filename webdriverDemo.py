#!/usr/bin/env python
#coding=utf-8
__author__ = 'Emmett'

import time
from selenium import webdriver
import pymysql
import codecs

HOST = 's2.cobo'
USER = 'cobo'
PWD = 'cobocobo'
DB = 'good_store_2'


class GoodsLink:
    def __init__(self):
        self.dr = webdriver.Firefox()

    def printLog(self, path, str):
        print str
        with codecs.open(path, "a", encoding='utf8') as jswrite:
            jswrite.write(str)

    def openAlimama(self):
        self.dr.get("https://www.alimama.com/member/login.htm")

        tryTimes = 0;
        while tryTimes < 100:
            time.sleep(2)
            print self.dr.current_url

            if (self.dr.current_url == 'http://www.alimama.com/index.htm'):
                break

    # https://item.taobao.com/item.htm?id=43826517158

    def convertId(self, id):

        self.dr.get("http://pub.alimama.com/myunion.htm?spm=a219t.7473494.1998155389.3.XfooxO#!/promo/self/links")

        while True:
            try:
                time.sleep(1)
                element = self.dr.find_element_by_id('J_originUrl')
                element.clear()
                element.send_keys("https://item.taobao.com/item.htm?id=" + id)
                break
            except Exception, e:
                print(e)

        genBtn = self.dr.find_element_by_xpath("//vframe[@id='J_vf_promo']/div/div[1]/div[1]/div/button")
        genBtn.click()

        while True:
            try:
                time.sleep(1)
                okBtn = self.dr.find_element_by_xpath("//vframe[@id='vf-dialog']/div/div/button")
                okBtn.click()
                print "ok btn click"
                break
            except Exception, e:
                print(e)

        tryTimes = 0
        outLink = ''
        while tryTimes < 3 :
            try:
                time.sleep(1)
                tryTimes = tryTimes + 1

                outErea = self.dr.find_element_by_xpath("//vframe[@id='magix_vf_code']/div/textarea")
                outLink =  outErea.text
                print outLink
                break
            except Exception, e:
                print(e)

        return outLink

    def getIncomeRatio(self, id):

        self.dr.get("http://pub.alimama.com/myunion.htm?spm=a219t.7473494.1998155389.3.V53efM#!/promo/self/items")

        while True:
            try:
                time.sleep(1)
                element = self.dr.find_element_by_id('q')
                element.clear()
                element.send_keys("https://item.taobao.com/item.htm?id=" + id)
                break
            except Exception, e:
                print(e)

        genBtn = self.dr.find_element_by_xpath("//vframe[@id='magix_vf_main']/div/div/div[@class='self-search']/div[@class='bd clearfix']/a[@class='iconfont search-btn']")
        genBtn.click()

        tryTimes = 0
        income_ratio = ''
        while tryTimes < 3:
            try:
                time.sleep(1)
                tryTimes = tryTimes + 1

                outErea = self.dr.find_element_by_xpath("//div[@id='J_item_list']/table/tbody/tr/td[4]/span")
                income_ratio = outErea.text
                print income_ratio
                break
            except Exception, e:
                print(e)

        return income_ratio

    def quit(self):
        self.dr.close()


    def convGoodsInDb(self):
        conn = pymysql.connect(host=HOST, user=USER, passwd=PWD, db=DB, port=3306, charset='utf8',cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()
        sql = "select good_id,title,good_type from  goods where own_url = 1  limit 50;"
        cursor.execute(sql)
        data = cursor.fetchall()

        try:
            for row in data:
                outLink = self.convertId(row['good_id'])
                income = self.getIncomeRatio(row['good_id'])
                if not outLink.startswith("http:"):
                    updatesql = "delete from  goods  where good_id = '" + row['good_id'] + "'"
                    cursor.execute(updatesql)
                    updatesql = "delete from  album_good  where good_id = '" + row['good_id'] + "'"
                    cursor.execute(updatesql)
                    updatesql = "delete from  youlike_no  where good_id = '" + row['good_id'] + "'"
                    cursor.execute(updatesql)
                    conn.commit()
                    path = '../logs/getGoodLink_' + time.strftime('%Y%m%d') +'.log'
                    msg = 'not out link:' + row['good_id'] + ':' + row['title'] + ':' + row['good_type']
                    self.printLog(path, msg)

                else:
                    updatesql = "update goods set own_url='" + outLink + "',income='" + income + "' where good_id='" + row['good_id'] + "'"
                    print updatesql
                    cursor.execute(updatesql)
                    conn.commit()

            print "update link done"
        except Exception, e:
            print e

        cursor.close()
        conn.close()



if __name__ == "__main__":

    goodsLink = GoodsLink()
    goodsLink.openAlimama()

    times = 0
    while (times < 100):
        goodsLink.convGoodsInDb()
        times += 1



