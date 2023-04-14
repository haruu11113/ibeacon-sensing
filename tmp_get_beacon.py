import asyncio
from bleak import BleakScanner

def print_ble_data(device, advertisement_data):
    if advertisement_data:
        # print(device.address, advertisement_data)

        local_name = advertisement_data.local_name
        service_uuids = advertisement_data.service_uuids
        manufacturer_data = advertisement_data.manufacturer_data
        tx_power_level = advertisement_data.tx_power
        rssi = advertisement_data.rssi

        print("device {} local_name {} service_uuids {} manufacturer_data {} tx_power_level {} rssi {}"
              .format(device.address, local_name, service_uuids, manufacturer_data, tx_power_level, rssi))


async def run():
    scanner = BleakScanner()
    scanner.register_detection_callback(print_ble_data)
    await scanner.start()
    while True:
        await asyncio.sleep(0.1)

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
