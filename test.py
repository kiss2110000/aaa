import re
# word = r"❤️❤️ BOX 大小号  二层牛皮 小号： 19*14。201788105739145。大号：24*18。 201788110739150 "
# find = re.findall("\d{15}", word)
# jiage = [i[-3:] for i in find]
#
# for i, u in zip(find, jiage):
#     word = word.replace(i, "💰"+u)
# print()

print(re.findall("💰\d{2,}","💰20000"))




