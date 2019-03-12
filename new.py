import uiautomator2 as u2
import xml.etree.ElementTree as ET
import time
import re

from version import *


Element = version["7.0.3"]
# for key, value in Element.items():
#     print('{key}:{value}'.format(key=key, value=value))


def openWXFS(d):
    """启用微信分身"""
    udid = d.device_info["udid"]
    num = 0
    while num < 5:
        try:
            if udid == "c176b27d-18:e2:9f:2e:dd:78-vivo_X23Plus":
                """vivo X23"""
                d.shell("am start com.tencent.mm/com.tencent.mm.ui.LauncherUI")
                d(text="Ⅱ·微信").click(timeout=0.5)
                print(" -- 点击了微信分身")
            elif udid == "c176b27d-18:e2:9f:2e:dd:78-vivo_X7Plus":
                """vivo X7"""
                # Home键返回桌面,点击微信分身
                d.shell("input keyevent 3")
                d(text=u"Ⅱ·微信", resourceId="com.bbk.launcher2:id/item_title").click(timeout=5)
            num = 6
        except:
            num += 1
            time.sleep(1)
            print("警告：正在尝试重新打开微信分身！")


def openWXBZ(d):
    # 启动微信本尊,打开朋友发表页面
    udid = d.device_info["udid"]
    num = 0
    while num < 5:
        try:
            if udid == "c176b27d-18:e2:9f:2e:dd:78-vivo_X23Plus":
                d.shell("am start com.tencent.mm/com.tencent.mm.ui.LauncherUI")
                d(text="微信").click(timeout=0.5)
            elif udid == "c176b27d-18:e2:9f:2e:dd:78-vivo_X7Plus":
                d.shell("am start com.tencent.mm/com.tencent.mm.ui.LauncherUI")
            num = 6
        except:
            num += 1
            time.sleep(1)
            print("警告：正在尝试重新打开微信本尊！")


def openDownloadWXXC(d):
    openWXFS(d)
    isAlbumMode(d)


def openUploadWXPYQ(d):
    openWXBZ(d)
    # 检查是否为发表页面
    result = d(description="拍照分享").exists(timeout=1.5)
    if not result:
        is_gone = d(description="返回",
                    packageName="com.tencent.mm",
                    className="android.widget.ImageView").click_gone(maxretry=20, interval=0.01)
        if is_gone is True:
            d(text="发现").click(timeout=5)
            d(text="朋友圈").click(timeout=5)
            print(" -- 已打开朋友圈页面")
            return True
        print("错误：找不到朋友圈页面！")
        return False
    return True


def findElements(d, resourceId=None, text=None, className=None, description=None):
    node_list = []
    # 将获取的层级文本,转化为xml格式的
    tree = ET.fromstring(d.dump_hierarchy())
    # 循环每个tag=node节点,将找到的匹配节点全部添加到列表中
    nodes = tree.iter(tag="node")
    for elem in nodes:
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


def findElemsInPhotoList(d):
    """找到相册列表的所有内容,取其最后一条"""
    elms = findElements(d, resourceId=Element["照片列表"])
    if len(elms) == 0:
        print("没有找到相册列表的任何数据！")
        return None
    return elms


def findLastSecondPhoto(d):
    pass


def getCenter(d, elem):
    pattern = re.compile(r"\d+")
    size = d.window_size()
    # print(size)
    bounds = elem.attrib["bounds"]
    coord = pattern.findall(bounds)
    Xpoint = ((int(coord[2]) - int(coord[0])) / 2.0 + int(coord[0])) / size[0]
    Ypoint = ((int(coord[3]) - int(coord[1])) / 2.0 + int(coord[1])) / size[1]
    return Xpoint, Ypoint


def clickElem(d, elem):
    click_pre = d.dump_hierarchy()
    num = 0
    while num < 3:
        pos = getCenter(d, elem)
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


def getElemBound(elem):
    bounds = elem.attrib["bounds"]
    pattern = re.compile(r'\d+')
    bounds = list(map(int, pattern.findall(bounds)))
    return bounds


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


def copyText(d, get_text=False):
    """在详情页面，复制发表的文字"""
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


