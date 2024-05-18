"""
Authors: SA Herdev Anish https://github.com/AnisHerdev
and      Suman BR https://github.com/SumanBR321
Students at RVU
"""
import network
import socket
import time
from time import sleep
from machine import Pin,I2C
import neopixel
from bh1750 import BH1750
from ds1307 import DS1307
import uasyncio as asyncio

ssid, password = ("Bravo's Galaxy M32","12341233")
#Initializing all the components
led_builtin = Pin("LED", Pin.OUT, value=0)
#Initializing the neopixel RGB 
pin = machine.Pin(2, machine.Pin.OUT) # Define the pin where the LED strip is connected
np = neopixel.NeoPixel(pin, 8) # Create a NeoPixel object, the arguments are pin Number , number of leds

# Initialize the BH1750 object with error handling
try:
    i2c0_bh1750 = I2C(0, sda=Pin(16), scl=Pin(17))
    bh1750 = BH1750(0x23, i2c0_bh1750)
except OSError as e:
    print("Error initializing BH1750 sensor:", e)
    
## Initiate I2C
#i2c_DS1307 = I2C(0, scl=Pin(13), sda=Pin(12), freq=400000)  # Initialize I2C bus
#clockObject = DS1307(i2c_DS1307)  # Create DS1307 object

#try:
 #   result = i2c_DS1307.scan()
  #  print("I2C scan result:", result)
   # if result:
    #    print("I2C connection successful")
    #else:
     #   print("No I2C devices found")
#except OSError as e:
 #   print("Error scanning I2C bus:", e)

# Enable the RTC module
#try:
 #   clockObject.halt(False)  # Enable the RTC module
  #  print("RTC module enabled")
#except OSError as e:
 #   print("Error enabling RTC module:", e)
        
