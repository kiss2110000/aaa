#!/usr/bin/python
# coding:utf-8

import uiautomator2 as u2
import xml.etree.ElementTree as ET
import time
import re
import os

d = u2.connect('192.168.0.100')

DEBUG = False
HEIGHT = 1920
WIDTH = 1080


def openWXFS():
    """启用微信分身"""
    # Home键返回桌面
    d.shell("input keyevent 3")
    # os.system("adb shell input keyevent 3")
    # 点击微信分身
    d(text=u"Ⅱ·微信", resourceId="com.bbk.launcher2:id/item_title").click(timeout=5)


def openWXBZPYQ():
    # 启动微信本尊,打开朋友发表页面
    d.shell("am start com.tencent.mm/com.tencent.mm.ui.LauncherUI")
    # 检查是否为发表页面
    result = d(description="拍照分享").exists.__bool__()
    # print(type(result))
    if result is False:
        print("正在打开朋友圈... ...")
        is_gone = d(description="返回").click_gone(maxretry=5, interval=1.0)
        if is_gone is True:
            d(text="发现").click(timeout=10)
            d(text="朋友圈").click(timeout=10)
            return True
        print("找不到朋友圈！")
        return False
    return True


def saveXML(file):
    # 获取xml内容
    string = d.dump_hierarchy()
    # 保存为txt到磁盘
    with open(file + ".txt","w", encoding='utf-8') as f:
        f.write(string)


def findElement(file, resourceId=None, text=None, className=None, description=None, index=None):
    # 将xml的txt文件,转为xml格式
    with open(file + ".txt","r", encoding='utf-8') as f:
        tree = ET.fromstring(f.read())
    # 循环每个tag=node节点,找到第一个匹配的节点
    treeIter = tree.iter(tag="node")
    for elem in treeIter:
        # if index is not None:
        #     if elem.attrib["index"] != index:
        #         continue
        if resourceId is not None:
            if elem.attrib["resource-id"] != resourceId:
                continue
        if text is not None:
            if elem.attrib["text"] != text:
                continue
        if className is not None:
            if elem.attrib["class"] != className:
                continue
        if description is not None:
            if elem.attrib["content-desc"] != description:
                continue
        return elem


def findElements(file, resourceId=None, text=None, className=None, description=None):
    node_list = []
    # 将xml的txt文件,转为xml格式
    with open(file + ".txt","r", encoding='utf-8') as f:
        tree = ET.fromstring(f.read())
    # 循环每个tag=node节点,将找到的匹配节点全部添加到列表中
    treeIter = tree.iter(tag="node")
    for elem in treeIter:
        if resourceId is not None:
            if elem.attrib["resource-id"] != resourceId:
                continue
        if text is not None:
            if elem.attrib["text"] != text:
                continue
        if className is not None:
            if elem.attrib["class"] != className:
                continue
        if description is not None:
            if elem.attrib["content-desc"] != description:
                continue
        node_list.append(elem)
    return node_list


def getCenter(elem):
    pattern = re.compile(r"\d+")
    size = d.window_size()
    bounds = elem.attrib["bounds"]
    coord = pattern.findall(bounds)
    Xpoint = ((int(coord[2]) - int(coord[0])) / 2.0 + int(coord[0]))/size[0]
    Ypoint = ((int(coord[3]) - int(coord[1])) / 2.0 + int(coord[1]))/size[1]
    return Xpoint, Ypoint


def clickElem(elem):
    pos = getCenter(elem)
    d.click(pos[0],pos[1])
    time.sleep(0.3)


def findElemsInPhotoList():
    """找到相册列表的所有内容,取其最后一条"""
    file = "xiangceliebiao"
    saveXML(file)
    elms = findElements(file, resourceId='com.tencent.mm:id/kl')
    if len(elms) == 0:
        print("没有找到相册列表的任何数据！")
        return None
    return elms


