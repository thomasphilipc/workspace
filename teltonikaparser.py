import datetime
import binascii
import numpy as np


from time import gmtime,strftime

fmt = "%Y-%m-%d %H:%M:%S"


def pop_string(data,length):
    popped = data[:length]
    data = data[length:]
    return popped

def parse_string(data,length,content):

    result=pop_string(data,length)
    val = int(str(result), 16)
    #print("{} is {}".format(content,val))
    data = data[length:]

    ret = (data,val)
    return ret

def convert_to_driverid(value):
    driverid=hex(int(value))
    return(str(driverid)[3:-2][::-1].upper())


def teltonika(data):
    print("in parsed data")

    parsed=process_data(data)
    print(parsed)
    return parsed

def codec_12(data):
    print("Preparing data for gprs forward commands")
    print("Data to send is  {}".format(data))
    # convert from string to hex
    hexcommand=binascii.hexlify(data.encode())
    print(" data in hex is {}".format(hexcommand))
    command = "{:08x}".format(0)

    datasize = "00000000"
    testcommand = b"0c0105000000127365746469676f7574203130203320330D0A01"
    fixedbyte = b"0c"
    onecommand = b"01"
    eocommand = b"0D0A"
    response = b"06"
    request = b"05"
    int_lenghtofcommnad=int((len(hexcommand)/2)+2)
    lengthofcommand = "{:08x}".format(int_lenghtofcommnad)
    int_totallength=int_lenghtofcommnad+8
    totallength = "{:08x}".format(int_totallength)
    codec12_data = bytearray(b"")
    codec12_data+=(command).encode()
    codec12_data+=(totallength).encode()
    codec12_data+=fixedbyte
    codec12_data+= onecommand
    codec12_data+= request
    codec12_data+=lengthofcommand.encode()
    codec12_data+=(hexcommand)
    codec12_data+=(eocommand)
    codec12_data+= onecommand


    print(codec12_data)



def crc16(data: bytes, poly=0xA001):
    '''
    CRC-16-CCITT Algorithm
    '''
    data = bytearray(data)
    crc = 0x0

    for b in data:

        cur_byte = 0xFF & b
        for _ in range(0, 8):
            if (crc & 0x0001) ^ (cur_byte & 0x0001):
                crc = (crc >> 1) ^ poly
            else:
                crc >>= 1
            cur_byte >>= 1
    crc = (~crc & 0xFFFF)
    crc = (crc << 8) | ((crc >> 8) & 0xFF)

    return crc & 0xFFFF

    return np.uint16(crc)

