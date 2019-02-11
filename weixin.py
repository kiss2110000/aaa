import uiautomator2 as u2
import xml.etree.ElementTree as ET
import time
import re
from version import *


# d = u2.connect('192.168.0.100')
# d = u2.connect_usb('1208ceba')
d = u2.connect_usb('c176b27d')
# d.disable_popups()
DEBUG = False
d.freeze_rotation()
size = d.window_size()


HEIGHT = size[1]
WIDTH = size[0]
BOTTON = 2214


# 检测到的手机名称
udid = d.device_info["udid"]
# 设备名称
vivoX7 = "c176b27d-18:e2:9f:2e:dd:78-vivo_X7Plus"
vivoX23 = "c176b27d-18:e2:9f:2e:dd:78-vivo_X23Plus"


Element = version["7.0.0"]


def openWXFS():
    """启用微信分身"""
    num = 0
    while num < 5:
        try:
            if udid == vivoX23:
                """vivo X23"""
                d.shell("am start com.tencent.mm/com.tencent.mm.ui.LauncherUI")
                d(text="Ⅱ·微信").click(timeout=0.5)
                print(" -- 点击了微信分身")
            elif udid == vivoX7:
                """vivo X7"""
                # Home键返回桌面,点击微信分身
                d.shell("input keyevent 3")
                d(text=u"Ⅱ·微信", resourceId="com.bbk.launcher2:id/item_title").click(timeout=5)
            num = 6
        except:
            num += 1
            print("警告：正在尝试重新打开微信分身！")


def openWXBZ():
    # 启动微信本尊,打开朋友发表页面
    num = 0
    while num < 5:
        try:
            if udid == vivoX23:
                d.shell("am start com.tencent.mm/com.tencent.mm.ui.LauncherUI")
                d(text="微信").click(timeout=0.5)
            elif udid == vivoX7:
                d.shell("am start com.tencent.mm/com.tencent.mm.ui.LauncherUI")
            num = 6
        except:
            num += 1
            print("警告：正在尝试重新打开微信本尊！")


def openDownloadWXXC():
    openWXFS()
    isAlbumMode()


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
                d(resourceId=Element["详情文字"]).long_click(duration=0.6)
                d(text="复制").click(timeout=1)
                return True
            except:
                num += 1
                print("警告：正在尝试复制文字！")
                if num >= 5:
                    print("错误：复制文字失败！")
                    return False
    else:
        word = d(resourceId=Element["详情文字"]).get_text(timeout=5)
        # 匹配
        find = re.findall("💰\d{2,3}", word)
        for i in find:
            o = i[1:]
            o = str(int(o) + 30)
            word = word.replace(i, "💰" + o)
        # 匹配 2201788105739145
        find = re.findall("\d{10,18}", word)
        for i in find:
            o = i[-3:]
            if o[0] == "0":
                o = o[1:]
            word = word.replace(i, "💰" + o)
        return word


def pasteText(set_text=None):
    """在发表页面，粘贴文字"""
    if set_text is None:
        d(text=u"这一刻的想法...").long_click(timeout=1, duration=0.6)
        d(text=u"粘贴").click(timeout=1)
    else:
        d(text=u"这一刻的想法...").set_text(set_text, timeout=1)
        result = d(description=u"表情").exists(timeout=1)
        if result is True:
            d.press("back")


def albumJumpReading(elem):
    # 找到视频按钮,点击进入阅读模式
    for child in elem.iter():
        if child.attrib["resource-id"] == Element["视频1部件"]:
            # 点击打开视频
            clickElem(child)
            # 检查是否为阅读模式
            isReadingMode()


def albumJumpReadingJumpDetails(elem):
    albumJumpReading(elem)
    d(resourceId=Element["评论按钮"]).click(timeout=5)
    # 检查是否为详情模式
    isDetailsMode()


def jumpToBack():
    d(description=u"返回", packageName="com.tencent.mm").click(timeout=10)


def setSecret():
    # 设置私密
    d(text=u"公开").click(timeout=10)
    d(text=u"私密").click(timeout=10)
    d(text=u"完成").click(timeout=10)


def isAlbumMode():
    """检测是否为相册列表"""
    assert d(resourceId=Element["照片列表"]).wait(timeout=5), "此页不是相册模式"