def pasteText(d, word_text=None):
    """在发表页面，粘贴文字"""
    if word_text is None:
        d(text=u"这一刻的想法...").long_click(timeout=1, duration=0.6)
        d(text=u"粘贴").click(timeout=1)
    else:
        d(text=u"这一刻的想法...").set_text(word_text, timeout=1)
        result = d(description=u"表情").exists(timeout=1)
        if result is True:
            d.press("back")


def downloadImage(d, video=False):
    # 在阅读模式或者查看模式下，下载图片或者视频
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


def uploadImages(d, upload_num=1, photo_index=0, video=False, word=None):
    """在朋友圈页面发表状态"""
    if video is False:
        if upload_num > 9:
            upload_num = 9
        if upload_num <= 0:
            return "没有照片发表"
    d(description=u"拍照分享").click(timeout=10)
    d(text=u"从相册选择").click(timeout=10)
    d(text=u"图片和视频").wait(timeout=15)
    time.sleep(0.5)
    # 获取照片池的前9个节点,因为最多传9个图片
    elms = findElements(d, resourceId=Element["照片池"])
    assert elms, "没有找到照片池的任何东西!"

    # 判断是上传图片还是视频
    if video is False:
        elms = elms[0:9]
        if photo_index != 0:
            # 索引切片：从第几个开始(index)
            elms = elms[photo_index:photo_index + 1]
        # 切片获取所需要的几个节点，循环选择
        elms = elms[0:upload_num]
        for elem in reversed(elms):
            # print(elem)
            result = False
            # 检查每个节点中是否存在选择框部件,存在就选择
            for child in elem.iter():
                if child.attrib["class"] == "android.widget.CheckBox":
                    # print(child.attrib['bounds'])
                    pos = getCenter(d, child)
                    d.click(pos[0], pos[1])
                    time.sleep(0.2)
                    # d(resourceId=child.attrib["resource-id"], className=child.attrib["class"],
                    #   instance=elem.attrib["index"]).click(timeout=5)
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

    isPublishEdit(d)
    # 是否粘贴文字
    if word:
        attempts = 0
        success = False
        while attempts < 3 and not success:
            try:
                pasteText(d, word_text=word)
                success = True
            except:
                attempts += 1
                print("警告：正在尝试重新粘贴...")
                assert attempts == 3, "粘贴文字失败，没有显示粘贴键!"

    # 设置私密
    setSecret(d)
    # 点击发布
    d(text=u"发表").click(timeout=10)
    print(" -- 发表了{}张照片".format(upload_num))


