import uiautomator2 as u2
import re
# d = u2.connect('192.168.0.100')
d = u2.connect_usb('1208ceba')


# d.shell("am start com.tencent.mm/com.tencent.mm.ui.LauncherUI")
# d(text="选择要使用的应用").wait(timeout=1)
# result = d(description="拍照分享").exists()

# word = d(resourceId="com.tencent.mm:id/jv").get_text(timeout=5)
# # find = re.findall("\d{15}", word)
# # jiage = [i[-3:] for i in find]
# #
# # for i,u in zip(find, jiage):
# #     word.replace(i,u)
# # # print(word)
# result = d(resourceId="com.sohu.inputmethod.sogou.vivo:id/imeview_candidates").exists(timeout=1)
# if result is True:
#     d.click(0.92, 0.626)
print(d.info)
print(d.device_info)