async def blink_led(frequency=0.5, num_blinks=1):
    global led_builtin
    for _ in range(num_blinks):
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
        @import url(https://fonts.googleapis.com/css?family=Dosis:700);
        body {
            font-family: "Dosis", Helvetica, Arial, sans-serif; 
            background: #ecf0f1;
            color: #34495e;
            padding-top: 40px;
            text-shadow: white 1px 1px 1px;
            text-align: center;
            font-size: 30px;
        }
        .container h1{
            margin-top: 0px;
        }
        button{
            background-color: #4CAF50; /* Green */
            border: none;
            color: rgb(0, 0, 0);
            font-family: "Dosis", Helvetica, Arial, sans-serif; 
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
        .brightness-level {
        border-bottom: 4px dashed #bdc3c7;
        text-align: center;
        font-weight: bold;
        font-size: 0px;
        width: 300px; 
        height: 100px;
        line-height: 60px;
        margin: 40px auto;
        letter-spacing: -.07em;
        text-shadow: white 2px 2px 2px;
        }
        input[type="range"] {
        display: block;
        -webkit-appearance: none;
        appearance: none;
        background-color: #bdc3c7;
        width: 300px;
        height: 5px;
        border-radius: 5px;
        margin: 0 auto;
        outline: 0;
        }
        input[type="range"]::-webkit-slider-thumb {
        -webkit-appearance: none;
        background-color: #e74c3c;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        border: 2px solid white;
        cursor: pointer;
        transition: .3s ease-in-out;
        }​
        input[type="range"]::-webkit-slider-thumb:hover {
            background-color: white;
            border: 2px solid #e74c3c;
        }
        input[type="range"]::-webkit-slider-thumb:active {
            transform: scale(1.6);
        }
    </style>
</head>
<body>
    <section class="container">
        <h1>Smart Light Control</h1>
        <div class="current_mode" style="font-size: 20px;">Mode: <span id="current_mode_value"></span></div><br>
        <button class="button_Normal" id="Normal_Button" value="normal" name="mode" onclick='control("normal")'>Normal</button>
        &nbsp;&nbsp;
        <button class="button_Circadian" id="Circadian_Button" value="circadian" name="mode" onclick='control("circadian")'>Circadian</button>
        <br><br>
        <button class="button_PowerSaver" id="PowerSaver" value="power_saver" name="mode" onclick='control("power_saver")'>Power Saver</button>
        <br><br>
        <div class="brightness-label">Brightness: <span id="brightnessValue">100
        
        </span>%</div><br>
        <input type="range" min="000" max="100" value="100" class="slider" id="brightnessSlider">
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
            const toggleButton1 = document.getElementById("Normal_Button");
            const toggleButton2 = document.getElementById("Circadian_Button");
            const toggleButton3 = document.getElementById("PowerSaver");
            const brightnessSlider = document.getElementById("brightnessSlider");
            const brightnessValueCurrent = document.getElementById("brightnessValue");
            const currentMode = document.getElementById("current_mode_value");
            toggleButton1.addEventListener("click", function() {
               currentMode.textContent = "Normal"
            });
            toggleButton2.addEventListener("click", function() {
               currentMode.textContent = "Circadian"
            });
            toggleButton3.addEventListener("click", function() {
               currentMode.textContent = "Power Saver"
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

def normal_mode():
    global brightness
    np.fill((int(255 * brightness), int(255 * brightness), int(255 * brightness)))
    np.write()
    print("normal mode initiated")
    
def circadian_mode():
    red = [int(i / 100) for i in range(23000, 25600, 12)]
    green = [int(i / 100) for i in range(23500, 14600, -41)]
    blue = [i for i in range(255, 38, -1)]
    #brightness = 1
    r, g = 0, 0
    #lux = bh1750.read_lux()
    
    #brightness = (500-lux)/1000
    #brightness = min(brightness,1)
    #print(brightness)
    for i in range(len(blue)):
        #lux = bh1750.read_lux()
        #brightness = 1 - min(1,(lux-600)/1000)
        #print("Brightness: ",brightness)
        if r >= len(red):
            r = len(red) - 1
        if g >= len(green):
            g = len(green) - 1
        np.fill((red[r], green[g], blue[i]))
        np.write()
        time.sleep(0.1)
        print(red[r], green[g], blue[i])
        r += 1
        g += 1
    #global brightness
    #np.fill((int(255 * brightness), int(255 * brightness), int(255 * brightness)))
    #np.write()
    #print(clockObject.datetime())
    #print("circadian mode initiated")

async def power_saver_mode():
    global brightness
    lux = bh1750.read_lux()
        # Map lux value to LED brightness (adjust the scaling factor as needed)
    brightness = 1-(min(lux,300))/300 # Limit brightness to a maximum value (0 to 1)+
        # Set NeoPixel colors
    np.fill((int(255 * brightness), int(255 * brightness), int(255  * brightness)))
    np.write()
    print(f"Brightness: {brightness*100:.2f}%")
    #await asyncio.sleep(1)
    print("power saver mode initiated")

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
    
max_wait = 10
print('Waiting for connection')
while max_wait > 10:
    if wlan.status() < 0 or wlan.status() >= 3:
        print("Connection status : ",wlan.status())
        break
    print(">>> Waiting for connection...")
    max_wait -= 1    
    time.sleep(100)
    
status = wlan.ifconfig()#None
if wlan.status() != 3:
    raise RuntimeError('Connections failed')
else:
    status = wlan.ifconfig()
    print('Connection to', ssid,'succesfull established!', sep=' ')
    print('IP-adress: ' + status[0])
    
ipAddress = status[0]
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
brightness=1
mode = "power_saver"

async def hosting():
    global brightness,mode
    while True:
        try:
            cl, addr = s.accept()
            print('Connection from ', addr, "accepted!")
            request = cl.recv(1024)
            request = str(request)
            print("*"*10)
            print(request)
            print("*"*10)
            if request.find('/mode/normal') == 6:
                normal_mode()
                mode = "normal"
                print(">>> Normal mode ON...")
            if request.find('/mode/circadian') == 6:
                circadian_mode()
                mode = "circadian"
                print(">>> Circadian mode ON...")
            if request.find('/mode/power_saver') == 6:
                task = asyncio.create_task(power_saver_mode())
                #await task
                mode = "power_saver"
                print(">>> Power saver mode ON...")
            if request.find('/brightness/') == 6:
                brightness = int(request[18:21])/100
                if mode == "circadian": circadian_mode()
                if mode == "power_saver": power_saver_mode()
                if mode == "normal": normal_mode()
                print(f">>> Brightness value changed to {brightness*100}%...")
                 
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(Website())
            cl.close()
        except OSError as e:
            cl.close()
            print('connection closed')
        finally:
            await asyncio.create_task(blink_led(0.1))

async def main():
    print("In main")
    global mode
    main_task = asyncio.create_task(hosting())
    while True:
        if mode == "power_saver":
            await power_saver_mode()
#         if mode == "normal":
#             normal_mode()
#         if mode == "circadian":
#             circadian_mode()
        await asyncio.sleep(1)

# Run the event loop
try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()