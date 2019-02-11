
import re
import time
import xml.etree.cElementTree as ET
from uiautomator import device as d


class Element(object):
    """
    通过元素定位,需要Android 4.0以上
    """

    def __init__(self):
        """
        初始化，获取系统临时文件存储目录，定义匹配数字模式
        """
    #     self.tempFile = tempfile.gettempdir()
        self.pattern = re.compile(r"\d+")

    def __uidump(self):
        """
        获取当前Activity控件树
        """
        d.dump("hierarchy.xml")
        print(d.dump())

    def __element(self, attrib, name):
        """
        同属性单个元素，返回单个坐标元组
        """

        self.__uidump()
        tree = ET.ElementTree(file="hierarchy.xml")
        print(tree)
        treeIter = tree.iter(tag="node")
        for elem in treeIter:
            aaa = elem.attrib[attrib]
            if len(aaa) != 0:
                print(aaa)
            if elem.attrib[attrib] == name:
                bounds = elem.attrib["bounds"]
                coord = self.pattern.findall(bounds)
                Xpoint = (int(coord[2]) - int(coord[0])) / 2.0 + int(coord[0])
                Ypoint = (int(coord[3]) - int(coord[1])) / 2.0 + int(coord[1])
                return Xpoint, Ypoint

    def __elements(self, attrib, name):
        """
        同属性多个元素，返回坐标元组列表
        """
        list = []
        self.__uidump()

        tree = ET.ElementTree(file="hierarchy.xml")
        treeIter = tree.iter(tag="node")
        for elem in treeIter:
            if elem.attrib[attrib] == name:
                bounds = elem.attrib["bounds"]
                coord = self.pattern.findall(bounds)
                Xpoint = (int(coord[2]) - int(coord[0])) / 2.0 + int(coord[0])
                Ypoint = (int(coord[3]) - int(coord[1])) / 2.0 + int(coord[1])
                list.append((Xpoint, Ypoint))
        return list

    def findElementByContentDesc(self, name):
        return self.__element("content-desc", name)

    def findElementByName(self, name):
        """
        通过元素名称定位
        usage: findElementByName(u"设置")
        """
        return self.__element("text", name)

    def findElementsByName(self, name):
        return self.__elements("text", name)

    def findElementByClass(self, className):
        """
        通过元素类名定位
        usage: findElementByClass("android.widget.TextView")
        """
        return self.__element("class", className)

    def findElementsByClass(self, className):
        return self.__elements("class", className)

    def findElementById(self, id):
        """
        通过元素的resource-id定位
        usage: findElementsById("com.android.deskclock:id/imageview")
        """
        return self.__element("resource-id", id)

    def findElementsById(self, id):
        return self.__elements("resource-id", id)


def forwardPYQ():
    d.press.home()

    element = Element()

    e1 = element.findElementByName("微信")
    if e1 is None:
        print("微信坐标：未找到!")
        return
    print("微信坐标：{}".format(e1))
    d.click(e1[0], e1[1])
    # time.sleep(10)

    e2 = element.findElementByName("发现")
    if e2 is None:
        print("发现坐标：未找到!")
        return
    print("发现坐标：{}".format(e2))
    d.click(e2[0], e2[1])
    # time.sleep(10)

    e3 = element.findElementByName("朋友圈")
    if e3 is None:
        print("发现坐标：未找到!")
        return
    print("朋友圈坐标：{}".format(e3))
    d.click(e3[0], e3[1])

def findTP():
    element = Element()
    ls = element.findElementsById("com.tencent.mm:id/mi")
    print(ls)
    # for i in list:
    d.click(ls[3][0], ls[3][1])
    pl = element.findElementById("com.tencent.mm:id/e38")
    print(pl)
    d.click(pl[0], pl[1])


# forwardPYQ()
findTP()
