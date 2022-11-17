from time import sleep

import mqtt_client
import Boiler
import asyncio
import aioschedule


async def scheduler():
    aioschedule.every(1).minutes.do(mqtt.publish, mqtt.boiler)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup():
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    boiler = Boiler.Boiler()
    mqtt = mqtt_client.MQTT_Client(boiler)
    asyncio.run(on_startup())
    mqtt.run()
    while True:
        sleep(60)
        mqtt.publish(mqtt.boiler)
    # mqtt.stop()