def isReadingMode():
    """检测是否为阅读模式"""
    assert d(resourceId=Element["阅读模式"], className="android.widget.Gallery",
             packageName="com.tencent.mm").wait(timeout=5), "此页不是阅读模式"


def isDetailsMode():
    """检测是否为详情模式"""
    assert d(resourceId="android:id/text1", text="详情",
             packageName="com.tencent.mm").wait(timeout=20), "此页不是详情模式"


def isFriendsPage():
    """检测是否为朋友圈发表页面"""
    assert d(resourceId=Element["拍照分享"], description="拍照分享",
             className="android.widget.ImageButton",
             packageName="com.tencent.mm").wait(timeout=5), "此页不是朋友圈发表页"


def isPublishEdit():
    """检测是否为发表编辑页面"""
    assert d(text=u"这一刻的想法...").wait(timeout=10), "此页不是发表编辑页面"


def findElemsInPhotoList():
    """找到相册列表的所有内容,取其最后一条"""
    file = "xiangceliebiao"
    saveXML(file)
    elms = findElements(file, resourceId=Element["照片列表"])
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
    empty_textView = None
    count_textView = None
    view_num, text_num, image_num = 0, 0, 0
    # 循环检查每个部件，获取文字部件、视频部件、图片部件的数量
    for child in elem.iter():
        # 是否为文字部件,并判断是空文字，还是计数文字
        if child.attrib["class"] == "android.widget.TextView" and \
                (child.attrib["resource-id"] == Element["纯文字部件"] or
                 child.attrib["resource-id"] == Element["描述文字部件"] or
                 child.attrib["resource-id"] == Element["计数文字部件"]):
            text_num += 1
            content = child.attrib["text"]
            if content == "":
                empty_textView = True
            elif re.match(r'^共\d张$', content) is not None:
                count_textView = True
        # 是否为视频部件
        elif child.attrib["class"] == "android.view.View" and \
                (child.attrib["resource-id"] == Element["视频1部件"] or
                 child.attrib["resource-id"] == Element["视频2部件"] or
                 child.attrib["resource-id"] == Element["视频3部件"]):
            view_num += 1
        # 是否为图片部件
        elif child.attrib["class"] == "android.widget.ImageView":
            image_num += 1

    # 从属性判断类型
    # 排除边框高度小于237的内容(还有可能是广告)，因为他们的属性不全（有可能看不到ImageView）
    bounds = getElemBound(elem)
    if (bounds[3] - bounds[1]) < 237 and view_num > 0:
        elem_type = "half"
    elif text_num == 1 and view_num == 0 and image_num == 0:
        elem_type = "word"
    elif text_num == 0 and view_num > 0 and image_num == 0:
        elem_type = "photoList"
    elif text_num == 0 and view_num == 1 and image_num == 1:
        elem_type = "video"
    elif text_num == 1 and view_num == 1 and image_num == 0:
        elem_type = "photoWord"
    elif text_num >= 2 and view_num == 1 and image_num == 1 and empty_textView is True:
        elem_type = "videoWord"
    elif text_num == 2 and view_num == 1 and image_num == 0 and count_textView is True:
        elem_type = "photoWordList"
    elif text_num == 0 and view_num == 0 and image_num == 0:
        elem_type = "empty"
    return elem_type


def getElemInPhotoPool():
    """找到相册文件夹的前9个文件,因为最多传9个图片"""
    file = "zhaopianchi"
    saveXML(file)
    elms = findElements(file, resourceId=Element["照片池"])
    if len(elms) == 0:
        print("没有找到照片池的任何数据！")
        return None
    return elms[0:9]


def downloadImage(video=False):
    attempts = 0
    success = False
    while attempts <= 3 and not success:
        try:
            assert d(className="android.widget.ProgressBar").wait_gone(timeout=600), "下载失败，检查网络是否正常！"
            if video is False:
                if not d(text=u"保存图片").exists():
                    d(className="android.widget.Gallery").long_click(duration=0.6, timeout=0.1)
                d(text=u"保存图片").click(timeout=2)
            else:
                if not d(text=u"保存视频").exists():
                    d(className="android.widget.Gallery").long_click(duration=0.6, timeout=0.1)
                d(text=u"保存视频").click(timeout=2)
                time.sleep(3)
            assert d(className="android.widget.CompoundButton").wait_gone(timeout=600), "下载失败，检查网络是否正常！"
            success = True
        except:
            assert attempts == 3, "下载失败！"
            attempts += 1
            print("警告：正在尝试重新下载...")
    return True


