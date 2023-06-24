class PropertiesUtil():
    def __init__(self, path):
        self.path = path
        self.properties = {}

    def __getDitc(self, key:str, value:str):
        key = key.strip()
        value = value.strip()

        if key == "day":
            dayList = []
            if value == "all" or value == "":
                dayList = ["周一", "周二", "周三", "周四", "周五"]
            else:
                day = value.split(',')
                dayJson = {"1":"周一", "2":"周二", "3":"周三", "4":"周四", "5":"周五"}
                for x in day:
                    x = x.strip()
                    if x in dayJson.keys():
                        dayList.append(dayJson[x])
            value = dayList

        if key == "time":
            if value == "morning":
                value = "1"
            elif value == "afternoon":
                value = "0"
            else:
                value = "all"

        if key == "lecture":
            if value == "1":
                value = ["3"]
            elif value == "0":
                value = ["2"]
            else:
                value = ["2","3"]

        if key == "week":
            value = [day.strip() for day in value.split(',')]



        self.properties[key] = value                

    def getProperties(self):
        try:
            file = open(self.path,'r',encoding="utf-8")
            lines = file.readlines()
            for line in lines:
                line = line.strip().replace('\n', '').strip()
                if line.find('#') != -1:
                    line = line[0:line.find('#')]
                if line.find('=') > 0:
                    strs = line.split('=')
                    self.__getDitc(strs[0], strs[1]) 
        except Exception as e:
            raise e
        else:
            file.close()
        return self.properties 