import sys
import time
import asyncio
import datetime
import signal
from bleak import BleakScanner
import pandas as pd
import matplotlib.pyplot as plt

# DataFrameを用意する
df = pd.DataFrame(columns=["Time", "UUID", "RSSI", 'local_name', 'service_uuids', 'manufacturer_data', 'tx_power_level', 'mac_address'])

# グラフを用意する
# fig, ax = plt.subplots()
fig1 = plt.figure(figsize=(10, 8))
fig1.subplots_adjust(bottom=0.6)
ax1 = fig1.add_subplot(121)

fig1.subplots_adjust(bottom=0.6)
ax2 = fig1.add_subplot(122)

## mac adress in facility1
rssi_list = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16', '17','18','19','20', '21','22', '23']
mac_list = ['F7:7F:78:76:7E:F3',
            'C6:CD:5E:3D:2F:BB',
            'D6:F4:3A:79:74:63',
            'C9:17:55:E2:3E:0E',
            'CA:60:AB:EE:EC:7F',
            'D6:51:7F:AB:0E:29',
            'CC:54:33:F6:A7:90',
            'EB:20:56:87:04:5A',
            'EE:E7:46:DC:19:6F',
            'C8:5B:BF:37:07:A0',
            'D7:26:F6:A3:44:D2',
            'DD:83:B0:27:FD:36',
            'E5:CD:4A:36:87:06',
            'DC:22:B8:17:4E:B5',
            'EA:09:20:80:D6:44',
            'E6:99:D1:EC:C6:81',
            'F6:DA:97:C7:D5:28',
            'EA:66:A1:12:2C:F4',
            'C9:EA:57:8B:0F:80',
            'D6:7C:1D:2C:2A:0A',
            'DA:E1:70:5F:44:97',
            'DD:10:10:F6:4F:27',
            'E6:F3:93:A8:9E:22']

mac2id = {m:r for r, m in zip(rssi_list, mac_list)}


# 同じUUIDごとに直近10個のRSSIを保持するための辞書を用意する
last_10_rssis = {}

async def scan():
    scanner = BleakScanner()
    scanner.register_detection_callback(scanBleData)
    await scanner.start()
    while True:
        await asyncio.sleep(0.1)

def scanBleData(device, advertisement_data):
    if advertisement_data:
        global df, last_10_rssis

        uuid = device.address
        rssi = advertisement_data.rssi
        local_name = advertisement_data.local_name
        service_uuids = advertisement_data.service_uuids
        manufacturer_data = advertisement_data.manufacturer_data
        tx_power_level = advertisement_data.tx_power

        # format Mac Address
        mac_address = uuid.replace("-", "").lower()
        mac_address = ":".join([mac_address[i:i+2] for i in range(0, len(mac_address), 2)])

        if mac_address in last_10_rssis:
            last_10_rssis[mac_address].append(rssi)
            if len(last_10_rssis[mac_address]) > 10:
                last_10_rssis[mac_address].pop(0)
        else:
            last_10_rssis[mac_address] = [rssi]

        tmp_df = pd.DataFrame([[datetime.datetime.now(), uuid, rssi, local_name, service_uuids, manufacturer_data, tx_power_level, mac_address]]
                    ,columns=["Time", "UUID", "RSSI", 'local_name', 'service_uuids', 'manufacturer_data', 'tx_power_level', 'mac_address'])
        df = pd.concat([df, tmp_df], axis=0)


async def updateGraph():
    global df, last_10_rssis
    while True:
        meanGraph()
        countGraph()
        await asyncio.sleep(0.2)

def meanGraph():
    global last_10_rssis

    # 直近10個のRSSIの平均を計算する
    means = []
    for mac, rssis in last_10_rssis.items():
        means.append((mac, sum(rssis)/len(rssis)))

    ax1.clear()
    ax1.bar([m[0] for m in means], [m[1] for m in means])
    ax1.set_title("Average value of RSSI for the past 10 packets", fontsize=12)
    ax1.set_ylabel("Meane RSSI", fontsize=14)
    ax1.set_xlabel("Mac Adress", fontsize=12)
    ax1.set_ylim(-100, 0)
    ax1.invert_yaxis()
    ax1.tick_params(axis="x", labelrotation=90)
    plt.pause(0.2)


def countGraph():
    global df

    # 直近10秒間の受信パケット数をカウントを計算する
    counts = []
    seconds=10
    start = datetime.datetime.now() - datetime.timedelta(seconds=seconds)
    recent_df = df[df["Time"] >= start]
    recent_data = dict(recent_df.groupby("mac_address").count()["Time"])
    for uuid, conut in recent_data.items():
        counts.append((uuid, conut))

    # グラフを更新する
    ax2.clear()
    ax2.bar([m[0] for m in counts], [m[1] for m in counts])
    ax2.set_title("Count of packet for the past {} seconds".format(seconds), fontsize=12)
    ax2.set_ylabel("Count", fontsize=14)
    ax2.set_xlabel("Mac Adress", fontsize=12)
    ax2.set_ylim(0, 20)
    ax2.tick_params(axis="x", labelrotation=90)
    plt.pause(1)

def saveCSV():
    global df
    df.to_csv("./beacons/beacon_{}.csv".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))

async def asyncTask():
    task1 = asyncio.create_task(scan())
    task2 = asyncio.create_task(updateGraph())
    await asyncio.gather(task1, task2)

def cleanup():
    print("===== cleanup plot_beacon.py =====")
    saveCSV()
    print("===== finish plot_beacon.py =====")
    plt.close()

def sigHandler(signum, frame) -> None:
    sys.exit(1)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, sigHandler)
    try:
        # sys.exit(asyncio.run(asyncTask()))
        asyncio.run(asyncTask())
    finally:
        # signal.signal(signal.SIGTERM, signal.SIG_IGN)
        # signal.signal(signal.SIGINT, signal.SIG_IGN)
        cleanup()
        # signal.signal(signal.SIGTERM, signal.SIG_DFL)
        # signal.signal(signal.SIGINT, signal.SIG_DFL)
