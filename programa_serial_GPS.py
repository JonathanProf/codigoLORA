from machine import UART, Pin
import time

# Inicalización de puertos Thonny
uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
uart1 = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

longitud = 0.
longitud = 0.
timeStamp = str()
speedBoat = float()

while True:
    
    rxData = bytes()
    rxString = str()
    
    while uart0.any() > 0:
        rxData += uart0.read(10)
        rxString = rxData.decode('utf-8')

        index_1 = rxString.rfind('$GPRMC')
        index_2 = rxString.find('$', index_1+5)
        
        time.sleep(0.05)
        
        if index_1 != -1 and index_2 != -1:
            
            dataGPS = rxString[index_1:index_2]
            
            uart1.write(dataGPS)
            time.sleep(0.05)
            
            listado_datos = dataGPS.split(',')
            #print(listado_datos)
            listado_datos.clear()
            rxData = b' '
            rxString = ' '
            uart1.write(dataGPS)