def uploadImages(upload_num=1, photo_index=0, video=False, paste_text=False, word=None):
    if video is False:
        if upload_num > 9:
            upload_num = 9
        if upload_num <= 0:
            return "没有照片发表"
    d(description=u"拍照分享").click(timeout=10)
    d(text=u"从相册选择").click(timeout=10)
    d(text=u"图片和视频").wait(timeout=15)
    # 获取照片池的前9个节点,因为最多传9个图片
    elms = getElemInPhotoPool()
    assert elms, "没有找到照片池的任何东西!"

    # 判断是上传图片还是视频
    if video is False:
        if photo_index != 0:
            # 索引切片：从第几个开始(index)
            elms = elms[photo_index:photo_index + 1]
        # 切片获取所需要的几个节点，循环选择
        elms = elms[0:upload_num]
        for elem in reversed(elms):
            result = False
            # 检查每个节点中是否存在选择框部件,存在就选择
            for child in elem.iter():
                if child.attrib["class"] == "android.widget.CheckBox":
                    d(resourceId=child.attrib["resource-id"], className=child.attrib["class"],
                      instance=elem.attrib["index"]).click(timeout=5)
                    result = True
            assert result, "{}此节点不是图片".format(elem.attrib["resource-id"])
        d(text=u"完成({}/9)".format(upload_num)).click(timeout=10)
    else:
        # 发表视频
        elem = elms[0]
        result = False
        for child in elem.iter():
            if child.attrib["class"] == "android.widget.TextView":
                # 第一个ID就是刚刚报存的视频
                d(resourceId=child.attrib["resource-id"]).click(timeout=5)
                result = True
        assert result, "{}此节点不是视频".format(elem.attrib["resource-id"])
        # 如果视频时长超过10秒，则需要编辑一下
        d(text=u"完成").wait(timeout=5)
        if d(text=u"编辑视频").exists():
            d(text=u"编辑").click(timeout=10)
            d(text=u"完成").click(timeout=10)
            d(text=u"完成").click(timeout=10)
        else:
            d(text=u"完成").click(timeout=10)
        d(className="android.widget.ProgressBar").wait(timeout=2)
        result = d(className="android.widget.ProgressBar").wait_gone(timeout=300)
        assert result, "转码失败！"

    isPublishEdit()
    # 是否粘贴文字
    if paste_text is True:
        attempts = 0
        success = False
        while attempts < 3 and not success:
            try:
                pasteText(set_text=word)
                success = True
            except:
                attempts += 1
                print("警告：正在尝试重新粘贴...")
                assert attempts == 3, "粘贴文字失败，没有显示粘贴键!"

    # 设置私密
    setSecret()
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
        isDetailsMode()

        word = copyText(get_text=True)
        if word is False:
            raise RuntimeError("文字复制失败！")
        print(" -- 复制文字:{}".format(word))
        jumpToBack()
        isAlbumMode()

        # 发表，打开朋友圈
        print(" -- 开始发表...")
        openUploadWXPYQ()
        d(description=u"拍照分享").long_click(duration=0.6)
        pasteText(set_text=word)
        # 设置秘密
        setSecret()
        d(text=u"发表").click(timeout=10)
        openDownloadWXXC()
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
                # 点击打开图片
                clickElem(child)
                isReadingMode()

                result = downloadImage()
                if result is False:
                    raise RuntimeError("下载失败！")
                photo_num += 1
                print(" -- 保存了图片{}".format(photo_num))
                jumpToBack()
                isAlbumMode()

        # 发表，打开本尊朋友圈
        openUploadWXPYQ()
        for i in reversed(range(photo_num)):
            result = uploadImages(photo_index=i)
            if result is False:
                raise RuntimeError("上传失败！")
        openDownloadWXXC()
        print(" -- 发表结束 -- ")
        return True
    elif elem_type == "video":
        # 找到视频按钮,点击进入阅读模式
        albumJumpReading(elem)

        # 然后直接保存视频
        result = downloadImage(video=True)
        if result is False:
            raise RuntimeError("下载失败！")
        print("保存了视频")
        jumpToBack()
        isAlbumMode()

        # 发表，打开朋友圈
        openUploadWXPYQ()
        result = uploadImages(video=True)
        if result is False:
            raise RuntimeError("上传失败！")

        openDownloadWXXC()
        return True
    elif elem_type == "photoWord":
        # 点击进入阅读模式,在进入详情模式中复制文本
        albumJumpReadingJumpDetails(elem)

        word = copyText(get_text=True)
        print(" -- 复制文字:{}".format(word))
        # 返回到阅读模式中保存图片,再从阅读模式返回相册列表
        jumpToBack()
        isReadingMode()

        result = downloadImage()
        if result is False:
            raise RuntimeError("下载失败！")
        print(" -- 保存了图片和文字")
        jumpToBack()
        isAlbumMode()

        # 打开朋友圈,发表
        openUploadWXPYQ()
        result = uploadImages(paste_text=True, word=word)
        if result is False:
            raise RuntimeError("上传失败！")

        openDownloadWXXC()
        return True
    elif elem_type == "videoWord":
        # 找到视频按钮,点击进入阅读模式,在进入详情模式中复制文本
        albumJumpReadingJumpDetails(elem)

        word = copyText(get_text=True)
        print(" -- 复制文字:{}".format(word))
        # 返回阅读模式
        jumpToBack()
        isReadingMode()

        result = downloadImage(video=True)
        if result is False:
            raise RuntimeError("下载失败！")
        print(" -- 保存了视频和文字")
        # 从阅读模式返回相册列表
        jumpToBack()
        isAlbumMode()

        # 发表，打开朋友圈
        openUploadWXPYQ()
        result = uploadImages(video=True, paste_text=True, word=word)
        if result is False:
            raise RuntimeError("上传失败！")
        openDownloadWXXC()
        return True
    elif elem_type == "photoWordList":
        # 点击进入阅读模式,在进入详情模式中复制文本
        albumJumpReadingJumpDetails(elem)

        word = copyText(get_text=True)
        print(" -- 复制文字:{}".format(word))

        # 获取图片,找到包含九宫格的节点,只有一个.ps:当有四个节点时不会按照九宫格的顺序排列，所以使用点击elem
        file = "xiangqing"
        saveXML(file)
        elem = findElement(file, resourceId='com.tencent.mm:id/e6j')
        photo_num = 0
        # 只需查找elem的子级,每个子级节点都是一个图片
        for child in elem:
            # 点击打开图片,（不会按照顺序排列,所以不能使用id选择）
            clickElem(child)
            isReadingMode()

            # 保存图片
            result = downloadImage()
            if result is False:
                raise RuntimeError("下载失败！")
            photo_num += 1
            print(" -- 保存了{}图片".format(photo_num))
            # 返回详情模式
            d.click(0.5, 0.5)
            isDetailsMode()

        # 从详情模式返回相册列表
        jumpToBack()
        isReadingMode()
        jumpToBack()
        isAlbumMode()

        print(" -- 开始发表....")
        # 发表，打开微信本尊朋友圈
        openUploadWXPYQ()
        result = uploadImages(upload_num=photo_num, paste_text=True, word=word)
        if result is False:
            raise RuntimeError("上传失败！")
        openDownloadWXXC()
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
    assert hie_pre != hie_post, "原地滑动！"
    return True


