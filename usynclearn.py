import uasyncio as asyncio
from machine import Pin
import time
led = Pin("LED",Pin.OUT,value=0)
async def blink_led(frequency=0.5,num_blinks=1):
    print("blinke")
    global led
    for i in range(num_blinks):
        led.on()
        await asyncio.sleep(frequency)
        led.off()
        await asyncio.sleep(frequency)
    return 12
async def coroutine_1():
    i=0
    while True:
        i +=1
        print("Coroutine 1 is running")
        blink = asyncio.create_task(blink_led(4))
        print("Done blinking")
        await asyncio.sleep(5)
        return i


async def main_coroutine():
    #asyncio.create_task(blink_led(1,20))
    # We need to keep the main coroutine running indefinitely
    while True:
        task = asyncio.create_task(blink_led(1,2))

        print(await task)
        await asyncio.sleep(1)

try:
    asyncio.run(main_coroutine())
finally:
    asyncio.new_event_loop()