def uploadAndDownloadElem(d, elem, elem_type):
    """6中类型：empty word photoList video photoWord videoWord photoWordList """
    print(" -- 开始保存....")
    result = False
    # 判断类型,选择保存
    if elem_type == "word":
        # 点击进入详情
        clickElem(d, elem)
        isDetailsMode(d)

        word = copyText(d, get_text=True)
        if word is False:
            raise RuntimeError("文字复制失败！")
        print(" -- 复制文字:{}".format(word))
        jumpToBack(d)
        isAlbumMode(d)

        # 发表，打开朋友圈
        print(" -- 开始发表...")
        openUploadWXPYQ(d)
        d(description=u"拍照分享").long_click(duration=0.6)
        pasteText(d, word_text=word)
        # 设置秘密
        setSecret(d)
        d(text=u"发表").click(timeout=10)
        openDownloadWXXC(d)
        print(" -- 发表结束")
        return True
    elif elem_type == "photoList":
        photo_num = 0
        for child in elem.iter():
            # 找到每个图片的按钮,点击进入阅读模式,并保存
            if child.attrib["class"] == "android.view.View" and \
                    (child.attrib["resource-id"] == Element["视频1部件"] or
                     child.attrib["resource-id"] == Element["视频2部件"] or
                     child.attrib["resource-id"] == Element["视频3部件"]):
                # 点击打开图片
                clickElem(d, child)
                isReadingMode(d)

                result = downloadImage(d)
                if result is False:
                    raise RuntimeError("下载失败！")
                photo_num += 1
                print(" -- 保存了图片{}".format(photo_num))
                jumpToBack(d)
                isAlbumMode(d)
        # 发表，打开本尊朋友圈
        openUploadWXPYQ(d)
        for i in reversed(range(photo_num)):
            result = uploadImages(d, photo_index=i)
            if result is False:
                raise RuntimeError("上传失败！")
        openDownloadWXXC(d)
        print(" -- 发表结束 -- ")
        return True
    elif elem_type == "video":
        # 找到视频按钮,点击进入阅读模式
        albumJumpReading(d, elem)

        # 然后直接保存视频
        result = downloadImage(d, video=True)
        if result is False:
            raise RuntimeError("下载失败！")
        print("保存了视频")
        jumpToBack(d)
        isAlbumMode(d)

        # 发表，打开朋友圈
        openUploadWXPYQ(d)
        result = uploadImages(d, video=True)
        if result is False:
            raise RuntimeError("上传失败！")

        openDownloadWXXC(d)
        return True
    elif elem_type == "photoWord":
        # 点击进入阅读模式,在进入详情模式中复制文本
        albumJumpReadingJumpDetails(d, elem)

        word = copyText(d, get_text=True)
        print(" -- 复制文字:{}".format(word))
        # 返回到阅读模式中保存图片,再从阅读模式返回相册列表
        jumpToBack(d)
        isReadingMode(d)

        result = downloadImage(d)
        if result is False:
            raise RuntimeError("下载失败！")
        print(" -- 保存了图片和文字")
        jumpToBack(d)
        isAlbumMode(d)

        # 打开朋友圈,发表
        openUploadWXPYQ(d)
        result = uploadImages(d, word=word)
        if result is False:
            raise RuntimeError("上传失败！")

        openDownloadWXXC(d)
        return True
    elif elem_type == "videoWord":
        # 找到视频按钮,点击进入阅读模式,在进入详情模式中复制文本
        albumJumpReadingJumpDetails(d, elem)

        word = copyText(d, get_text=True)
        print(" -- 复制文字:{}".format(word))
        # 返回阅读模式
        jumpToBack(d)
        isReadingMode(d)

        result = downloadImage(d, video=True)
        if result is False:
            raise RuntimeError("下载失败！")
        print(" -- 保存了视频和文字")
        # 从阅读模式返回相册列表
        jumpToBack(d)
        isAlbumMode(d)

        # 发表，打开朋友圈
        openUploadWXPYQ(d)
        result = uploadImages(d, video=True, word=word)
        if result is False:
            raise RuntimeError("上传失败！")
        openDownloadWXXC(d)
        return True
    elif elem_type == "photoWordList":
        # 点击进入阅读模式,在进入详情模式中复制文本
        albumJumpReadingJumpDetails(d, elem)

        word = copyText(d, get_text=True)
        print(" -- 复制文字:{}".format(word))

        # 获取图片,找到包含九宫格的节点,只有一个.ps:当有四个节点时不会按照九宫格的顺序排列，所以使用点击elem
        elem = None
        string = d.dump_hierarchy()
        tree = ET.fromstring(string)
        treeIter = tree.iter(tag="node")
        for each in treeIter:
            if each.attrib["resource-id"] == Element["九宫格"]:
                elem = each
                break

        photo_num = 0
        # 只需查找elem的子级,每个子级节点都是一个图片
        for child in elem:
            # 点击打开图片,（不会按照顺序排列,所以不能使用id选择）
            clickElem(d, child)
            isReadingMode(d)
            # 保存图片
            result = downloadImage(d)
            if result is False:
                raise RuntimeError("下载失败！")
            photo_num += 1
            print(" -- 保存了{}图片".format(photo_num))
            # 返回详情模式
            d.click(0.5, 0.5)
            isDetailsMode(d)

        # 从详情模式返回相册列表
        jumpToBack(d)
        isReadingMode(d)
        jumpToBack(d)
        isAlbumMode(d)

        print(" -- 开始发表....")
        # 发表，打开微信本尊朋友圈
        openUploadWXPYQ(d)
        result = uploadImages(d, upload_num=photo_num, word=word)
        if result is False:
            raise RuntimeError("上传失败！")
        openDownloadWXXC(d)
        return True
    return result


def swipeUpElemToEnd(d, elem):
    """拖动换下一行"""
    botton = bottons[d.device_info["udid"]]
    time.sleep(0.2)
    hie_pre = d.dump_hierarchy()
    bounds = getElemBound(elem)
    d.swipe(540, bounds[1] + (bounds[3] - bounds[1]) / 2, 540, botton)
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