def checkPhotoElemType(elem):
    """
    检查相册列表发布动态的类型
    动态的类型：纯文字、纯视频、纯图片列表、图文（一张图）、图文列表（大于1张）、视频文字、空类型
    7 中类型：word photoList video photoWord videoWord photoWordList empty
    """
    elem_type = None

    view_num = 0
    text_num = 0
    image_num = 0
    text_empty = None
    text_count = None
    # 循环检查每个部件，获取属性
    for child in elem.iter():
        # print(child.attrib["class"])
        if child.attrib["class"] == "android.widget.TextView":
            text_num += 1
            content = child.attrib["text"]
            if content == "":
                text_empty = True
            elif re.match(r'^共\d张$', content) is not None:
                text_count = True
        elif child.attrib["class"] == "android.view.View":
            view_num += 1
        elif child.attrib["class"] == "android.widget.ImageView":
            image_num += 1
    # 排除边框高度小于237的内容，因为他们的属性不全（有可能看不到ImageView）
    bounds = getElemBound(elem)
    if (bounds[3] - bounds[1])< 237 and view_num != 0:
        elem_type = "half"
    # 从属性判断类型
    elif text_num == 1 and view_num == 0 and image_num == 0:
        elem_type = "word"
    elif text_num == 0 and view_num > 0 and image_num == 0:
        elem_type = "photoList"
    elif text_num == 0 and view_num == 1 and image_num == 1:
        elem_type = "video"
    elif text_num == 1 and view_num == 1 and image_num == 0:
        elem_type = "photoWord"
    elif text_num >= 2 and view_num == 1 and image_num == 1 and text_empty is True:
        elem_type = "videoWord"
    elif text_num == 2 and view_num == 1 and image_num == 0 and text_count is True:
        elem_type = "photoWordList"
    elif text_num == 0 and view_num == 0 and image_num == 0:
        elem_type = "empty"
    return elem_type


def copyText():
    """在详情页面，复制发表的文字"""
    if d(text="详情").wait(timeout=3.0) is False:
        return False
    d.long_click(0.191, 0.184)
    d(text="复制").click(timeout=10)
    return True


def downloadImage():
    time.sleep(1)
    result = d(className="android.widget.ProgressBar").wait_gone(timeout=20)
    # print(result)
    if result is False:
        print("下载失败，检查网络是否正常！")
        d(description=u"返回").click(timeout=10)
        return False
    d.long_click(0.5, 0.5, 1)
    d(text=u"保存图片").click(timeout=10)
    result = d(className="android.widget.ProgressBar").wait_gone(timeout=20)
    # print(result)
    if result is False:
        print("下载失败，检查网络是否正常！")
        d(description=u"返回").click(timeout=10)
        return False
    return True


def setSecret():
    # 设置私密
    d(text=u"公开").click(timeout=5)
    d(text=u"私密").click(timeout=5)
    d(text=u"完成").click(timeout=5)


def getElemInPhotoPool():
    """找到相册文件夹的前9个文件,因为最多传9个图片"""
    file = "zhaopianchi"
    saveXML(file)
    elms = findElements(file, resourceId="com.tencent.mm:id/h0")
    if len(elms) == 0:
        print("没有找到照片池的任何数据！")
        return None
    return elms[0:9]


def publishImages(photo_num, photo_index=0, paste_text=None):
    result = False
    if photo_num > 9:
        photo_num = 9
    if photo_num <= 0:
        return "没有照片发表"
    d(description=u"拍照分享").click()
    d(text=u"从相册选择").click(timeout=5)
    time.sleep(0.5)
    # 获取照片池的前9个节点,因为最多传9个图片
    elms = getElemInPhotoPool()
    # print(elms[3].attrib["resource-id"])
    if elms is None:
        print("没有找到图片")
        return False
    if photo_num != 0:
        # 索引切片：从第几个开始(index)
        elms = elms[photo_index:photo_index+1]
    # 切片获取所需要的几个节点，循环选择
    elms = elms[0:photo_num]
    for elem in reversed(elms):
        # print(elem.attrib["resource-id"])
        # 检查每个节点中是否存在选择框部件,存在就选择
        for child in elem.iter():
            # print(elem.attrib["resource-id"])
            # print(child.attrib["class"])
            if child.attrib["class"] == "android.widget.CheckBox":
                # 检查是否有选择框部件，来选择图片
                clickElem(child)
                result = True
        if result is False:
            print("{}此节点不是图片".format(elem.attrib["resource-id"]))
    d(text=u"完成({}/9)".format(photo_num)).click(timeout=5)
    # 是否粘贴文字
    if paste_text is not None:
        d(text=u"这一刻的想法...").long_click()
        d(text=u"粘贴").click(timeout=10)
    # 设置私密
    setSecret()
    # 点击发布
    d(text=u"发表").click(timeout=10)
    print("发表了{}张照片".format(photo_num))


