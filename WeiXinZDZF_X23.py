#!/usr/bin/python
# coding:utf-8

import uiautomator2 as u2
import xml.etree.ElementTree as ET
import time
import re
import os

# d = u2.connect('192.168.0.100')
# d = u2.connect_usb('1208ceba')
# d = u2.connect_usb('c176b27d')
d = u2.connect()

# d.disable_popups()
DEBUG = False
size = d.window_size()
# HEIGHT = size[1]
WIDTH = size[0]
HEIGHT = 2214


def openWXFS():
    """vivo X23 启用微信分身"""
    num = 0
    while num < 5:
        try:
            d.shell("am start com.tencent.mm/com.tencent.mm.ui.LauncherUI")
            d(text="Ⅱ·微信").click(timeout=0.5)
            print(" -- 点击了微信分身")
            num = 6
        except:
            num += 1
            print("警告：正在尝试重新打开微信分身！")


# def openWXFS():
#     """vivo X7 启用微信分身"""
#     # Home键返回桌面
#     d.shell("input keyevent 3")
#     # os.system("adb shell input keyevent 3")
#     # 点击微信分身
#     d(text=u"Ⅱ·微信", resourceId="com.bbk.launcher2:id/item_title").click(timeout=5)


def openWXBZ():
    # 启动微信本尊,打开朋友发表页面
    num = 0
    while num < 5:
        try:
            d.shell("am start com.tencent.mm/com.tencent.mm.ui.LauncherUI")
            d(text="微信").click(timeout=0.5)
            num = 6
        except:
            num += 1
            print("警告：正在尝试重新打开微信本尊！")


def openDownloadWX():
    openWXFS()


def openUploadWXPYQ():
    openWXBZ()
    # 检查是否为发表页面
    result = d(description="拍照分享").exists(timeout=1.5)
    if not result:
        if DEBUG:
            print("Debug -- 正在退回微信主页面....")
        is_gone = d(description="返回",
                    packageName="com.tencent.mm",
                    className="android.widget.ImageView").click_gone(maxretry=20, interval=0.01)
        if is_gone is True:
            if DEBUG:
                print("Debug -- 开始点击发现，进入朋友圈页面....")
            d(text="发现").click(timeout=5)
            d(text="朋友圈").click(timeout=5)
            print(" -- 已打开朋友圈页面")
            return True
        print("错误：找不到朋友圈页面！")
        return False
    return True


def saveXML(file):
    # 获取xml内容
    string = d.dump_hierarchy()
    # 保存为txt到磁盘
    with open(file + ".txt", "w", encoding='utf-8') as f:
        f.write(string)


def findElement(file, resourceId=None, text=None, className=None, description=None, index=None):
    # 将xml的txt文件,转为xml格式
    with open(file + ".txt", "r", encoding='utf-8') as f:
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
    with open(file + ".txt", "r", encoding='utf-8') as f:
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
    # print(size)
    bounds = elem.attrib["bounds"]
    coord = pattern.findall(bounds)
    Xpoint = ((int(coord[2]) - int(coord[0])) / 2.0 + int(coord[0])) / size[0]
    Ypoint = ((int(coord[3]) - int(coord[1])) / 2.0 + int(coord[1])) / size[1]
    return Xpoint, Ypoint


def clickElem(elem):
    click_pre = d.dump_hierarchy()
    num = 0
    while num < 3:
        pos = getCenter(elem)
        d.click(pos[0], pos[1])
        time.sleep(0.3)
        click_now = d.dump_hierarchy()
        num += 1
        if click_pre != click_now:
            return True
        exist = d(resourceId=elem.attrib['resource-id']).exists()
        if exist is False:
            print("错误：点击失败！")
            num = 4
        else:
            print("警告：正在尝试重新点击:{}次！".format(num))
    return False


def copyText(get_text=False):
    """在详情页面，复制发表的文字"""
    if DEBUG:
        print("Debug -- 开始复制文字")
    if not get_text:
        num = 0
        while num < 5:
            try:
                d(resourceId="com.tencent.mm:id/jv").long_click(duration=0.6)
                d(text="复制").click(timeout=1)
                return True
            except:
                num += 1
                print("警告：正在尝试复制文字！")
                if num >= 5:
                    print("错误：复制文字失败！")
                    return False
    else:
        word = d(resourceId="com.tencent.mm:id/jv").get_text(timeout=5)
        find = re.findall("\d{10,18}", word)
        if not find:
            jiage = re.findall(r"💰\d{2:}",word)
            print(jiage)
        for i in find:
            o = i[-3:]
            if o[0] == "0":
                o = o[1:]
            word = word.replace(i, "💰" + o)
        return word