def forLoopElms(d, func_elem):
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
        last_elem = findElemsInPhotoList(d)[-2]
        elem_type = checkPhotoElemType(last_elem)
        print("检测到的类型:", elem_type)
        # 执行循环函数
        result = func_elem(d, last_elem, elem_type)
        if result is False:
            # 如果最后一条为空或者没有匹配，则继续滑动屏幕，获取倒数第二个的类型
            print("没有匹配到相册列表的任何类型或者是空的！")
        else:
            num += 1
        # 发表完后向下滑动
        swipeUpElemToEnd(d, last_elem)
        # 计算时间
        str_time = calculateTime(start_time, time.perf_counter())
        print("-" * 50 + "已完成{}条  {}".format(num, str_time))

    # 获取除去倒数第一条的所有条木
    print("\n=== 马上就要完工了 ===\n")
    elms = findElemsInPhotoList(d)
    elms = elms[:len(elms) - 1]
    for elem in reversed(elms):
        start_time = time.perf_counter()
        # 检查此条内容的格式：6 种有效格式。如果此条为空或者没有匹配，则滑动屏幕，获取倒数第二个的类型
        elem_type = checkPhotoElemType(elem)
        print("检测到的类型:", elem_type)
        # 执行循环函数
        result = func_elem(d, elem, elem_type)
        if result is False:
            print("没有匹配到相册列表的任何类型或者是空的！")
        else:
            num += 1
        # 计算时间
        str_time = calculateTime(start_time, time.perf_counter())
        print("-" * 50 + "已完成{}条  {}".format(num, str_time))
    str_time = calculateTime(first_time, time.perf_counter())
    print("--- 总共完成{}条  {} ---".format(num, str_time))
    return True


def test(d, aaa, bbb):
    print("{}".format(bbb, aaa, d))
    return True


def albumJumpReading(d, elem):
    # 找到视频按钮,点击进入阅读模式
    for child in elem.iter():
        if child.attrib["resource-id"] == Element["视频1部件"]:
            # 点击打开视频
            clickElem(d, child)
            # 检查是否为阅读模式
            isReadingMode(d)


def albumJumpReadingJumpDetails(d, elem):
    albumJumpReading(d, elem)
    d(resourceId=Element["评论按钮"]).click(timeout=5)
    # 检查是否为详情模式
    isDetailsMode(d)


def jumpToBack(d):
    d(description=u"返回", packageName="com.tencent.mm").click(timeout=10)


def setSecret(d):
    # 设置私密
    d(text=u"公开").click(timeout=10)
    d(text=u"私密").click(timeout=10)
    d(text=u"完成").click(timeout=10)


def isAlbumMode(d):
    """检测是否为相册列表"""
    assert d(resourceId=Element["照片列表"]).wait(timeout=5), "此页不是相册模式"


def isReadingMode(d):
    """检测是否为阅读模式"""
    assert d(resourceId=Element["阅读模式"], className="android.widget.Gallery",
             packageName="com.tencent.mm").wait(timeout=5), "此页不是阅读模式"


def isDetailsMode(d):
    """检测是否为详情模式"""
    assert d(resourceId="android:id/text1", text="详情",
             packageName="com.tencent.mm").wait(timeout=20), "此页不是详情模式"


def isFriendsPage(d):
    """检测是否为朋友圈发表页面"""
    assert d(resourceId=Element["拍照分享"], description="拍照分享",
             className="android.widget.ImageButton",
             packageName="com.tencent.mm").wait(timeout=5), "此页不是朋友圈发表页"


def isPublishEdit(d):
    """检测是否为发表编辑页面"""
    assert d(text=u"这一刻的想法...").wait(timeout=10), "此页不是发表编辑页面"


def changePriceFromText(d):
    text_word = d(resourceId=Element["详情文字"]).get_text(timeout=5)
    # text_word = d
    print(" -- 复制文字:{}".format(text_word))
    # 匹配 "💰125"、"P125" 这种 标志+价格 的方式

    def _replace(matched):
        value = int(matched.group('price'))
        return matched.group('flag') + str(value+30)
    text_word = re.sub("(?P<flag>💰)(?P<price>\d{1,3})", _replace, text_word)
    text_word = re.sub("(?P<flag>P)(?P<price>\d{1,3})", _replace, text_word)

    # 匹配 "2201788105739145" 这种 取一串数字的后三位数作为价格 的方式
    def _replace(matched):
        value = matched.group('price')[-3:]
        value = value[1:] if value[0] == "0" else value
        return "💰" + str(value)
    text_word = re.sub("(?P<price>\d{10,18})", _replace, text_word)
    print(" -- 替换文字:{}".format(text_word))
    return text_word


