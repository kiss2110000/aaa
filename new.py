import uiautomator2 as u2
import xml.etree.ElementTree as ET
import time
import re

from version import *

HEIGHT = 1920

Element = version["7.0.3"]
# for key, value in Element.items():
#     print('{key}:{value}'.format(key=key, value=value))


def saveXML(d, file):
    # 获取xml内容
    string = d.dump_hierarchy()
    # 保存为txt到磁盘
    with open(file + ".txt", "w", encoding='utf-8') as f:
        f.write(string)


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


def findElemsInPhotoList(d):
    """找到相册列表的所有内容,取其最后一条"""
    file = "xiangceliebiao"
    saveXML(d, file)
    elms = findElements(file, resourceId=Element["照片列表"])
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


def swipeUpElemToEnd(d, elem):
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
    print("{}".format(bbb))
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
    albumJumpReading(elem)
    d(resourceId=Element["评论按钮"]).click(timeout=5)
    # 检查是否为详情模式
    isDetailsMode()


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
    elif elem_type == "photoList":
        for child in elem.iter():
            # 找到每个图片的按钮,点击进入阅读模式,并保存
            if child.attrib["class"] == "android.view.View" and \
                    (child.attrib["resource-id"] == Element["视频1部件"] or
                     child.attrib["resource-id"] == Element["视频2部件"] or
                     child.attrib["resource-id"] == Element["视频3部件"]):
                # 点击打开图片
                albumJumpReading(elem)
                isReadingMode(d)
                assert d(className="android.widget.ProgressBar").wait_gone(timeout=600), "下载失败，检查网络是否正常！"
                d(description="更多").click(timeout=3)
                d(text="收藏").click(timeout=3)
                jumpToBack(d)
                isAlbumMode(d)
    elif elem_type == "video" or elem_type == "photoWord" or elem_type == "videoWord"or elem_type == "photoWordList":
        albumJumpReading(d, elem)
        isReadingMode(d)
        assert d(className="android.widget.ProgressBar").wait_gone(timeout=600), "下载失败，检查网络是否正常！"
        d(description="更多").click(timeout=3)
        d(text="收藏").click(timeout=3)
        jumpToBack(d)
        isAlbumMode(d)
    print(" -- 收藏成功....")


def main():
    d = u2.connect_usb('c176b27d')
    d.freeze_rotation()
    forLoopElms(d, shoucangOnly)


if __name__ == '__main__':
    main()