def pasteText(set_text=None):
    """在发表页面，粘贴文字"""
    if set_text is None:
        d(resourceId="com.tencent.mm:id/cib", text=u"这一刻的想法...").long_click(timeout=1, duration=0.6)
        d(text=u"粘贴").click(timeout=1)
    else:
        d(resourceId="com.tencent.mm:id/cib", text=u"这一刻的想法...").set_text(set_text, timeout=1)
        result = d(resourceId="com.tencent.mm:id/br2", description=u"表情").exists(timeout=1)
        if result is True:
            d.press("back")


def setSecret():
    # 设置私密
    d(text=u"公开").click(timeout=10)
    d(text=u"私密").click(timeout=10)
    d(text=u"完成").click(timeout=10)


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
    7 中类型：word photoList video photoWord videoWord photoWordList empty half None
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
        if child.attrib["class"] == "android.widget.TextView" and \
                (child.attrib["resource-id"] == "com.tencent.mm:id/e51" or
                 child.attrib["resource-id"] == "com.tencent.mm:id/mi" or
                 child.attrib["resource-id"] == "com.tencent.mm:id/jv"):
            text_num += 1
            content = child.attrib["text"]
            if content == "":
                text_empty = True
            elif re.match(r'^共\d张$', content) is not None:
                text_count = True
        elif child.attrib["class"] == "android.view.View" and \
                (child.attrib["resource-id"] == "com.tencent.mm:id/e1b" or
                 child.attrib["resource-id"] == "com.tencent.mm:id/e1c" or
                 child.attrib["resource-id"] == "com.tencent.mm:id/e1d"):
            view_num += 1
        elif child.attrib["class"] == "android.widget.ImageView":
            image_num += 1
    # 排除边框高度小于237的内容，因为他们的属性不全（有可能看不到ImageView）
    bounds = getElemBound(elem)
    if (bounds[3] - bounds[1]) < 237 and view_num > 0:
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


def getElemInPhotoPool():
    """找到相册文件夹的前9个文件,因为最多传9个图片"""
    file = "zhaopianchi"
    saveXML(file)
    elms = findElements(file, resourceId="com.tencent.mm:id/h0")
    if len(elms) == 0:
        print("没有找到照片池的任何数据！")
        return None
    return elms[0:9]


def downloadImage(video=False):
    if DEBUG:
        print("Debug -- 等待查看模式")
    result = d(className="android.widget.Gallery").wait(timeout=5)
    if result is False:
        print("错误：当前页面不是阅读或查看页面!")
        return False
    if DEBUG:
        print("Debug -- 开始下载")
    attempts = 0
    success = False
    while attempts <= 3 and not success:
        try:
            result = d(className="android.widget.ProgressBar").wait_gone(timeout=600)
            if result is False:
                print("错误：下载失败，检查网络是否正常！")
                return False
            if video is False:
                if DEBUG:
                    print("Debug -- 下载图片")
                if not d(text=u"保存图片").exists():
                    d(className="android.widget.Gallery").long_click(duration=0.6, timeout=0.1)
                d(text=u"保存图片").click(timeout=2)
            else:
                if DEBUG:
                    print("Debug -- 下载视频")
                if not d(text=u"保存视频").exists():
                    d(className="android.widget.Gallery").long_click(duration=0.6, timeout=0.1)
                d(text=u"保存视频").click(timeout=2)
                time.sleep(2)
            result = d(className="android.widget.CompoundButton").wait_gone(timeout=600)
            if result is False:
                print("错误：下载失败，检查网络是否正常！")
                return False
            success = True
            if DEBUG:
                print("Debug -- 下载完成")
        except:
            if attempts == 3:
                print("错误：下载失败!")
                return False
            attempts += 1
            print("警告：正在尝试重新下载...")
    return True


