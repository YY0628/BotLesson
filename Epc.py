import requests
import time
import os
from bs4 import BeautifulSoup
import threading
from PropertiesUtil import *


url_topic = 'https://epc.ustc.edu.cn/m_practice.asp?second_id=2002'
url_chosen = 'https://epc.ustc.edu.cn/record_book.asp'
url_login = 'https://epc.ustc.edu.cn/n_left.asp'


httpRequsetAttr = {
'submit_type': 'user_login',
'name': '',
'pass': '',
'user_type': '2',
'Submit': 'LOG IN'}

bookAttr = {
'submit_type': 'book_submit'
}
cancelAttr = {
'submit_type': 'book_cancel'
}

orderInfo = {
"day":"",
"time":"",
"lecture":"",
"compromise":"",
"week":"",
}

data = PropertiesUtil("epc.properties").getProperties()
httpRequsetAttr["name"] = data["username"]
httpRequsetAttr["pass"] = data["password"]
orderInfo["day"] = data["day"]
orderInfo["time"] = data["time"]
orderInfo["lecture"] = data["lecture"]
orderInfo["compromise"] = data["compromise"]
orderInfo["week"] = data["week"]


helloWord = """Welcome to YY's autoEpc!
You can edit your requirements in "epc.properties"
If you hava more ideas or more requirements, you can send me a message
Email: 964422062@qq.com
"""

def login():
    # http会话作用域对象，使多次http请求归属于同一个httpSession，第二次连接带有第一次的cookies
    httpSession = requests.Session()
    # 使用Post方法登录
    httpRespond = httpSession.post(url_login, data=httpRequsetAttr)
    return httpSession


def epcInfo(httpSession):
    # 查看可选信息
    # 登录
    httpRespond = httpSession.get(url_topic)
    data = httpRespond.text

    # 保存网页
    path = os.path.join("./epcInfo","classInfo_"+time.ctime()+'.html')
    path = path.replace(' ', '_')
    path = path.replace(':', '_')
    with open(path, 'w') as f:
        f.write(data) 

    # 读取网页信息
    data = readInfoHtml(path) 

    return data


def readInfoHtml(path):
    soup = BeautifulSoup(open(path, encoding="gb2312"),features="html.parser")
    lessonDatas = []
    datas = soup.findAll("form")
    for lessonForm in datas:

        lessonData = []
        lessonData.append(lessonForm.attrs["action"])
        for td in lessonForm.findAll("td"):
            lessonData.append(td.text.strip())
        lessonDatas.append(lessonData)
    return lessonDatas 


def readSelectionHtml(path):
    soup = BeautifulSoup(open(path, encoding="gb2312"),features="html.parser")
    lessonDatas = []
    datas = soup.findAll("form")[1:]
    for lessonForm in datas:

        lessonData = []
        lessonData.append(lessonForm.attrs["action"])
        for td in lessonForm.findAll("td"):
            lessonData.append(td.text.strip())
        lessonDatas.append(lessonData)
    return lessonDatas 



def searchSelection(httpSession):
    httpRespond = httpSession.get(url_chosen)
    httpSession.close()
    data = httpRespond.text

    # 保存网页
    path = os.path.join("./selections", httpRequsetAttr["name"]+'.html')
    with open(path, 'w') as f:
        f.write(data) 

    return readSelectionHtml(path)
    

def printSelections(httpSession):
    data = searchSelection(httpSession)
    print("former orders: ")
    if len(data)==0:
        print("None!")
    for i in range(len(data)):
        print("%s\t%-30s\t%-10s\t%s\t%s"%(data[i][1],data[i][2],data[i][3],data[i][7],data[i][8]))

def printEpc(data):
    if len(data)==0:
        print("None!")
    for i in range(len(data)):
        print("%-35s\t%s\t%s\t%-10s\t%s"%(data[i][1],data[i][2],data[i][3],data[i][4],data[i][6]))


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


def orderEpc(httpSession, uri):
    # 选课
    url = "https://epc.ustc.edu.cn/"+uri
    httpRespond = httpSession.post(url, data=bookAttr)
    data = httpRespond.text

    # 保存网页
    path = os.path.join("./response","RespondInfo_"+time.ctime()+'.html')
    path = path.replace(' ', '_')
    path = path.replace(':', '_')
    with open(path, 'w') as f:
        f.write(data) 

    return httpRespond


def multiThreadOrder(lessonDatas, httpSession):
    threads = []
    for data in lessonDatas:
        thread = threading.Thread(target=orderEpc, args=(httpSession, data[0],))
        threads.append(thread)
        thread.start()
    for t in threads:
        t.join()


def cancelOrder(httpSession, uri):
    # 退课
    url = "https://epc.ustc.edu.cn/"+uri
    httpRespond = httpSession.post(url, data=cancelAttr)

def orderNew():
    # 选新课
    print(helloWord)
    while 1:
        print("Logining...")
        # 登录
        httpSession = login() 
        print(httpRequsetAttr["name"],"Successfully login!")

        # 在查看课表的同时，开启线程查询当前选到的课
        print("Searching for former orders...")
        threadSelections = threading.Thread(target=printSelections, args=(httpSession,))
        threadSelections.start()

        # 查看可选课
        print("Searching for lessons...")
        lessonDatas = epcInfo(httpSession) 
        print("Lessons for selecting:")
        printEpc(lessonDatas)

        # 过滤 
        lessonDatas = filterEpc(lessonDatas)
        print("Lessons going to order:")
        printEpc(lessonDatas)
        print(time.ctime())


        # 如果没课就过1分钟后再来看看
        if lessonDatas == []:
            print("Searching over, no lessons meeting the requirements!")
            time.sleep(5)
            httpSession.close()

        # 多线程抢课
        else:
            print("Ordering...")
            multiThreadOrder(lessonDatas, httpSession)
            httpSession.close()
            print("Order over!")
            time.sleep(1)
        print()


def changeOneSelection(uri):
    # 替换为更早的课
    while 1:
        print("Logining...")
        # 登录
        httpSession = login() 
        print(httpRequsetAttr["name"],"Successfully login!")

        # 在查看课表的同时，开启线程查询当前选到的课
        print("Searching for former orders...")
        threadSelections = threading.Thread(target=printSelections, args=(httpSession,))
        threadSelections.start()

        # 查看可选课
        print("Searching for lessons...")
        lessonDatas = epcInfo(httpSession) 
        print("Lessons for selecting:")
        printEpc(lessonDatas)

        # 过滤 
        lessonDatas = filterEpc(lessonDatas)
        print("Lessons for ordering:")
        printEpc(lessonDatas)

        # 替换为更早的课
        lessonNew = []
        for lesson in lessonDatas:
            if lesson[2] in orderInfo["week"]:
                lessonNew.append(lesson)
        print("Lessons for changing:")
        printEpc(lessonNew)
    
        if lessonNew != []:
            print("Going to change!")
            threadCancel = threading.Thread(target=cancelOrder, args=(httpSession, uri,))
            threadCancel.start()
            time.sleep(1)
            multiThreadOrder(lessonNew, httpSession)
            print("Over!")
        
        # 如果没课就过1分钟后再来看看
        elif lessonDatas == []:
            print("Searching over, no lessons meeting the requirements!")
            print()

        httpSession.close()


if __name__ == '__main__':
    uri = "record_book.asp?second_id=2002&info_id=2577&week=13&week_day=5&book_sum_id=116022"
    changeOneSelection(uri)    