def shoucangOnly(d, elem, elem_type):
    """只收藏，不改价格"""
    print(" -- 开始收藏....")
    # 纯文字点击会进入详情模式，其他会进入阅读模式，还有一种是广告模式（暂时没考虑）
    if elem_type == "word":
        clickElem(d, elem)
        isDetailsMode(d)
        d(resourceId=Element["详情文字"]).long_click(duration=0.6)
        d(text="收藏").click(timeout=3)
        jumpToBack(d)
        isAlbumMode(d)
        print(" -- 收藏成功....")
        return True
    elif elem_type == "photoList":
        for child in elem.iter():
            # 找到每个图片的按钮,点击进入阅读模式,并保存
            if child.attrib["class"] == "android.view.View" and \
                    (child.attrib["resource-id"] == Element["视频1部件"] or
                     child.attrib["resource-id"] == Element["视频2部件"] or
                     child.attrib["resource-id"] == Element["视频3部件"]):
                # 点击打开图片
                albumJumpReading(d, elem)
                isReadingMode(d)
                assert d(className="android.widget.ProgressBar").wait_gone(timeout=600), "下载失败，检查网络是否正常！"
                d(description="更多").click(timeout=3)
                d(text="收藏").click(timeout=3)
                jumpToBack(d)
                isAlbumMode(d)
        print(" -- 收藏成功....")
        return True
    elif elem_type == "video" or elem_type == "photoWord" or elem_type == "videoWord"or elem_type == "photoWordList":
        albumJumpReading(d, elem)
        isReadingMode(d)
        assert d(className="android.widget.ProgressBar").wait_gone(timeout=600), "下载失败，检查网络是否正常！"
        d(description="更多").click(timeout=3)
        d(text="收藏").click(timeout=3)
        jumpToBack(d)
        isAlbumMode(d)
        print(" -- 收藏成功....")
        return True
    return False


def shoucangNoChange(d, elem, elem_type):
    """6中类型：empty word photoList video photoWord videoWord photoWordList """
    print(" -- 开始收藏....")
    # 判断类型,选择保存
    if elem_type == "word":
        # 点击进入详情
        clickElem(d, elem)
        isDetailsMode(d)
        word = d(resourceId=Element["详情文字"]).get_text(timeout=5)

        d(text=u"评论").set_text(word, timeout=1)
        d(text=u"发送").exists(timeout=1)
        d(text=u"发送").click_exists(timeout=1)

        d(resourceId=Element["详情文字"]).long_click(duration=0.6)
        d(text="收藏").click(timeout=1)

        jumpToBack(d)
        isAlbumMode(d)
        print(" -- 收藏成功....")
        return False
    elif elem_type == "photoList":
        for child in elem.iter():
            # 找到每个图片的按钮,点击进入阅读模式,并保存
            if child.attrib["class"] == "android.view.View" and \
                    (child.attrib["resource-id"] == Element["视频1部件"] or
                     child.attrib["resource-id"] == Element["视频2部件"] or
                     child.attrib["resource-id"] == Element["视频3部件"]):
                # 点击打开图片
                clickElem(d, child)
                isReadingMode(d)
                assert d(className="android.widget.ProgressBar").wait_gone(timeout=600), "下载失败，检查网络是否正常！"
                d(description="更多").click(timeout=3)
                d(text="收藏").click(timeout=3)
                jumpToBack(d)
                isAlbumMode(d)
        print(" -- 收藏成功....")
        return True
    elif elem_type == "video":
        # 找到视频按钮,点击进入阅读模式
        albumJumpReading(d, elem)
        assert d(className="android.widget.ProgressBar").wait_gone(timeout=600), "下载失败，检查网络是否正常！"
        d(description="更多").click(timeout=3)
        d(text="收藏").click(timeout=3)
        jumpToBack(d)
        isAlbumMode(d)
        print(" -- 收藏成功....")
        return True
    elif elem_type == "photoWord" or elem_type == "videoWord" or elem_type == "photoWordList":
        # 点击进入阅读模式,在进入详情模式中复制文本
        albumJumpReadingJumpDetails(d, elem)
        word = d(resourceId=Element["详情文字"]).get_text(timeout=5)

        d(text=u"评论").set_text(word, timeout=1)
        d(text=u"发送").exists(timeout=1)
        d(text=u"发送").click_exists(timeout=1)

        d(resourceId=Element["详情文字"]).long_click(duration=0.6)
        d(text="收藏").click(timeout=1)

        # 返回到阅读模式中保存图片,再从阅读模式返回相册列表
        jumpToBack(d)
        isReadingMode(d)
        jumpToBack(d)
        isAlbumMode(d)
        print(" -- 收藏成功....")
        return True
    return False


