def test(aaa, bbb):
    print("{}".format(bbb))
    return True


def forLoopElms(func_elem):
    last_elem = 222
    elem_type = 555
    result = func_elem(last_elem, elem_type)
    print(result)
    if result is False:
        # 如果最后一条为空或者没有匹配，则继续滑动屏幕，获取倒数第二个的类型
        print("没有匹配到相册列表的任何类型或者是空的！")

forLoopElms(test)