def calculateTime(start, end):
    """计算时间差，返回字符串"""
    dur_time = end - start
    str_time = "用时："
    if dur_time / 60 > 1:
        str_time += str(int(dur_time / 60)) + "分"
    str_time += str(round(dur_time % 60)) + "秒"
    return str_time


def shoucangOnly(elem, elem_type):
    """只收藏，不改价格"""
    print(" -- 开始收藏....")
    # 纯文字点击会进入详情模式，其他会进入阅读模式，还有一种是广告模式（暂时没考虑）
    if elem_type == "word":
        clickElem(elem)
        isDetailsMode()
        d(resourceId=Element["详情文字"]).long_click(duration=0.6)
        d(text="收藏").click(timeout=3)
        jumpToBack()
        isAlbumMode()
    elif elem_type == "photoList":
        for child in elem.iter():
            # 找到每个图片的按钮,点击进入阅读模式,并保存
            if child.attrib["class"] == "android.view.View" and \
                    (child.attrib["resource-id"] == Element["视频1部件"] or
                     child.attrib["resource-id"] == Element["视频2部件"] or
                     child.attrib["resource-id"] == Element["视频3部件"]):
                # 点击打开图片
                albumJumpReading(elem)
                isReadingMode()
                assert d(className="android.widget.ProgressBar").wait_gone(timeout=600), "下载失败，检查网络是否正常！"
                d(description="更多").click(timeout=3)
                d(text="收藏").click(timeout=3)
                jumpToBack()
                isAlbumMode()
    elif elem_type == "video" or elem_type == "photoWord" or elem_type == "videoWord"or elem_type == "photoWordList":
        albumJumpReading(elem)
        isReadingMode()
        assert d(className="android.widget.ProgressBar").wait_gone(timeout=600), "下载失败，检查网络是否正常！"
        d(description="更多").click(timeout=3)
        d(text="收藏").click(timeout=3)
        jumpToBack()
        isAlbumMode()
    print(" -- 收藏成功....")


