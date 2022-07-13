from machine import UART, Pin
import time

# Inicalización de puertos Thonny
uartSerial = UART(0, baudrate=9600, tx=Pin(16), rx=Pin(17)) # Serial
uartGPS = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5)) # GPS

# Definición de funciones
def obtenerDatoDecimal( numeros ):
    try:
        entero = int(numeros[0][:-2])
        decimal_1 = float(numeros[0][-2:])
        
        decimal_2 = float(numeros[1])/10**(len(numeros[1]))

        #num = entero + (decimal_1 + (decimal_2/60))/60
        num = entero + (decimal_1 + decimal_2)/60
        return round(num,8)
    except:
        return 0.

def obtenerTiempo(hora, fecha):
    try:
        timeStamp = str()
        tmp = hora.split('.')[0]
        
        horaCol = int(tmp[0:2]) - 5
        horaCol = str(horaCol)
        
        tmp = horaCol + tmp[2:]
        
        for i, car in enumerate(fecha):
            if i % 2 == 0 and i > 0:
                timeStamp += '-'
            timeStamp += car
        
        timeStamp += ' '
            
        for i, car in enumerate(tmp):
            if i % 2 == 0 and i > 0:
                timeStamp += ':'
            timeStamp += car

        return timeStamp
    except:
        return '0-0-0 00:00:00'

def obtenerLong_and_lat( lon, lat ):

    try:
        
        datos_1 = lon.split('.')
        datos_2 = lat.split('.')
        
        # Calculo longitud
        longitud = obtenerDatoDecimal(datos_1)
        
        #Calculo latitud
        latitud = obtenerDatoDecimal(datos_2)
        
        return longitud, latitud
    except:
        return 0., 0.

def obtenerVelocidad ( vel ):
    try:
        velocity = float(vel) * 0.514444
        return round(velocity,2)
    except:
        return 0.

# Inicio del programa

longitud = 0.
longitud = 0.
timeStamp = str()
speedBoat = float()

while True:
    
    rxData = bytes()
    rxString = str()

    while uartGPS.any() > 0:
        rxData += uartGPS.read(50)
        time.sleep(0.05)
        rxString = rxData.decode('utf-8')

        index_1 = rxString.find('$GPRMC')
        index_2 = rxString.find('$', index_1+5)

        if index_1 != -1 and index_2 != -1:
            
            dataGPS = rxString[index_1:index_2]
            
            listado_datos = dataGPS.split(',')

            #if len(listado_datos) == 13 and listado_datos[0] == '$GPRMC' and listado_datos[2] == 'A':
            if len(listado_datos) == 13 and listado_datos[0] == '$GPRMC':
                
                latitud, longitud = obtenerLong_and_lat(listado_datos[3], listado_datos[5])
                longitud = -longitud if listado_datos[6] == 'W' else longitud
                timeStamp = obtenerTiempo(listado_datos[1], listado_datos[9])
                speedBoat = obtenerVelocidad(listado_datos[7])
                #print(f'{latitud}, {longitud}, time={timeStamp}, vel={speedBoat}')

                dataLORA = "{"+'"tripTime": 15,"timeStamp": "{0}","gpsCoords": [{1}, {2}],"windDir": 90,"windSpeed": 17,"boatAccell": {3},"boatGyros": 14,"boatMagnet": 29,"battStatus": 85,"rudderAngle": 45,"sail1Angle": 54,"sail2Angle": 73'.format(timeStamp, latitud, longitud, speedBoat)+"}\r\n"
                listado_datos.clear()
                rxData = b' '
                rxString = ' '
                
                uartSerial.write(dataLORA)
                time.sleep(0.1)
