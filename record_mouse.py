import pandas as pd
import matplotlib.pyplot as plt
import random
import datetime
import numpy as np

x1=[random.random() for i in range(1000)]
y1=[random.randint(0, 5000) for i in range(1000)]

def onclick(event):
    global event_xdata_list, event_ydata_list, event_datetime_list
    print("event.button=%d,  event.x=%d, event.y=%d, event.xdata=%f, \
    event.ydata=%f"%(event.button, event.x, event.y, event.xdata, event.ydata))
    event_xdata_list.append(event.xdata)
    event_ydata_list.append(event.ydata)
    event_datetime_list.append(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))

import matplotlib.pyplot as plt
from PIL import Image

# 画像読み込み
image = Image.open("2F.png")
size = 3
resize_size = (int(image.width*size), int(image.height*size))
resized_image = image.resize(resize_size)
width = resized_image.width
height = resized_image.height

# Figureとaxの準備 ... matplotlibの定型的な処理
fig = plt.figure(figsize=(10, 10))
fig.patch.set_facecolor('white') #<--これはなくてもよさそう。図全体の背景色を設定するが、imageで塗られる形になるため。
ax = fig.add_subplot(1, 1, 1)

# 画像だと(0,0)が左上に来て, y軸の正の方向が下を向くのでinvert_yaxis()
# ax.invert_yaxis()と思ったけど、いらないようす。

# xとyはログから入手したタッチ座標。ここでは、暫定的に左上、中央、右下を指定している
x = [1800, 2000, 2200, 2400, 2600]
y = [550, 550, 550, 550, 550]

# タッチ座標をプロットする
ax.scatter(x, y, c='red', s=50)

# 背景に画面イメージ(resized_image)を出す
plt.xticks([i for i in range(0, width, 100)], minor=True)
plt.xticks([i for i in range(0, width, 500)], minor=False)
plt.yticks([i for i in range(0, height, 100)], minor=True)
plt.yticks([i for i in range(0, height, 500)], minor=False)
ax.imshow(resized_image)
plt.grid(which="minor", lw=0.8, ls="--", color="gray", alpha=0.5)
plt.grid(which="major", lw=1, ls="-", color="gray", alpha=1)


event_xdata_list = list()
event_ydata_list = list()
event_datetime_list = list()
fig.canvas.mpl_connect('button_press_event', onclick)

plt.show()
# プロット画像を保存する
# plt.savefig("aaaa_plot.png")

plt.show()
print("positions are ",event_xdata_list)
print("positions are ",event_ydata_list)
data=pd.DataFrame([event_datetime_list, event_xdata_list,event_ydata_list], index=['datetime', 'x', 'y']).T
data.to_csv("event/event_{}.csv".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))
plt.close()