def shoucangChangePrice(elem, elem_type):
    """6中类型：empty word photoList video photoWord videoWord photoWordList """
    print(" -- 开始保存....")
    # 判断类型,选择保存
    if elem_type == "word":
        # 点击进入详情
        clickElem(elem)
        isDetailsMode()
        word = copyText(get_text=True)
        if word is False:
            raise RuntimeError("文字复制失败！")
        print(" -- 复制文字:{}".format(word))
        jumpToBack()
        isAlbumMode()
    elif elem_type == "photoList":
        for child in elem.iter():
            # 找到每个图片的按钮,点击进入阅读模式,并保存
            if child.attrib["class"] == "android.view.View" and \
                    (child.attrib["resource-id"] == Element["视频1部件"] or
                     child.attrib["resource-id"] == Element["视频2部件"] or
                     child.attrib["resource-id"] == Element["视频3部件"]):
                # 点击打开图片
                clickElem(child)
                isReadingMode()
                assert d(className="android.widget.ProgressBar").wait_gone(timeout=600), "下载失败，检查网络是否正常！"
                d(description="更多").click(timeout=3)
                d(text="收藏").click(timeout=3)
                jumpToBack()
                isAlbumMode()
    elif elem_type == "video":
        # 找到视频按钮,点击进入阅读模式
        albumJumpReading(elem)
        assert d(className="android.widget.ProgressBar").wait_gone(timeout=600), "下载失败，检查网络是否正常！"
        d(description="更多").click(timeout=3)
        d(text="收藏").click(timeout=3)
        jumpToBack()
        isAlbumMode()
    elif elem_type == "photoWord":
        # 点击进入阅读模式,在进入详情模式中复制文本
        albumJumpReadingJumpDetails(elem)
        word = copyText(get_text=True)
        print(" -- 复制文字:{}".format(word))

        d(text=u"评论").set_text(word, timeout=1)
        result = d(text=u"发送").exists(timeout=1)
        d(text=u"发送").click_exists(timeout=1)

        d(resourceId=Element["详情文字"]).long_click(duration=0.6)
        d(text="收藏").click(timeout=1)

        # 返回到阅读模式中保存图片,再从阅读模式返回相册列表
        jumpToBack()
        isReadingMode()
        jumpToBack()
        isAlbumMode()
    elif elem_type == "videoWord":
        # 找到视频按钮,点击进入阅读模式,在进入详情模式中复制文本
        albumJumpReadingJumpDetails(elem)
        word = copyText(get_text=True)
        print(" -- 复制文字:{}".format(word))

        d(text=u"评论").set_text(word, timeout=1)
        result = d(text=u"发送").exists(timeout=1)
        d(text=u"发送").click_exists(timeout=1)

        d(resourceId=Element["详情文字"]).long_click(duration=0.6)
        d(text="收藏").click(timeout=1)
        # 返回阅读模式
        jumpToBack()
        isReadingMode()
        jumpToBack()
        isAlbumMode()
    elif elem_type == "photoWordList":
        # 点击进入阅读模式,在进入详情模式中复制文本
        albumJumpReadingJumpDetails(elem)

        word = copyText(get_text=True)
        print(" -- 复制文字:{}".format(word))

        d(text=u"评论").set_text(word, timeout=1)
        result = d(text=u"发送").exists(timeout=1)
        d(text=u"发送").click_exists(timeout=1)

        d(resourceId=Element["详情文字"]).long_click(duration=0.6)
        d(text="收藏").click(timeout=1)
        # 从详情模式返回相册列表
        jumpToBack()
        isReadingMode()
        jumpToBack()
        isAlbumMode()
    return result