def uploadImages(upload_num=1, photo_index=0, video=False, paste_text=False, word=None):
    if video is False:
        if upload_num > 9:
            upload_num = 9
        if upload_num <= 0:
            return "没有照片发表"
    if DEBUG:
        print("Debug -- 等待拍照分享按钮")
    d(description=u"拍照分享").click(timeout=10)
    d(text=u"从相册选择").click(timeout=10)
    d(text=u"图片和视频").wait(timeout=15)
    if DEBUG:
        print("Debug -- 获取照片池")
    # 获取照片池的前9个节点,因为最多传9个图片
    elms = getElemInPhotoPool()
    if elms is None:
        print("错误：没有找到照片池的任何东西!")
        return False
    # 判断是上传图片还是视频
    if video is False:
        if DEBUG:
            print("Debug -- 开始上传图片")
        if photo_index != 0:
            # 索引切片：从第几个开始(index)
            elms = elms[photo_index:photo_index + 1]
        # 切片获取所需要的几个节点，循环选择
        elms = elms[0:upload_num]
        for elem in reversed(elms):
            result = False
            # 检查每个节点中是否存在选择框部件,存在就选择
            if DEBUG:
                print("Debug -- 找到选择框按钮")
            for child in elem.iter():
                if child.attrib["class"] == "android.widget.CheckBox":
                    if DEBUG:
                        print("Debug -- 点击选择框按钮")
                    d(resourceId=child.attrib["resource-id"], className=child.attrib["class"],
                      instance=elem.attrib["index"]).click(timeout=5)
                    result = True
            if result is False:
                print("{}此节点不是图片".format(elem.attrib["resource-id"]))
        d(text=u"完成({}/9)".format(upload_num)).click(timeout=10)
    elif video is True:
        result = False
        elem = elms[0]
        if DEBUG:
            print("Debug -- 查找文字字段")
        for child in elem.iter():
            if child.attrib["class"] == "android.widget.TextView":
                # 第一个ID就是刚刚报存的视频
                if DEBUG:
                    print("Debug -- 选择视频")
                d(resourceId=child.attrib["resource-id"]).click(timeout=5)
                result = True
        if result is False:
            print("错误：{}此节点不是视频".format(elem.attrib["resource-id"]))
            return False
        # 如果视频时长超过10秒，则需要编辑一下
        d(text=u"完成").wait(timeout=0.5)
        if d(text=u"编辑视频").exists():
            if DEBUG:
                print("Debug -- 编辑视频时长")
            d(text=u"编辑").click(timeout=10)
            d(text=u"完成").click(timeout=10)
            d(text=u"完成").click(timeout=10)
        else:
            d(text=u"完成").click(timeout=10)
        if DEBUG:
            print("Debug -- 等待视频转码")
        d(className="android.widget.ProgressBar").wait(timeout=2)
        result = d(className="android.widget.ProgressBar").wait_gone(timeout=300)
        if result is False:
            print("错误：转码失败！")
            return False
    if DEBUG:
        print("Debug -- 等待编辑发布页面")
    result = d(text=u"这一刻的想法...").wait(timeout=10)
    if result is False:
        print("没有发现'这一刻的想法...'的部件!")
    # 是否粘贴文字
    if paste_text is True:
        if DEBUG:
            print("Debug -- 粘贴文字内容")
        attempts = 0
        success = False
        while attempts < 3 and not success:
            try:
                pasteText(set_text=word)
                success = True
            except:
                attempts += 1
                print("警告：正在尝试重新粘贴...")
                if attempts == 3:
                    print("错误：粘贴文字失败，没有显示粘贴键!")
                    return False
    # 设置私密
    # setSecret()
    # 点击发布
    d(text=u"发表").click(timeout=10)
    print(" -- 发表了{}张照片".format(upload_num))


