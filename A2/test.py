# 开发时间：2022/4/26 1:51
# 作者：Shawn_Bravo
from constants import *
from typing import Optional

wnd = []
sb = {'a': [1, 2], 'b': [3, 4]}
for item in sb:
    print(item + ': ' + str(len(sb[item])))

a = 'asdasdasd\nasdasdasdasd\ndsadasdasdasdasd\nasdobfvndfvno\nasduivibeiv\n'
print(a.strip('\n').split('\n'))
for i in a.strip('\n').split('\n'):
    wnd.append([i])
print(wnd)


a = 'asdasd'
print(list(eval(a)))