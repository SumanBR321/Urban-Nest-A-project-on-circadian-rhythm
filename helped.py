import network
import socket
import time
from machine import Pin, I2C
import neopixel
from bh1750 import BH1750
from ds1307 import DS1307
import uasyncio as asyncio

ssid, password = ("Bravo's Galaxy M32", "12341233")

# Initialize components
led_builtin = Pin("LED", Pin.OUT, value=0)
pin = Pin(2, Pin.OUT)  # NeoPixel pin
np = neopixel.NeoPixel(pin, 8)  # NeoPixel object

# Initialize BH1750 ambient light sensor
i2c_bh1750 = I2C(0, sda=Pin(16), scl=Pin(17))
bh1750 = BH1750(0x23, i2c_bh1750)

# Initialize DS1307 RTC
i2c_ds1307 = I2C(0, scl=Pin(13), sda=Pin(12), freq=400000)
clock = DS1307(i2c_ds1307)

# Enable RTC
clock.halt(False)

async def blink_led(frequency=0.5, num_blinks=1):
    global led_builtin
    for i in range(num_blinks):
        led_builtin.on()
        await asyncio.sleep(frequency)
        led_builtin.off()

def Website():
    website = """
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
        button:active{
            color:white;
            background-color: black;
        }
        .button_Circadian:active{
            color:white;
            background:black;
        }
        .slider {
            /* -webkit-appearance: none;
            appearance: none; */
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
            /* -webkit-appearance: none;
            appearance: none; */
            width: 25px;
            height: 25px;
            border-radius: 50%;
            color: #fc9300;
            background: #fc9300;
            cursor: pointer;
        }
        .slider::-moz-range-thumb {
            width: 25px;
            height: 25px;
            border-radius: 50%;
            color: #fc9300;
            background: #fc9300; 
            cursor: pointer;
        }
        /* .slider::-moz-range-track {
           background: #fc9300; 
        }
        .slider::-webkit-slider-runnable-track {
            background: #fc9300; 
        } */
    </style>
</head>
<body>
    <section class="container">
        <h1>Smart Light Control</h1>
        <button class="button_Normal" id="Normal_Button" value="normal" name="mode" onclick='control("normal")'>Normal</button>
        &nbsp;&nbsp;
        <button class="button_Circadian" id="Circadian_Button" value="circadian" name="mode" onclick='control("circadian")'>Circadian</button>
        <br><br>
        <button class="button_PowerSaver" id="PowerSaver" value="power_saver" name="mode" onclick='control("power_saver")'>Power Saver</button>
        <br><br>
        <input type="range" min="000" max="100" value="50" class="slider" id="brightnessSlider">
        <div class="brightness-label">Brightness: <span id="brightnessValue">50</span>%</div>
    </section>

    <script>
        function control(mode){
            var xhttp = new XMLHttpRequest();
            xhttp.open('GET', '/mode/'+ mode, true);
            xhttp.send();
        }

        function brightness(brightness){
            var xhttp = new XMLHttpRequest();
            xhttp.open('GET', '/brightness/'+ brightness, true);
            xhttp.send();
        }

        function Update(){
            location.reload(true);
        }

        
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
                let brightnessValue = String(this.value).padStart(3,'0');//brightnessSlider.value;
                const brightnessValueSpan = this.value;
                brightnessValueCurrent.textContent = brightnessValueSpan;
                brightness(brightnessValue);
                controlLight("BRIGHTNESS", brightnessValue);
            });
        });
    </script>
</body>
</html>
    """
    return website

def circadian_mode():
    global brightness
    np.fill((int(0 * brightness), int(167 * brightness), int(0 * brightness)))
    np.write()
    print(clock.datetime())
    print("Circadian mode initiated")

def normal_mode():
    global brightness
    np.fill((int(255 * brightness), int(255 * brightness), int(255 * brightness)))
    np.write()
    print("Normal mode initiated")

async def power_saver_mode():
    global brightness
    while True:
        lux = bh1750.read_lux()
        # Adjust brightness based on lux value
        brightness = 1 - min(lux, 1000) / 1000
        # Update NeoPixel colors
        np.fill((int(255 * brightness), int(255 * brightness), int(255  * brightness)))
        np.write()
        print(f"Brightness: {brightness*100:.2f}%")
        await asyncio.sleep(1)
    print("Power saver mode initiated")

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wait for connection
max_wait = 10
print('Waiting for connection')
while max_wait > 0:
    if wlan.isconnected():
        print('Connection successful!')
        print('IP address:', wlan.ifconfig()[0])
        break
    print(f"Waiting... {max_wait} seconds remaining")
    max_wait -= 1
    time.sleep(1)

# Initialize socket for web server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

brightness = 1
mode = "circadian"  # Default mode

async def hosting():
    global brightness, mode
    while True:
        try:
            cl, addr = s.accept()
            print('Connection from', addr, 'accepted!')
            request = cl.recv(1024)
            request = str(request)
            print("*"*10)
            print(request)
            print("*"*10)
            if request.find('/mode/normal') == 6:
                normal_mode()
                mode = "normal"
                print("Normal mode activated")
            elif request.find('/mode/circadian') == 6:
                circadian_mode()
                mode = "circadian"
                print("Circadian mode activated")
            elif request.find('/mode/power_saver') == 6:
                await power_saver_mode()
                mode = "power_saver"
                print("Power saver mode activated")
            elif request.find('/brightness/') == 6:
                brightness = int(request[18:21]) / 100
                if mode == "circadian":
                    circadian_mode()
                elif mode == "power_saver":
                    await power_saver_mode()
                elif mode == "normal":
                    normal_mode()
                print(f"Brightness changed to {brightness*100}%")
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(Website())
            cl.close()
        except OSError as e:
            cl.close()
            print('Connection closed')
        finally:
            await asyncio.create_task(blink_led(0.1))

async def main():
    print("In main")
    hosting_task = asyncio.create_task(hosting())
    while True:
        await asyncio.sleep(1)

# Run the event loop
try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
