try:
    import usocket as socket
except:
    import socket

response_404 = """HTTP/1.0 404 NOT FOUND

<h1>404 Not Found</h1>
"""

response_500 = """HTTP/1.0 500 INTERNAL SERVER ERROR

<h1>500 Internal Server Error</h1>
"""

response_template = """HTTP/1.0 200 OK

%s
"""

import machine
import ntptime, utime
from machine import RTC
from time import sleep

rtc = RTC()
try:
    seconds = ntptime.time()
except:
    seconds = 0
rtc.datetime(utime.localtime(seconds))

led = machine.Pin(9, machine.Pin.OUT)
switch_gpio = machine.Pin(10, machine.Pin.IN)
adc = machine.ADC(0)

def time():
    body = """<html>
<body>
<h1>Time</h1>
<p>%s</p>
</body>
</html>
""" % str(rtc.datetime())

    return response_template % body

def dummy():
    body = "This is a dummy endpoint"

    return response_template % body

def light_on():
    led.value(1)
    body = "Light has been turned on"

    return response_template % body

def light_off():
    led.value(0)
    body = "Light has been turned off"

    return response_template % body

def switch():
    values = {0: 'Off', 1: 'On'}
    body = "The switch is {}".format(values[switch_gpio.value()])

    return response_template % body

def light():
    body = "{value: " + str(adc.read()) + "}"

    return response_template % body

handlers = {
    'time': time,
    'dummy': dummy,
    'light_on': light_on,
    'light_off': light_off,
    'switch': switch,
    'light': light,
}

def main():
    s = socket.socket()
    ai = socket.getaddrinfo("0.0.0.0", 8080)
    addr = ai[0][-1]

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(addr)
    s.listen(5)
    print("Listening, connect your browser to http://<this_host>:8080")

    while True:
        sleep(1)
        res = s.accept()
        client_s = res[0]
        client_addr = res[1]
        req = client_s.recv(4096)
        print("Request:")
        print(req)

        try:
            path = req.decode().split("\r\n")[0].split(" ")[1]
            handler = handlers[path.strip('/').split('/')[0]]
            response = handler()
        except KeyError:
            response = response_404
        except Exception as e:
            response = response_500
            print(str(e))

        client_s.send(b"\r\n".join([line.encode() for line in response.split("\n")]))

        client_s.close()
        print()

main()