def uploadAndDownloadElem(elem, elem_type):
    """6中类型：empty word photoList video photoWord videoWord photoWordList """
    print(" -- 开始保存....")
    result = False
    # 判断类型,选择保存
    if elem_type == "word":
        # 点击进入详情
        clickElem(elem)
        # 保存
        word = copyText(get_text=True)
        print(" -- 复制文字:{}".format(word))
        d(description=u"返回", packageName="com.tencent.mm").click(timeout=10)
        if word is False:
            print("错误：文字复制失败！")
            return False

        # 发表，打开朋友圈
        print(" -- 开始发表...")
        openUploadWXPYQ()
        d(description=u"拍照分享").long_click(duration=0.6)
        pasteText(set_text=word)
        # 设置秘密
        # setSecret()
        d(text=u"发表").click(timeout=10)
        openDownloadWX()
        print(" -- 发表结束")
        return True
    elif elem_type == "photoList":
        photo_num = 0
        for child in elem.iter():
            # 找到每个图片的按钮,点击进入阅读模式,并保存
            if child.attrib["class"] == "android.view.View" and \
                    (child.attrib["resource-id"] == "com.tencent.mm:id/e1b" or
                     child.attrib["resource-id"] == "com.tencent.mm:id/e1c" or
                     child.attrib["resource-id"] == "com.tencent.mm:id/e1d"):
                photo_num += 1
                # 点击打开图片
                clickElem(child)
                result = downloadImage()
                if result is False:
                    print("错误：下载失败！")
                    return False
                d(description=u"返回", packageName="com.tencent.mm").click(timeout=10)
                print(" -- 保存了图片{}".format(photo_num))

        # 发表，打开本尊朋友圈
        openUploadWXPYQ()
        for i in reversed(range(photo_num)):
            result = uploadImages(photo_index=i)
            if result is False:
                print("错误：上传失败！")
                return False
        openDownloadWX()
        print(" -- 发表结束 -- ")
        return True
    elif elem_type == "video":
        for child in elem.iter():
            # 找到视频按钮,点击进入阅读模式,然后直接保存视频
            if child.attrib["class"] == "android.view.View" and \
                    child.attrib["content-desc"] == u"图片":
                # 点击打开视频
                clickElem(child)
                result = downloadImage(video=True)
                if result is False:
                    print("下载失败！")
                    return False
                d(description=u"返回", packageName="com.tencent.mm").click(timeout=10)
                print("保存了视频")

        # 发表，打开朋友圈
        openUploadWXPYQ()
        result = uploadImages(video=True)
        if result is False:
            print("上传失败！")
            return False
        openDownloadWX()
        return True
    elif elem_type == "photoWord":
        # 点击进入阅读模式,在进入详情模式中复制文本
        clickElem(elem)
        d(className="android.widget.ImageView", instance=3).click(timeout=5)
        # 检查是否是详情模式
        result = d(text="详情").wait(timeout=30)
        if result is False:
            print("错误：没有找到详情模式")
            return False
        word = copyText(get_text=True)
        print(" -- 复制文字:{}".format(word))
        # 返回到阅读模式中保存图片,再从阅读模式返回相册列表
        d(description=u"返回", packageName="com.tencent.mm").click(timeout=10)
        result = downloadImage()
        if result is False:
            print("错误：下载失败！")
            return False
        d(description=u"返回", packageName="com.tencent.mm").click(timeout=10)
        print(" -- 保存了图片和文字")

        # 打开朋友圈,发表
        openUploadWXPYQ()
        result = uploadImages(paste_text=True, word=word)
        if result is False:
            print("错误：上传失败！")
            return False
        openDownloadWX()
        return True
    elif elem_type == "videoWord":
        # 点击进入阅读模式,在进入详情模式中复制文本
        clickElem(elem)
        attempts, success = 0, False
        while not success:
            # print(elem.attrib["resource-id"])
            # print(elem.attrib["index"])
            # d(resourceId=elem.attrib["resource-id"], instance=elem.attrib["index"]).click(timeout=1)
            d(className="android.widget.ImageView", instance=3).click(timeout=1)
            # 检查是否是详情模式
            success = d(text="详情").wait(timeout=2)
            attempts += 1
            if attempts == 3 and not success:
                print("错误：没有找到详情模式!")
                return False

        word = copyText(get_text=True)
        print(" -- 复制文字:{}".format(word))
        # 返回阅读模式
        d(description=u"返回", packageName="com.tencent.mm").click(timeout=10)
        result = downloadImage(video=True)
        if result is False:
            print("错误：下载失败！")
            return False
        # 从阅读模式返回相册列表
        d(description=u"返回", packageName="com.tencent.mm").click(timeout=10)
        print(" -- 保存了视频和文字")

        # 发表，打开朋友圈
        openUploadWXPYQ()
        result = uploadImages(video=True, paste_text=True, word=word)
        if result is False:
            print("错误：上传失败！")
            return False
        openDownloadWX()
        return True
    elif elem_type == "photoWordList":
        # 点击进入阅读模式,在进入详情模式中复制文本
        clickElem(elem)
        d(className="android.widget.ImageView", instance=3).click(timeout=5)
        # 检查是否是详情模式
        result = d(text="详情").wait(timeout=30)
        if result is False:
            print("错误：没有找到详情模式")
            return False
        word = copyText(get_text=True)
        print(" -- 复制文字:{}".format(word))

        # 获取图片九宫格的节点,只有一个九宫格
        image = {0: "com.tencent.mm:id/e3e",
                 1: "com.tencent.mm:id/e6k",
                 2: "com.tencent.mm:id/e6l",
                 3: "com.tencent.mm:id/e6m",
                 4: "com.tencent.mm:id/e6n",
                 5: "com.tencent.mm:id/e6o",
                 6: "com.tencent.mm:id/e6p",
                 7: "com.tencent.mm:id/e6q",
                 8: "com.tencent.mm:id/e6r",
                 }
        # 获取图片九宫格的节点,只有一个九宫格
        file = "xiangqing"
        saveXML(file)
        elem = findElement(file, resourceId='com.tencent.mm:id/e6j')
        photo_num = 0
        # 只需查找elem的子级,每个子级节点都是一个图片
        for child in elem:
            # 点击打开图片
            # clickElem(child)
            d(resourceId=image[photo_num]).click(timeout=2)
            photo_num += 1
            # 保存图片
            result = downloadImage()
            if result is False:
                print("错误：下载失败！")
                return False
            # 返回详情模式
            d.click(0.5, 0.5)
            print(" -- 保存了{}图片".format(photo_num))
            # 检查是否返回到了详情模式
            result = d(text="详情").wait(timeout=30)
            if result is False:
                print("错误：没有返回到详情模式！")
                return False
        # 从详情模式返回相册列表
        d(description=u"返回", packageName="com.tencent.mm").click(timeout=10)
        d(description=u"返回", packageName="com.tencent.mm").click(timeout=10)
        print(" -- 保存完毕")
        print(" -- 开始发表....")
        # 发表，打开微信本尊朋友圈
        openUploadWXPYQ()
        result = uploadImages(upload_num=photo_num, paste_text=True, word=word)
        if result is False:
            print("错误：上传失败！")
            return False
        openDownloadWX()
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
    d.swipe(540, bounds[1] + (bounds[3] - bounds[1]) / 2, 540, HEIGHT)
    time.sleep(0.1)
    hie_post = d.dump_hierarchy()
    # print("高度{} 起点{} 终点{} 移动距离{}".format(bounds[3]-bounds[1],bounds[1],bounds[3],HEIGHT-bounds[1]))
    if hie_pre == hie_post:
        print("错误：原地滑动！")
        return False
    return True