def test(aaa,bbb):
    print("{}".format(bbb))


def forLoopElms(func_elem):
    """打开好友相册列表，找到要转发的第一条内容，将其拖动到屏幕的下端（保持下面还有半个）,然后启用.
        本参数是一个elem函数名，此函数包含两个参数：一个元素，一个元素的类型
    """
    first_time = time.perf_counter()
    num = 0
    ui = d(text="今天")
    while True:
        if ui.exists() is True:
            if ui.center()[1] > 700:
                break
        # 计时开始
        start_time = time.perf_counter()
        # 获取倒数第二条elem 并检查此条内容的格式
        last_elem = findElemsInPhotoList()[-2]
        elem_type = checkPhotoElemType(last_elem)
        print("检测到的类型:", elem_type)
        # 执行循环函数
        result = func_elem(last_elem, elem_type)
        if result is False:
            # 如果最后一条为空或者没有匹配，则继续滑动屏幕，获取倒数第二个的类型
            print("没有匹配到相册列表的任何类型或者是空的！")
        else:
            num += 1
        # 发表完后向下滑动
        swipeUpElemToEnd(last_elem)
        # 计算时间
        str_time = calculateTime(start_time, time.perf_counter())
        print("-" * 50 + "已转发{}条  {}".format(num, str_time))

    # 获取除去倒数第一条的所有条木
    print("\n=== 马上就要完工了 ===\n")
    elms = findElemsInPhotoList()
    elms = elms[:len(elms) - 1]
    for elem in reversed(elms):
        start_time = time.perf_counter()
        # 检查此条内容的格式：6 种有效格式。如果此条为空或者没有匹配，则滑动屏幕，获取倒数第二个的类型
        elem_type = checkPhotoElemType(elem)
        print("检测到的类型:", elem_type)
        # 执行循环函数
        result = func_elem(elem, elem_type)
        if result is False:
            print("没有匹配到相册列表的任何类型或者是空的！")
        else:
            num += 1
        # 计算时间
        str_time = calculateTime(start_time, time.perf_counter())
        print("-" * 50 + "已转发{}条  {}".format(num, str_time))
    str_time = calculateTime(first_time, time.perf_counter())
    print("--- 总共转发{}条  {} ---".format(num, str_time))


if __name__ == "__main__":
    # openWXFS()
    # openWXBZ()
    # openDownloadWXXC()
    # openUploadWXPYQ()
    # print(copyText(get_text=True))
    # pasteText(set_text=None)
    # downloadImage(video=False)

    # try:
    #     openDownloadWXXC()
    # except RuntimeError as err:
    #     print(err)
    # isReadingMode()
    # isAlbumMode()

    # forLoopElms(test)
    forLoopElms(shoucangOnly)

    # forLoopElmsNoType(shoucang)
    # gengduo = d(description="更多")
    # if gengduo.exists():
    #     print(gengduo)
    # print(d.device_info)
    # items = d(resourceId=Element["照片列表"])
    # cnt = items.count
    # print(cnt)
    # d(resourceId=item)[cnt-2].click()
    # string = d.dump_hierarchy()
    # tree = ET.fromstring(string)
    # treeIter = tree.iter(tag="node")
    # for elem in treeIter:
    #     if elem.attrib["resource-id"] == item:
    #         print(elem.attrib["index"])
    # print(type(tree))

    # ui = d(text="今天")
    # print(ui.exists())
    # print( ui.center()[1] < 700)
    # print(version["7.0.0"]["照片列表"])
