import board
import busio
import digitalio
import time

# Configuración de los puertos M0, M1, AUX
portM1 = digitalio.DigitalInOut(board.GP18)
portM0 = digitalio.DigitalInOut(board.GP19)
portAUX = digitalio.DigitalInOut(board.GP20)


portM1.direction = digitalio.Direction.OUTPUT
portM1.value = False

portM0.direction = digitalio.Direction.OUTPUT
portM0.value = False

portAUX.direction = digitalio.Direction.INPUT

uartGPS = busio.UART(board.GP4, board.GP5, baudrate=9600)
uartSerial = busio.UART(board.GP16, board.GP17, baudrate=9600)

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
        
        horaCol = int(tmp[0:2])

        horaCol = (horaCol-5) if (horaCol-5) >= 0 else 24 + (horaCol - 5)

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
        return '1-7-2022 00:00:00'

def obtenerLong_and_lat( lon, lat ):

    try:
        if (lon is None) or (float(lon) == 0.0) or (lat is None) or (float(lat) == 0.0):
            return 6.2677941, -75.5684756
        
        datos_1 = lon.split('.')
        datos_2 = lat.split('.')
        
        # Calculo longitud
        longitud = obtenerDatoDecimal(datos_1)
        
        #Calculo latitud
        latitud = obtenerDatoDecimal(datos_2)
        
        return longitud, latitud
    except:
        return 6.2677941, -75.5684756

def obtenerVelocidad ( vel ):
    try:
        velocity = float(vel) * 0.514444
        return round(velocity,2)
    except:
        return 1.

# Inicio del programa

longitud = 0.
longitud = 0.
timeStamp = str()
speedBoat = float()
tripTime = int(1)
windDir = int(0)
rxData = bytes()
while True:
    data = uartGPS.read(58)  # read up to 32 bytes
    #time.sleep(0.1)
    # print(data)  # this is a bytearray type

    if data is not None:
        
        rxData += data
        rxString = ''.join([chr(b) for b in rxData])

        index_1 = rxString.find('$GPRMC')
        index_2 = rxString.find('$', index_1+5)

        if index_1 != -1 and index_2 != -1:
            tripTime += 1
            
            dataGPS = rxString[index_1:index_2]
            
            listado_datos = dataGPS.split(',')

            #if len(listado_datos) == 13 and listado_datos[0] == '$GPRMC' and listado_datos[2] == 'A':
            if len(listado_datos) == 13 and listado_datos[0] == '$GPRMC' and portAUX.value == True:
                
                latitud, longitud = obtenerLong_and_lat(listado_datos[3], listado_datos[5])
                longitud = -longitud if listado_datos[6] == 'W' else longitud
                timeStamp = obtenerTiempo(listado_datos[1], listado_datos[9])
                speedBoat = obtenerVelocidad(listado_datos[7])
                #print(f'{latitud}, {longitud}, time={timeStamp}, vel={speedBoat}')
                windDir = (windDir+10) if windDir < 360 else 0
                dataLORA = "{"+'"tripTime": {0},"timeStamp": "{1}","gpsCoords": [{2}, {3}],"windDir": {4},"windSpeed": 17,"boatAccell": {5},"boatGyros": 14,"boatMagnet": 29,"battStatus": 85,"rudderAngle": 45,"sail1Angle": 54,"sail2Angle": 73'.format(tripTime, timeStamp, latitud, longitud, windDir, speedBoat)+"}\r\n"
                #dataLORA = "{"+'"gpsCoords": [{0}, {1}]'.format(latitud, longitud)+"}\r\n"
                listado_datos.clear()
                rxData = b' '
                rxString = ' '
                print(dataLORA)
                uartSerial.write(bytearray(dataLORA,'ascii'))
                time.sleep(0.5)