import requests
import time
import os
from bs4 import BeautifulSoup
import threading
from PropertiesUtil import *
from Epc import *

cancelAttr = {
'submit_type': 'book_cancel'
}

httpRequsetAttr = {
'submit_type': 'user_login',
'name': 'SA21168173',
'pass': 'EQSSRQ',
'user_type': '2',
'Submit': 'LOG IN'}

orderInfo = {
"day":"",
"time":"",
"lecture":"",
"compromise":"",
"week":"",
}

data = PropertiesUtil("epc.properties").getProperties()
httpRequsetAttr["name"] = data["username"]
httpRequsetAttr["password"] = data["password"]
orderInfo["day"] = data["day"]
orderInfo["time"] = data["time"]
orderInfo["lecture"] = data["lecture"]
orderInfo["compromise"] = data["compromise"]
orderInfo["week"] = data["week"]




def cancelOrder(httpSession):
    url = "https://epc.ustc.edu.cn/record_book.asp?second_id=2002&info_id=1502&week=13&week_day=1&book_sum_id=115945"
    httpRespond = httpSession.post(url, data=cancelAttr)

def filterEpc(lessonDatas):
    # 筛选
    lessons = []
    for i in range(len(lessonDatas)):
        time = lessonDatas[i][6][-11:-9]
        day = lessonDatas[i][3]
        lecture = lessonDatas[i][5]

        if day in orderInfo["day"]:
            if lecture in orderInfo["lecture"]:
                if orderInfo["time"] == "all":
                    lessons.append(lessonDatas[i])
                elif orderInfo["time"] == "1":
                    if time < "12":
                        lessons.append(lessonDatas[i])
                elif orderInfo["time"] == "0":
                    if time > "12":
                        lessons.append(lessonDatas[i])

    # 如果筛选后没有符合条件的值，则随机选取 
    if lessons == [] and orderInfo["compromise"]=="1":
        lessons = lessonDatas
    return lessons


if __name__ == '__main__':


    data = readInfoHtml("./epcInfo/classInfo_Fri_Nov_19_01_30_32_2021.html")

    lessons = filterEpc(data)

    printEpc(lessons)
