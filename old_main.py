"""
Authors: SA Herdev Anish https://github.com/AnisHerdev
and      Suman BR https://github.com/SumanBR321
Students at RVU
"""
import machine, time
import neopixel
from machine import Pin, I2C
from bh1750 import BH1750
import uasyncio as asyncio
import network   # handles connecting to WiFi
import urequests

#Initializing all the components
led_builtin = Pin("LED", Pin.OUT, value=0)
#Initializing the neopixel RGB 
pin = machine.Pin(2, machine.Pin.OUT) # Define the pin where the LED strip is connected
np = neopixel.NeoPixel(pin, 8) # Create a NeoPixel object, the arguments are pin Number , number of leds
# Initialize the BH1750 object
i2c0 = I2C(0, sda=Pin(16), scl=Pin(17))
bh1750 = BH1750(0x23, i2c0)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
    
html="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Light Control</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #b0cece;
        }
        .container {
            margin-top: 50px;
        }
        button{
            background-color: #4CAF50; /* Green */
            border: none;
            color: rgb(0, 0, 0);
            font-weight: bold;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 8px;
            box-shadow: 0px 2px 2px black;
            
        }
        .button_Normal{
            background-color:rgb(68, 151, 179);
        }
        .button_Circadian{
            background-image: linear-gradient(to right, hsl(240, 100%, 79%), hsl(40, 100%, 80%));
            color:black;
            font-weight: bold;
        }
        .slider {
            /* -webkit-appearance: none; */
            width: 50%;
            height: 20%;
            border-radius: 5px;
            background: #d3d3d3;
            outline: none;
            opacity: 0.7;
            -webkit-transition: .2s;
            transition: opacity .2s;
        }
        .slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 25px;
            height: 25px;
            border-radius: 50%;
            background: #4CAF50;
            cursor: pointer;
        }
        .slider::-moz-range-thumb {
            width: 25px;
            height: 25px;
            border-radius: 50%;
            background: #4CAF50;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <section class="container">
        <h1>Smart Light Control</h1>
        <button class="button_Normal" id="Normal_Button" name="mode" value="normal" type="submit" >Normal</button>
        &nbsp;&nbsp;
        <button class="button_Circadian" id="Circadian_Button" name="mode" value="circadian" type="submit" >Circadian</button>
        <br><br>
        <button class="button_PowerSaver" id="PowerSaver" name="mode" value="power_saver" type="submit" >Power Saver</button>
        <br><br>
        <input type="range" min="0" max="100" value="50" class="slider" id="brightnessSlider">
        <div class="brightness-label">Brightness: <span id="brightnessValue">50</span>%</div>
    </section>

    <script>
        document.addEventListener("DOMContentLoaded", function() {
            const toggleButton = document.getElementById("PowerSaver");
            const brightnessSlider = document.getElementById("brightnessSlider");
            const brightnessValueCurrent = document.getElementById("brightnessValue");

            // Function to send control commands to the smart light
            function controlLight(command, value) {
                console.log("Command:", command, "Value:", value);
            }

            toggleButton.addEventListener("click", function() {
                controlLight("TOGGLE", null);
            });

            brightnessSlider.addEventListener("input", function() {
                const brightnessValue = brightnessSlider.value;
                brightnessValueCurrent.textContent = brightnessValue;
                // document.write(brightnessValue)
                controlLight("BRIGHTNESS", brightnessValue);
            });
        });
    </script>
</body>
</html>
"""
def blink_led(frequency=0.5,num_blinks=1):
    for i in range(num_blinks):
        led_builtin.on()
        time.sleep(frequency)
        led_builtin.off()
        time.sleep(frequency)
        
async def connect_to_wifi(ssid = "Bravo's Galaxy M32", password = "12341233"):
    print("Connecting to Wifi...")
    wlan.config(pm = 0xa11140)  # Diable powersave mode ##
    wlan.connect(ssid, password)
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3: # lesser that 0 indicates error and greater that 3 indicates connected
            break
        max_wait -= 1
        print('Waiting for connection...')
        asyncio.sleep(1)
    if wlan.status()!=3:
        print("Unable to connect to the wifi...")
        blink_led(1,1)
    else:
        blink_led(0.1,3)
        print("Connected to wifi successfully...")
        status = wlan.ifconfig()
        print('IP = ' + status[0])
    
# Coroutine to control the RGB LED intensity based on lux value
async def rgb_led_intensity():
    while True:
        lux = bh1750.read_lux()
        # Map lux value to LED brightness (adjust the scaling factor as needed)
        brightness = 1-(min(lux,500)) / 500 # Limit brightness to a maximum value (0 to 1)+
        # Set NeoPixel colors
        np.fill((int(255 * brightness), int(167 * brightness), int(87 * brightness)))
        np.write()
        print(f"Brightness: {brightness*100:.2f}%, LUX: {lux}")
        
        await asyncio.sleep(1)
        
        
async def serve_client(reader, writer):
    print("Client connected")
    request_line = await reader.readline()
    print("Request:", request_line)
    # We are not interested in HTTP request headers, skip them
    while await reader.readline() != b"\r\n":
        pass
    
    # find() valid garage-door commands within the request
    request = str(request_line)
    cmd_normal = request.find('mode=normal')
    cmd_power = request.find('mode=power_saver')
    cmd_circadian = request.find('mode=circadian')
    blink_led(1,1)
    print("Normal mode:"+str(cmd_normal))
    print("Power saver mode:"+str(cmd_power))
    print("Circadian mode:"+str(cmd_circadian))
    
    if cmd_normal == 8:
        stateis = "Door: STOP"
        print(stateis)
        control_door('stop')
        
    elif cmd_power == 8:
        stateis = "Door: UP"
        print(stateis)
        control_door('up')
        
    elif cmd_circadian == 8:
        stateis = "Door: DOWN"
        print(stateis)
        control_door('down')
    
    response = html #% stateis
    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    writer.write(response)

    await writer.drain()
    await writer.wait_closed()
# Run the event loop with the RGB LED intensity coroutine
async def main():
    asyncio.create_task(connect_to_wifi()) # Connecting to wifi
    #if wlan.status()>=3:
    print('Setting up webserver...')
    asyncio.create_task(asyncio.start_server(serve_client, "0.0.0.0", 80))
    #await rgb_led_intensity()
    while True:
        await asyncio.sleep(0.25)

blink_led()
# Run the event loop
try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
    
    