def zhuanfaPYQ():
    """打开好友相册列表，找到要转发的第一条内容，将其拖动到屏幕的下端（保持下面还有半个）,然后启用"""
    num = 0
    result = True
    ui = d(text="今天")
    while result:
        start_time = time.perf_counter()

        if ui.exists() is True and ui.center()[1] > 700:
            break
        last_elem = findElemsInPhotoList()[-2]
        # 检查此条内容的格式：纯文字、纯视频、纯图片列表、图文（一张图）、图文列表（大于1张）、视频文字
        elem_type = checkPhotoElemType(last_elem)
        # 如果最后一条为空或者没有匹配，则滑动屏幕，获取倒数第二个的类型
        print("检测到的类型:", elem_type)
        if elem_type == "empty" or elem_type == "half" or elem_type is None:
            swipeUpElemToEnd(last_elem)
            print("警告：无法匹配相册列表的任何类型或者是空的！")
            continue
        # 开始下载保存和上传发表
        result = uploadAndDownloadElem(last_elem, elem_type)
        if result is False:
            return False
        # 发表完后向下滑动
        num += 1
        result = swipeUpElemToEnd(last_elem)

        # 计算时间
        end_time = time.perf_counter()
        dur_time = end_time - start_time
        str_time = "用时："
        if dur_time / 60 > 1:
            str_time += str(int(dur_time / 60)) + "分"
        str_time += str(round(dur_time % 60)) + "秒"
        # 输出结果
        print("-" * 50 + "已转发{}条  {}".format(num, str_time))
    if ui.exists() is True and ui.center()[1] > 700 and result is True:
        elms = findElemsInPhotoList()
        elms = elms[:len(elms) - 1]
        for elem in reversed(elms):
            start_time = time.perf_counter()

            elem_type = checkPhotoElemType(elem)
            # 如果最后一条为空或者没有匹配，则滑动屏幕，获取倒数第二个的类型
            if elem_type == "empty" or elem_type is None:
                print("没有匹配到相册列表的任何类型或者是空的！")
                continue
            print("检测到的类型:", elem_type)
            result = uploadAndDownloadElem(elem, elem_type)
            num += 1
            if result is False:
                return False

            # 计算时间
            end_time = time.perf_counter()
            dur_time = end_time - start_time
            str_time = "用时："
            if dur_time / 60 > 1:
                str_time += str(int(dur_time / 60)) + "分"
            str_time += str(round(dur_time % 60)) + "秒"

            # 输出结果
            print("-" * 50 + "已转发{}条  {}".format(num, str_time))
    print(" -- 总共转发{}".format(num))


if __name__ == "__main__":
    # openWXFS()
    # openWXBZ()
    # openDownloadWX()
    # openUploadWXPYQ()
    # print(copyText(get_text=True))
    # pasteText(set_text=None)
    # downloadImage(video=False)
    zhuanfaPYQ()
