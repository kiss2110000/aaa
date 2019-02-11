import datetime
from wxpy import *
import uiautomator2 as u2

d = u2.connect()
d(resourceId="com.tencent.mm:id/aq4").wait(timeout=0.5)
red = d(resourceId="com.tencent.mm:id/aq4")
count = red.count
print("打开红包 {}".format(count))


bot = Bot(cache_path=True)
order_group = bot.groups().search(r'中科水王')[0]


@bot.register(order_group, except_self=False)
def reply_order(msg):
    account = msg.raw['ActualNickName']
    text = msg.text
    print(text)
    if '收到红包，请在手机上查看' == text:
        # print('等待红包出现！')
        # d(resourceId="com.tencent.mm:id/aq4").wait(timeout=0.5)
        print('打开红包！')
        d(resourceId="com.tencent.mm:id/aq4").click()
        print('点击圆圈开字！')
        d(resourceId="com.tencent.mm:id/cyf").click(timeout=0.5)


embed()