def saveElemToDisk(elem, elem_type):
    """6中类型：empty word photoList video photoWord videoWord photoWordList """
    print(" -- 开始保存....")
    result = False
    # 判断类型,选择保存
    if elem_type == "word":
        clickElem(elem)
        # 保存
        result = copyText()
        d(description=u"返回").click(timeout=10)
        if result is True:
            # 发表，打开朋友圈
            print(" -- 开始发表...")
            openWXBZPYQ()
            d(description=u"拍照分享").long_click()
            d(text=u"这一刻的想法...").long_click()
            d(text=u"粘贴").click(timeout=10)
            # 设置秘密
            setSecret()
            d(text=u"发表").click(timeout=10)
            print(" -- 发表结束")
            openWXFS()
        return True
    elif elem_type == "photoList":
        photo_num = 0
        for child in elem.iter():
            # 找到图片按钮,点击进入阅读模式
            if child.attrib["class"] == "android.view.View":
                # 保存
                photo_num += 1
                clickElem(child)
                # 保存图片
                downloadImage()
                d(description=u"返回").click(timeout=10)
                print(" -- 保存了图片{}".format(photo_num))

        # 发表，打开本尊朋友圈
        openWXBZPYQ()
        for i in reversed(range(photo_num)):
            publishImages(1, photo_index=i)
        openWXFS()
        print(" -- 发表结束 -- ")
        return True
    elif elem_type == "video":
        for child in elem.iter():
            # 找到视频按钮,点击进入阅读模式
            if child.attrib["class"] == "android.view.View":
                # 保存
                clickElem(child)
                time.sleep(1)
                result = d(className="android.widget.ProgressBar").wait_gone(timeout=20)
                # print(result)
                if result is False:
                    print("下载失败，检查网络是否正常！")
                    d(description=u"返回").click(timeout=10)
                    return False
                d.long_click(0.5,0.5,1)
                d(text=u"保存视频").click(timeout=10)
                d(description=u"返回").click(timeout=10)
                print("保存了视频")

        # 发表，打开朋友圈
        openWXBZPYQ()
        d(description=u"拍照分享").click()
        d(text=u"从相册选择").click(timeout=5)
        time.sleep(0.5)
        # 从照片池选择文件
        elms = getElemInPhotoPool()
        if elms is None:
            print("没有找到视频")
            return False
        elms = elms[0]
        for child in elms.iter():
            # print(child.attrib["class"])
            if child.attrib["class"] == "android.widget.TextView":
                # 检查是否有文本字段，记录视频时间
                clickElem(elms)
                d(text=u"完成").click(timeout=5)
                result = d(className="android.widget.ProgressBar").wait_gone(timeout=300)
                if result is False:
                    print("转码失败！")
                    return False
                setSecret()
                d(text=u"发表").click(timeout=10)
                print("发表了视频")
                result = True
        if result is False:
            print("没有找到视频文件")
        openWXFS()
        return True
    elif elem_type == "photoWord":
        # 点击进入阅读模式,在进入详情模式
        clickElem(elem)
        d(className="android.widget.ImageView", instance=3).click(timeout=5)
        # 检查是否是详情模式
        d.implicitly_wait(10.0)
        result = d(resourceId="android:id/text1").exists()
        print(result)
        if result is False:
            print("没有找到详情模式")
            return False
        # 保存
        result = copyText()
        print("复制文字{}".format(result))
        # 返回阅读模式
        d(description=u"返回").click(timeout=10)
        # 保存图片
        downloadImage()
        # 从阅读模式返回相册列表
        d(description=u"返回").click(timeout=10)
        print("保存了图片和文字")

        # 发表，打开朋友圈
        openWXBZPYQ()
        d(description=u"拍照分享").click()
        d(text=u"从相册选择").click(timeout=5)
        time.sleep(0.5)
        # 从照片池选择文件
        elms = getElemInPhotoPool()
        if elms is None:
            print("没有找到图片")
            return False
        elms = elms[0]
        for child in elms.iter():
            print(child.attrib["class"])
            if child.attrib["class"] == "android.widget.CheckBox":
                # 检查是否有选择框部件，来选择图片
                clickElem(child)
                d(text=u"完成(1/9)").click(timeout=5)
                d(text=u"这一刻的想法...").long_click()
                d(text=u"粘贴").click(timeout=10)

                setSecret()
                d(text=u"发表").click(timeout=10)
                print("发表了图文")
                result = True
        if result is False:
            print("没有找到图片文件")
        openWXFS()
        return True
    elif elem_type == "videoWord":
        # 点击进入阅读模式,在进入详情模式
        clickElem(elem)
        d(className="android.widget.ImageView", instance=3).click(timeout=5)
        # 检查是否是详情模式
        d.implicitly_wait(10.0)
        result = d(text="详情").exists(timeout=10)
        print(result)
        if result is False:
            print("没有找到详情模式")
            return False
        # 保存
        result = copyText()
        print("复制文字{}".format(result))
        # 返回阅读模式
        d(description=u"返回").click(timeout=10)

        # 保存视频有两次延迟，一次保存之前，一次保存之后
        time.sleep(1)
        result = d(className="android.widget.ProgressBar").wait_gone(timeout=20)
        # print(result)
        if result is False:
            print("下载失败，检查网络是否正常！")
            d(description=u"返回").click(timeout=10)
            return False

        d.long_click(0.5,0.5,1)
        d(text=u"保存视频").click(timeout=10)

        # 控制延迟
        time.sleep(1)
        result = d(className="android.widget.ProgressBar").wait_gone(timeout=20)
        # print(result)
        if result is False:
            print("下载失败，检查网络是否正常！")
            d(description=u"返回").click(timeout=10)
            return False

        # 从阅读模式返回相册列表
        d(description=u"返回").click(timeout=10)
        print("保存了视频和文字")

        # 发表，打开朋友圈
        openWXBZPYQ()
        d(description=u"拍照分享").click()
        d(text=u"从相册选择").click(timeout=5)
        time.sleep(0.5)
        # 从照片池选择文件
        elms = getElemInPhotoPool()
        if elms is None:
            print("没有找到视频")
            return False
        elms = elms[0]
        print()
        for child in elms.iter():
            print(child.attrib["class"])
            if child.attrib["class"] == "android.widget.TextView":
                # 检查是否有文本字段，记录视频时间
                clickElem(elms)
                d(text=u"完成").click(timeout=5)
                result = d(className="android.widget.ProgressBar").wait_gone(timeout=60)
                if result is False:
                    print("转码失败！")
                    return False
                d(text=u"这一刻的想法...").long_click()
                d(text=u"粘贴").click(timeout=10)
                setSecret()
                d(text=u"发表").click(timeout=10)
                print("发表了视频文字")
                result = True
        if result is False:
            print("没有找到视频文件")
        openWXFS()
        return True
    elif elem_type == "photoWordList":
        # 点击进入阅读模式,在进入详情模式
        clickElem(elem)
        d(className="android.widget.ImageView", instance=3).click(timeout=5)
        # 检查是否是详情模式
        d.implicitly_wait(10.0)
        result = d(resourceId="android:id/text1").exists()
        # print(result)
        if result is False:
            print("没有找到详情模式")
            return False
        # 保存
        result = copyText()
        print(" -- 复制文字:{}".format(result))
        # 获取九宫格的节点,只有一个
        file = "xiangqing"
        saveXML(file)
        elem = findElement(file, resourceId='com.tencent.mm:id/e6j')
        photo_num = 0
        # 只需查找elem的子级,每个子级节点都是一个图片
        for child in elem:
            photo_num += 1
            # print(child.attrib["resource-id"])
            # 点击打开图片
            clickElem(child)
            # 保存图片
            downloadImage()
            # 返回查看模式
            d.click(0.5, 0.5)
            time.sleep(0.5)
            print(" -- 保存了{}图片".format(photo_num))

        # 从详情模式返回相册列表
        d(description=u"返回").click(timeout=10)
        d(description=u"返回").click(timeout=10)
        print(" -- 保存了图片和文字")
        print(" -- 开始发表....")
        # 发表，打开微信本尊朋友圈
        openWXBZPYQ()
        d(description=u"拍照分享").click()
        d(text=u"从相册选择").click(timeout=5)
        time.sleep(0.5)
        # 获取照片池的前9个节点,因为最多传9个图片
        elms = getElemInPhotoPool()
        if elms is None:
            print("没有找到图片")
            return False
        # 切片获取所需要的几个节点，循环选择
        elms = elms[0:photo_num]
        for elem in reversed(elms):
            # 检查每个节点中是否存在选择框部件,存在就选择
            for child in elem.iter():
                # print(child.attrib["class"])
                if child.attrib["class"] == "android.widget.CheckBox":
                    # 检查是否有选择框部件，来选择图片
                    clickElem(child)

        d(text=u"完成({}/9)".format(photo_num)).click(timeout=10)
        d(text=u"这一刻的想法...").long_click(timeout=10)
        d(text=u"粘贴").click(timeout=10)

        setSecret()
        d(text=u"发表").click(timeout=10)
        print(" -- 发表了图文")
        result = True
        if result is False:
            print("没有找到图片文件")
        openWXFS()
        return True
    return result