def process_data(data):

    print("In process data")
    paramdict = {1:"DigitalInputStatus1",2:"DigitalInputStatus2",3:"DigitalInputStatus3",4:"DigitalInputStatus4",9:"AnalogInput1",10:"AnalogInput2",21:"GSMlevel",24:"Speed",66:"ExternalPowerVoltage",67:"BatteryVoltage",68:"BatteryCurrent",69:"GNSSStatus",72:"DallasTemperature1",73:"DallasTemperature2",74:"DallasTemperature3",75:"DallasTemperatureSensorID1",76:"DallasTemperatureSensorID2",77:"DallasTemperatureSensorID3",78:"iButtonID",79:"Networktype",80:"WorkingMode",99:"Continuousodometer",179:"DigitalOutput1state",180:"DigitalOutput2state",181:"PDOP",182:"HDOP",199:"OdometerValue(VirtualOdometer)",200:"DeepSleep",205:"CellID",206:"AreaCode",239:"Ignition",240:"MovementSensor",241:"GSMOperatorCode",155:"Geofence zone 01",156:"Geofence zone 02",157:"Geofence zone 03",158:"Geofence zone 04",159:"Geofence zone 05",175:"Auto Geofence",177:"Idling",249:"Jamming detection",250:"Trip",251:"Immobilizer",252:"Authorized driving",253:"Green driving type",254:"Green driving value",255:"Over Speeding"}

    #additional for FM63
    paramdict.update({219:"(MSB)CCID",220:"CCID",221:"(LSB)CCID",62:"DallasTemperatureID1",63:"DallasTemperatureID2",64:"DallasTemperatureID3",65:"DallasTemperatureID4",216:"TotalOdometer",218:"IMSI",22:"ActualProfile",71:"GNSSStatus",178:"NetworkType",236:"X-axis",237:"Y-axis",238:"Z-axis"})

    if (len(data)>34):
        parsed=[]
        print ("{} received data:  {}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()),data))
        print((len(data)/2))

        # drop first 16 chars (8 bytes)
        #result=pop_string(data,16)
        #print(result)
        #data = data[16:]

        #codec
        result=pop_string(data,2)
        line=("Codec is {}".format(int(result, 16)))
        parsed.append(line)
        data = data[2:]

        #avl data count
        count=pop_string(data,2)
        line=("AVL data count is {}".format(int(count, 16)))
        parsed.append(line)
        data = data[2:]

        for i in range(0,int(count, 16)):

            # timestamp
            result=pop_string(data,16)
            epochtime =int(result, 16)

            t = datetime.datetime.fromtimestamp(float(epochtime)/1000.)
            line=("Epoch is {} Timestampt is  {}".format(epochtime,t.strftime(fmt))) # prints 2012-08-28 02:45:17
            parsed.append(line)
            data = data[16:]

            result=pop_string(data,2)
            line=("Priority is {}".format(int(result, 16)))
            parsed.append(line)
            data = data[2:]

            result=pop_string(data,30)
            line=("GPS is {}".format(int(result, 30)))
            parsed.append(line)
            data = data[30:]

            data,value=parse_string(data,2,"Event ID")
            line=( "The event id {} was generated by {}".format(value,paramdict.get(value)))
            parsed.append(line)


            data,value=parse_string(data,2,"Element Count")
            line=("Element Count is {}".format(value))
            parsed.append(line)


            data,value=parse_string(data,2,"1Byte element count")
            line=( " Total 1 byte elements are {}".format(value))
            parsed.append(line)
            for i in range(1,value+1):
                data,value1=parse_string(data,2,"ID")
                data,value=parse_string(data,2,"value")
                if value1 in paramdict:
                    line=( " the {} id is {}/{} with value {}".format(i,value1,paramdict.get(value1),value))
                    parsed.append(line)
                else:
                    line=( " the {} id is {} with value {}".format(i,value1,value))
                    parsed.append(line)

            data,value=parse_string(data,2,"2Byte element count")
            line=( " Total 2 byte elements are {}".format(value))
            parsed.append(line)
            for i in range(1,value+1):
                data,value1=parse_string(data,2,"ID")
                data,value=parse_string(data,4,"value")
                if value1 in paramdict:
                    line=( " the {} id is {}/{} with value {}".format(i,value1,paramdict.get(value1),value))
                    parsed.append(line)
                else:
                    line = (" the {} id is {} with value {}".format(i,value1,value))
                    parsed.append(line)

            data,value=parse_string(data,2,"4Byte element count")
            line=( " Total 4 byte elements are {}".format(value))
            parsed.append(line)
            for i in range(1,value+1):
                data,value1=parse_string(data,2,"ID")
                data,value=parse_string(data,8,"value")
                if value1 in paramdict:
                    line=( " the {} id is {}/{} with value {}".format(i,value1,paramdict.get(value1),value))
                    parsed.append(line)
                else:
                    line=( " the {} id is {} with value {}".format(i,value1,value))
                    parsed.append(line)

            data,value=parse_string(data,2,"8Byte element count")
            line=( " Total 4 byte elements are {}".format(value))
            parsed.append(line)
            for i in range(1,value+1):
                data,value1=parse_string(data,2,"ID")
                data,value=parse_string(data,16,"value")
                if value1 in paramdict:
                    if value1==78:
                        driverid=convert_to_driverid(value)
                        line=( " the {} id is {}/{} with value {}".format(i,value1,paramdict.get(value1),driverid))
                        parsed.append(line)

                    else:
                        line=( " the {} id is {}/{} with value {}".format(i,value1,paramdict.get(value1),value))
                        parsed.append(line)
                else:
                     line=( " the {} id is {} with value {}".format(i,value1,value))
                     parsed.append(line)

        data,value=parse_string(data,2,"AVL Data count")
        line=( " AVL Data count {}".format(value))
        parsed.append(line)

        #data,value=parse_string(data,8,"CRC ")
        #print( " CRC {}".format(value))

        return parsed

    else:
        return 0

if __name__ == '__main__':
    # print_a() is only executed when the module is run directly.
    teltonika("0600000026444F5554313A312054696D656F75743A337320444F5554323A302054696D656F75743A337320")
    #codec_12("setdigout 11")
    codec_12("setdigout 10 3 3")
    print(hex(crc16(b"0c0105000000127365746469676f7574203130203320330D0A01")))

##00000000000000180c0105000000107365746469676f757420313020332033010000E96C
##00000000000000160C01050000000E7365746469676F75742031310D0A010000E258
##000000000000001a0c0105000000127365746469676f7574203130203320330D0A0100004fbd