def shoucangChangePrice(d, elem, elem_type):
    """6中类型：empty word photoList video photoWord videoWord photoWordList """
    print(" -- 开始收藏....")
    # 判断类型,选择保存
    if elem_type == "word":
        # 点击进入详情
        clickElem(d, elem)
        isDetailsMode(d)
        word = changePriceFromText(d)

        d(text=u"评论").set_text(word, timeout=1)
        d(text=u"发送").exists(timeout=1)
        d(text=u"发送").click_exists(timeout=1)

        d(resourceId=Element["详情文字"]).long_click(duration=0.6)
        d(text="收藏").click(timeout=1)

        jumpToBack(d)
        isAlbumMode(d)
        print(" -- 收藏成功....")
        return False
    elif elem_type == "photoList":
        for child in elem.iter():
            # 找到每个图片的按钮,点击进入阅读模式,并保存
            if child.attrib["class"] == "android.view.View" and \
                    (child.attrib["resource-id"] == Element["视频1部件"] or
                     child.attrib["resource-id"] == Element["视频2部件"] or
                     child.attrib["resource-id"] == Element["视频3部件"]):
                # 点击打开图片
                clickElem(d, child)
                isReadingMode(d)
                assert d(className="android.widget.ProgressBar").wait_gone(timeout=600), "下载失败，检查网络是否正常！"
                d(description="更多").click(timeout=3)
                d(text="收藏").click(timeout=3)
                jumpToBack(d)
                isAlbumMode(d)
        print(" -- 收藏成功....")
        return True
    elif elem_type == "video":
        # 找到视频按钮,点击进入阅读模式
        albumJumpReading(d, elem)
        assert d(className="android.widget.ProgressBar").wait_gone(timeout=600), "下载失败，检查网络是否正常！"
        d(description="更多").click(timeout=3)
        d(text="收藏").click(timeout=3)
        jumpToBack(d)
        isAlbumMode(d)
        print(" -- 收藏成功....")
        return True
    elif elem_type == "photoWord" or elem_type == "videoWord" or elem_type == "photoWordList":
        # 点击进入阅读模式,在进入详情模式中复制文本
        albumJumpReadingJumpDetails(d, elem)
        word = changePriceFromText(d)

        d(text=u"评论").set_text(word, timeout=1)
        d(text=u"发送").exists(timeout=1)
        d(text=u"发送").click_exists(timeout=1)

        d(resourceId=Element["详情文字"]).long_click(duration=0.6)
        d(text="收藏").click(timeout=1)

        # 返回到阅读模式中保存图片,再从阅读模式返回相册列表
        jumpToBack(d)
        isReadingMode(d)
        jumpToBack(d)
        isAlbumMode(d)
        print(" -- 收藏成功....")
        return True
    return False


def main():
    d = u2.connect()
    # d = u2.connect_usb('c176b27d')
    d.freeze_rotation()
    # forLoopElms(d, shoucangOnly)
    # openWXFS(d)
    # openWXBZ(d)
    # openDownloadWXXC(d)
    # openUploadWXPYQ(d)
    # uploadImages(d, upload_num=9, word='8888')
    # print(len(elms))

    # forLoopElms(d, uploadAndDownloadElem)
    # forLoopElms(d, shoucangOnly)
    # forLoopElms(d, shoucangNoChange)
    forLoopElms(d, shoucangChangePrice)


if __name__ == '__main__':
    main()