def getElemBound(elem):
    bounds = elem.attrib["bounds"]
    pattern = re.compile(r'\d+')
    bounds = list(map(int, pattern.findall(bounds)))
    return bounds


def swipeUpElemToEnd(elem):
    """拖动换下一行"""
    time.sleep(0.2)
    hie_pre = d.dump_hierarchy()
    bounds = getElemBound(elem)
    d.swipe(540, bounds[1]+(bounds[3]-bounds[1])/2, 540, HEIGHT)
    time.sleep(0.1)
    hie_post = d.dump_hierarchy()
    # print("高度{} 起点{} 终点{} 移动距离{}".format(bounds[3]-bounds[1],bounds[1],bounds[3],HEIGHT-bounds[1]))
    if hie_pre == hie_post:
        print("原地滑动！")
        return False
    return True


def zhuanfaPYQ():
    """打开好友相册列表，找到要转发的第一条内容，将其拖动到屏幕的下端（保持下面还有半个）,然后启用"""
    num=0
    result = True
    ui = d(text="今天")
    while result:
        if ui.exists() is True and ui.center()[1] > 700:
            break
        last_elem = findElemsInPhotoList()[-2]
        # 检查此条内容的格式：纯文字、纯视频、纯图片列表、图文（一张图）、图文列表（大于1张）、视频文字
        elem_type = checkPhotoElemType(last_elem)
        # 如果最后一条为空或者没有匹配，则滑动屏幕，获取倒数第二个的类型
        if elem_type == "empty" or elem_type is None:
            swipeUpElemToEnd(last_elem)
            print("没有匹配到相册列表的任何类型或者是空的！")
            continue
        # DEBUG
        print("检测到的类型:", elem_type)
        # for i in last_elem.iter():
        #     if i.attrib["class"] == "android.widget.TextView":
        #         print("检测所有：", i.attrib["text"])
        # 保存发表
        result = saveElemToDisk(last_elem, elem_type)
        # result = True
        if result is False:
            return False

        # 发表完后向下滑动
        num+=1
        result = swipeUpElemToEnd(last_elem)
        print("-" * 50)
    if ui.exists() is True and ui.center()[1] > 700:
        elms = findElemsInPhotoList()
        # print(len(elms))
        elms = elms[:len(elms)-1]
        # print(len(elms))
        for elem in reversed(elms):
            elem_type = checkPhotoElemType(elem)
            # 如果最后一条为空或者没有匹配，则滑动屏幕，获取倒数第二个的类型
            if elem_type == "empty" or elem_type is None:
                print("没有匹配到相册列表的任何类型或者是空的！")
                continue
            # DEBUG
            print("检测到的类型:", elem_type)
            for i in elem.iter():
                if i.attrib["class"] == "android.widget.TextView":
                    print("检测所有：", i.attrib["text"])
            # 保存发表
            result = saveElemToDisk(elem, elem_type)
            num+=1
            # result = True
            if result is False:
                return False
    print("总共转发{}".format(num))




if __name__ == "__main__":
    # zhuanfaPYQ()
    d.shell("adb")
    # print(d.implicitly_wait(10.0))
    # result = d(resourceId="android:id/text1").exists()
    # ui = d(text="今天")
    # if ui.exists() is True and ui.center()[1]>700:






