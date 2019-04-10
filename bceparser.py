import datetime
import utils
from struct import pack,unpack

from time import gmtime,strftime
from ctypes import *
fmt = "%Y-%m-%d %H:%M:%S"



mask1 = {'0':17,
         '1': 2,
         '2': 2,
         '3': 2,
         '4': 2,
         '5': 2,
         '6': 2,
         '7': 2,
         '8': 2,
         '9': 2,
         '10': 4,
         '11': 4,
         '12': 2,
         '13': 2,
         '14': 9,
         '15': 1,
         }
mask2 = {'0':2,
         '1': 2,
         '2': 2,
         '3': 2,
         '4': 2,
         '5': 2,
         '6': 2,
         '7': 2,
         '8': 2,
         '9': 2,
         '10': 4,
         '11': 4,
         '12': 2,
         '13': 2,
         '14': 9,
         '15': 1,
         }


def create_dict_fromlist(datalist):
    length=len(datalist)
    key=[]
    for i in range(0,length):
        key.append(str(i))
    resultdict = dict(zip(key,datalist))
    return resultdict
# function POP_STRING
# description : the function here pops a string and returns the popped value and the string after pop
# input :  data (string) and the length (int )that has to be popped
# output :  popped value (string) and the data(string) after pop operation

def pop_string(data,length):
    popped = data[:length]
    data = data[length:]
    return popped,data



#funtion convert
#description : the function here is to convert to floating point representation
# input : hex value
# ouput : float value
def convert(s):
    i = int(s, 16)                   # convert from hex to a Python int
    cp = pointer(c_int(i))           # make this into a c integer
    fp = cast(cp, POINTER(c_float))  # cast the int pointer to a float pointer
    return fp.contents.value         # dereference the pointer, get the float

# function reorder_hexstring
# description : the function reorders the string to have it in reverse byte order
# input :  value (string)
# output :  reversed value (string)
def reorder_hexstring(value):
    result= value.encode('utf-8')

    resultnew=[]
    for i in range(0,len(result),2):
        resultnew.append(result[-2:].decode('utf-8'))
        result=result[:-2]
    result=(''.join(resultnew))
    return result

# function check_mask
# description : the function checks the mask1 to determine what data is available
# input :  mask string
# output : returns a list of available items
def check_mask(mask_string):
    available_data = []
    mask_string=mask_string[::-1]
    for i in range(0,(len(mask_string))):
        if mask_string[i]=='1':
            available_data.append(i)
    return available_data

# function parse_string
# description : the function does the logic to convert bytes into data
# input :  data (string) , lengthinbytes(int) , content (string) to do logic
# output :  data (string) , val (result) , content (what the content was)
def parse_string(data,lengthinbytes,content):
    length=2*lengthinbytes
    result,data=pop_string(data,length)
    # imei obtained in reverse order- convert reordered hex to int
    if content == 'imei':
        result=reorder_hexstring(result)
        val=int(result, 16)
    # lenth is two bytes object which needs to be reordered and then reordered hex to int
    elif content == 'len':
        result=reorder_hexstring(result)
        val=int(result,16)
    # service id is hex to int
    elif content == 'serviceid':
        val=int(result,16)
    # confirmation key is hex to int
    elif content == 'confirmationkey':
        val=int(result,16)
    #stucture length is 1 byte hex to int
    elif content == 'structurelength':
        val=int(result,16)
    #checksum is 1 byte hex to int
    elif content == 'checksum':
        val=int(result,16)
    #date time is a custom calculation where the reordered hex is multiplied by 2 and added with another hex value to obtain the epoch time
    elif content == 'data_time':
        result=reorder_hexstring(result)
        result=result[:-1]
        val=(int(result,16))*2
        val=val+(int('47798280',16))
        epochtime =val
        t = datetime.datetime.fromtimestamp(epochtime)
        val=t.strftime(fmt)
    #data mask required the byte to be convereted to bits and then processed to generate a mask for data that is present
    elif content == 'data_mask':
        result=reorder_hexstring(result)
        val="{0:b}".format(int(result,16))
        val=val.zfill(16)
        available_data=check_mask(val)
        val=available_data
    #data cordinates is a combination of events
    elif content == 'data_coord':

        coord=[]
        lon =convert(reorder_hexstring(result[:8]))
        coord.append(lon)
        lat=convert(reorder_hexstring(result[8:16]))
        coord.append(lat)
        speed=int((result[16:18]),16)
        coord.append(speed)
        hdop=int(('0'+result[18]),16)*5
        coord.append(hdop)
        sat=int('0'+result[19],16)
        coord.append(sat)
        course=int(result[20:22],16)
        coord.append(course)
        alt=int(reorder_hexstring(result[22:26]),16)
        coord.append(alt)
        odo=int((result[26:]),16)
        coord.append(odo)
        val=coord
    elif content == 'data_di':
        di=[]
        val="{0:b}".format(int(result,16))
        val=val.zfill(16)
        for i in range(0,16):
            di.append(val[i])
        val=di
    elif content == 'gsminfo':
        gsminfo=[]
        mcc=int(reorder_hexstring(result[:4]),16)
        gsminfo.append(mcc)
        mnc=int((result[4:6]),16)
        gsminfo.append(mnc)
        lac=int(reorder_hexstring(result[6:10]),16)
        gsminfo.append(lac)
        cell_id=int(reorder_hexstring(result[10:14]),16)
        gsminfo.append(cell_id)
        ta=int((result[14:16]),16)
        gsminfo.append(ta)
        gsmlvl=int((result[16:]),16)
        gsminfo.append(gsmlvl)
        val=gsminfo

    else:
        if length>2:
            result=reorder_hexstring(result)
            val=int(result,16)
        else:
            val = int(result,16)
    ret = (data,val,content)
    return ret



# function parse_string
# description : the function does the logic to cover bytes into data
# input :  data (string)
# output :  result (list)
def parsed_data(data):
    #calling function to process the result
    parsed=process_data(data)
    #calling function to build the ack response
    ack=process_ack(data)

    return parsed

def process_ack(data):

    result = ''
    #add imei
    result = data[:16]
    #adding length and ServiceKey
    result = result + "020019"
    #get CONFIRMATION KEY A to generate CONFIRMATION KEY B that is required to be in ACK
    #foo function to just remove the first 11 bytes (22 charachters)
    # future use below since it is cleaner
    # data=data[22:]
    data,val,content=parse_string(data,11,'confirmationkey')
    data,val,content=parse_string(data,1,'confirmationkey')
    # perform required operation to
    confirmationkeyB= int(hex(val),16) & int(hex(127),16)
    confirmationkeyB=("%02X" % confirmationkeyB)
    #confirmation key b is added
    result= result + confirmationkeyB
    hexresult = bytearray.fromhex(result)
    #adding checksum byte
    checksum=0
    for i in hexresult:
        checksum=checksum+i
    if checksum>255:
        result=result+(hex(checksum)[-2:])
    else:
        result=result+(hex(checksum))
    #Resulting ack message is converted to byte array and returned
    return bytes.fromhex(result)

# function process_data
# description : the function does the logic to call the parse_string function by passing required arguments
# input :  data (string), bytes(int), contentidentifier(string)
# output :  data (string) , val (string/int/list) , contentidentifier(string)
def process_data(data):
    proceed= True
    #function builds the message data
    result = []
    #IMEI
    data,val,content=parse_string(data,8,'imei')
    result.append(val)
    #length
    data,val,content=parse_string(data,2,'len')
    result.append(val)
    # service key
    data,val,content=parse_string(data,1,'serviceid')

    result.append(val)
    #confirmation key A

    data,val,content=parse_string(data,1,'confirmationkey')
    result.append(val)

    # here you need to build a function that will keep processing the structure length
    #structure length
    # while there is not more than two remaining bytes then proceed
    while (proceed and (len(data)>2)):
        #print("Going to process : {}".format(data))
        structure = []

        data,val,content=parse_string(data,1,'structurelength')
        structure.append(val)
        data_length=val

        #date time
        data,val,content=parse_string(data,4,'data_time')
        structure.append(val)
        # data mask 1
        data,val,content=parse_string(data,2,'data_mask')
        structure.append(val)
        # there will always be the first mask. however to determine if there are additional masks we must check the 15 bit if that is high there is the next mask
        aggregateddatamasklist=[]
        aggregateddatamasklist.append(val)
        while (15 in val):
            i=2
            #addtional data mask if present
            data,val,content=parse_string(data,2,'data_mask')
            structure.append(val)
            aggregateddatamasklist.append(val)
            i=i+1
        #process mask values one at a time
        num=0
        for item in aggregateddatamasklist:
            num=num+1
            for i in item:
                if num==1:
                    if i==0:
                        data,val,content=parse_string(data,17,'data_coord')
                        structure.append(val)
                    elif i==1:
                            data,val,content=parse_string(data,2,'data_di')
                            structure.append(val)
                    elif i==2:
                            data,val,content=parse_string(data,2,'ADC1')
                            structure.append(val)
                    elif i==3:
                            data,val,content=parse_string(data,2,'ADC2')
                            structure.append(val)
                    elif i==4:
                            data,val,content=parse_string(data,2,'ADC3')
                            structure.append(val)
                    elif i==5:
                            data,val,content=parse_string(data,2,'ADC4')
                            structure.append(val)
                    elif i==6:
                            data,val,content=parse_string(data,2,'ADC5')
                            structure.append(val)
                    elif i==7:
                            data,val,content=parse_string(data,2,'ADC6')
                            structure.append(val)
                    elif i==8:
                            data,val,content=parse_string(data,2,'ADC7')
                            structure.append(val)
                    elif i==9:
                            data,val,content=parse_string(data,2,'ADC8')
                            structure.append(val)
                    elif i==10:
                            data,val,content=parse_string(data,4,'Countfreq1')
                            structure.append(val)
                    elif i==11:
                            data,val,content=parse_string(data,4,'Countfreq2')
                            structure.append(val)
                    elif i==12:
                            data,val,content=parse_string(data,2,'filADC1')
                            structure.append(val)
                    elif i==13:
                            data,val,content=parse_string(data,2,'filADC2')
                            structure.append(val)
                    elif i==14:
                            data,val,content=parse_string(data,9,'gsminfo')
                            structure.append(val)
                if num==2:
                    if i==0:
                        data,val,content=parse_string(data,2,'wheelspeed')
                        structure.append(val)
                    elif i==1:
                        data,val,content=parse_string(data,1,'accel_pedal')
                        structure.append(val)
                    elif i==2:
                        data,val,content=parse_string(data,4,'total_fuel_used')
                        structure.append(val)
                    elif i==3:
                        data,val,content=parse_string(data,1,'fuel_level')
                        structure.append(val)
                    elif i==4:
                        data,val,content=parse_string(data,2,'tacho')
                        structure.append(val)
                    elif i==5:
                        data,val,content=parse_string(data,4,'engine hours')
                        structure.append(val)
                    elif i==6:
                        data,val,content=parse_string(data,4,'mileagse')
                        structure.append(val)
                    elif i==7:
                        data,val,content=parse_string(data,1,'enginetemp')
                        structure.append(val)
                    elif i==8:
                        data,val,content=parse_string(data,1,'ADC7')
                        structure.append(val)
                    elif i==9:
                        data,val,content=parse_string(data,1,'ADC8')
                        structure.append(val)
                    elif i==10:
                        data,val,content=parse_string(data,2,'Countfreq1')
                        structure.append(val)
                    elif i==11:
                        data,val,content=parse_string(data,8,'Countfreq2')
                        structure.append(val)
                    elif i==12:
                        data,val,content=parse_string(data,2,'filADC1')
                        structure.append(val)
                    elif i==13:
                        data,val,content=parse_string(data,8,'filADC2')
                        structure.append(val)
                    elif i==14:
                        data,val,content=parse_string(data,2,'gsminfo')
                        structure.append(val)
                if num==3:
                    if i==0:
                        data,val,content=parse_string(data,2,'wheelspeed')
                        structure.append(val)
                    elif i==1:
                        data,val,content=parse_string(data,4,'accel_pedal')
                        structure.append(val)
                    elif i==2:
                        data,val,content=parse_string(data,3,'total_fuel_used')
                        structure.append(val)
                    elif i==3:
                        data,val,content=parse_string(data,1,'fuel_level')
                        structure.append(val)
                    elif i==4:
                        data,val,content=parse_string(data,20,'tacho')
                        structure.append(val)
                    elif i==5:
                        data,val,content=parse_string(data,2,'engine hours')
                        structure.append(val)
                    elif i==6:
                        data,val,content=parse_string(data,8,'mileagse')
                        structure.append(val)
                    elif i==7:
                        data,val,content=parse_string(data,2,'ADC6')
                        structure.append(val)
                    elif i==8:
                        data,val,content=parse_string(data,2,'ADC7')
                        structure.append(val)
                    elif i==9:
                        data,val,content=parse_string(data,6,'ADC8')
                        structure.append(val)
                    elif i==10:
                        data,val,content=parse_string(data,6,'Countfreq1')
                        structure.append(val)
                    elif i==11:
                        data,val,content=parse_string(data,21,'Countfreq2')
                        structure.append(val)
                    elif i==12:
                        data,val,content=parse_string(data,20,'filADC1')
                        structure.append(val)
                    elif i==13:
                        data,val,content=parse_string(data,9,'filADC2')
                        structure.append(val)
                    elif i==14:
                        data,val,content=parse_string(data,21,'gsminfo')
                        structure.append(val)
                if num==4:
                    if i==0:
                        data,val,content=parse_string(data,4,'wheelspeed')
                        structure.append(val)
                    elif i==1:
                        data,val,content=parse_string(data,30,'accel_pedal')
                        structure.append(val)
                    elif i==2:
                        data,val,content=parse_string(data,4,'total_fuel_used')
                        structure.append(val)
                    else:
                        data,val,content=parse_string(data,4,'total_fuel_used')
                        structure.append(val)
                if num==5:
                    if i==0:
                        data,val,content=parse_string(data,4,'wheelspeed')
                        structure.append(val)
                    elif i==1:
                        data,val,content=parse_string(data,1,'accel_pedal')
                        structure.append(val)
                    elif i==2:
                        data,val,content=parse_string(data,66,'total_fuel_used')
                        structure.append(val)
        result.append(structure)
        #print(" Length of data remaining is {} :{}".format(len(data),data))
        if (len(data)>1 and len(data)<40):
            #print("ignored and removed {}".format(data[:-2]))
            data=data[-2:]
            #print(data)
            proceed= False



    data,val,content=parse_string(data,1,'checksum')
    result.append(val)

    #print(result)
    return result

if __name__ == '__main__':
    parsed_data("4c79e971581403002601a5021b0710eca58ac0008000800000c180b5380600a801027510863000481b3710eca58ac0008000800000c08089380600a801027510863000482ce710eca58bc000800080000008a75c4211cac841001863000000000000c1a080380600a801027510863000482c0711eca58bc000800080000008a75c4211cac841001863000000000000c080b5380600a801027510863000482cd75aeca58bc000800080000008a75c4211cac841001863000000000000c0809b380600a801027510f96600441be75aeca58ac0008000800000c18077380400a801027510f96600441b075beca58ac0008000800000c08080380600a801027510f96600442ca75ceca58bc000800080000008a75c4211cac841002763000000000000c18077380600a801027510f9660044e9")
