import requests
import time
import os
from bs4 import BeautifulSoup
import threading


url_topic = 'https://epc.ustc.edu.cn/m_practice.asp?second_id=2002'
url_chosen = 'https://epc.ustc.edu.cn/record_book.asp'
url_login = 'https://epc.ustc.edu.cn/n_left.asp'

# httpRequsetAttr = {
# 'submit_type': 'user_login',
# 'name': '',
# 'pass': '',
# 'user_type': '2',
# 'Submit': 'LOG IN'}

# httpRequsetAttr = {
# 'submit_type': 'user_login',
# 'name': '',
# 'pass': '',
# 'user_type': '2',
# 'Submit': 'LOG IN'}

httpRequsetAttr = {
'submit_type': 'user_login',
'name': '',
'pass': '',
'user_type': '2',
'Submit': 'LOG IN'}



bookAttr = {
'submit_type': 'book_submit'
}


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
        print("%s\t%20s\t%s\t%s\t%s"%(data[i][1],data[i][2],data[i][3],data[i][7],data[i][8]))


def filterEpc(lessonDatas):
    # 筛选
    lessons = []
    for i in range(len(lessonDatas)):
        time = lessonDatas[i][6][-11:]

        # if lessonDatas[i][5] == '3': # 讲座
        #     lessons.append(lessonDatas[i])          
        # if time[:2]>"12" and lessonDatas[i][5] != "3": # 上下午
        #     lessons.append(lessonDatas[i])

        if lessonDatas[i][3]=="周二" or lessonDatas[i][3]=="周四" or lessonDatas[i][3]=="周五":
            if time[:2]<"12":
                lessons.append(lessonDatas[i])

    # 如果筛选后没有符合条件的值，则随机选取 
    if lessons == []:
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


if __name__ == '__main__':
    
    while 1:
        print("Waiting...")
        # 登录
        httpSession = login() 
        print(httpRequsetAttr["name"],"successfully login!")

        # 在查看课表的同时，开启线程查询当前选到的课
        print("searching former orders...")
        threadSelections = threading.Thread(target=printSelections, args=(httpSession,))
        threadSelections.start()

        # 查看可选课
        print("searching lessons...")
        lessonDatas = epcInfo(httpSession) 
        print("lessons for selecting:")
        print(lessonDatas)

        # 过滤 
        lessonDatas = filterEpc(lessonDatas)
        print("lessons going to order:")
        print(lessonDatas)
        print(time.ctime())
        print()


        # 如果没课就过1分钟后再来看看
        if lessonDatas == []:
            time.sleep(100)
            httpSession.close()

        # 多线程抢课
        else:
            print("ordering...")
            threads = []
            for data in lessonDatas:
                thread = threading.Thread(target=orderEpc, args=(httpSession, data[0],))
                threads.append(thread)
                thread.start()
            for t in threads:
                t.join()
            httpSession.close()
            time.sleep(1)
        

