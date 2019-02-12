import re


def changePriceFromText(d):
    def _replace(matched):
        value = int(matched.group('value'))
        return matched.group('flag') + str(value+30)

    text_word = d
    # 匹配 "💰125" 这种 钱袋+价格 的方式
    text_word = re.sub("(?P<flag>💰)(?P<value>\d{1,3})", _replace, text_word)
    return text_word


print(changePriceFromText('💰145 💰120 💰1959'))
