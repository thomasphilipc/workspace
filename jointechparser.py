from pymongo import MongoClient

client = MongoClient()
client = MongoClient("mongodb+srv://admin:W1nd0ws87@cluster0-wkvwq.gcp.mongodb.net/test?retryWrites=true")
mydb = client["mydatabase"]
mycol = mydb["jointechraw-smoothflow"]



def create_dict_fromlist(datalist):
    length=len(datalist)
    key=[]
    for i in range(0,length):
        key.append(str(i))
    resultdict = dict(zip(key,datalist))
    return resultdict


def process_data(data):
    #try:
        list=[]
        print("------------------------------------------------")

        print(data.hex())
        list.append(data.hex())
        insertdict= create_dict_fromlist(list)
        x=mycol.insert_one(insertdict)
        print("Data inserted in mongodb")
        print(x.inserted_id)
        check= str(data.hex())
        if check.startswith('28'):
            print(data.decode("utf-8"))
            ascii_value=data.decode("utf-8")
            if (process_ack(ascii_value)==1):
                result=None
                return result
            elif (process_ack(ascii_value)==2):
                result="(P46)"
                return str.encode(result)
        elif check.startswith('24'):
            process(data)
            result="(P35)"
            #(P43,888888)
            return str.encode(result)
        else:
            result=None
            return result


    #except:
    #    print("Error")



def process_ack(data):
    #checking if it is a lock or unlock
    if data.find('P45')==12:
        return 2


def process(data):
    if len(data)>40:
        print("Protocol Head")
        print(data[:1].hex())
        print("Device ID")
        print(data[1:6].hex())
        print("Protocol version")
        print(data[6:7].hex())
        print("DeviceType")
        print(str(data[7:8].hex())[0])
        print("Data Type")
        print(str(data[7:8].hex())[1])
        print("DataLength")
        print(data[8:10].hex())
        print("Date")
        print(data[10:13].hex())
        print("Time")
        print(data[13:16].hex())
        print("Latitude")
        print(data[16:20].hex())
        print("Longitude")
        print(data[20:25].hex())
        #print("Location Indicator")
        #print(str(data[24:25].hex())[1])
        print("Speed")
        print(data[25:26].hex())
        print("Direction")
        print(data[26:27].hex())
        print("Mileage")
        print(data[27:31].hex())
        print("Quantity of GPS Satellite")
        print(data[31:32].hex())
        print("Vehicle ID combined")
        print(data[32:36].hex())
        print("Device Status")
        print(data[36:37].hex())
        t_Hexbyte = int(data[36:37].hex(), 16)
        bitholder1 = ( bin(t_Hexbyte)[2:]).zfill(8)
        print(data[37:38].hex())
        t_Hexbyte = int(data[37:38].hex(), 16)
        bitholder2 = ( bin(t_Hexbyte)[2:]).zfill(8)
        process_alarm_states(bitholder2+bitholder1)
        print("Battery Percentage")
        print(int(data[38:39].hex(),16))
        print("Cell ID and LAC")
        print(data[39:43].hex())
        print("GSM signal Quality")
        print(data[43:44].hex())
        print("Geo-fence alarmID")
        print(data[44:45].hex())
        print("Reserve")
        print(data[45:48].hex())
        print("Serial Number")
        print(data[48:49].hex())


def process_alarm_states(data):
    print(data)
    #print (len(data))
    for i in range(0,16):
        check_alarm_state(i,data[i])


def check_alarm_state(item,value):

    # define the function blocks
    def motor_lock_state(value):
        if value ==1:
            print("Motor Lock")
        else:
            print("Motor Unlocked")

    def steel_string_state(value):
        if value ==1:
            print("steel String inserted")
        else:
            print("Steel String removed")

    def confirmation(value):
        if value ==1:
            print("Confirmation needed")
        else:
            print("Confirmation not needed")

    def vibration_alarm(value):
        if value ==1:
            print("vibration Detected")
        else:
            print("vibration not detected")

    def steel_string_cut(value):
        if value ==1:
            print("Tamper Alarm - String Cut")
        else:
            print("No Tamper Alarm")

    def geofence_exit(value):
        if value ==1:
            print("Geonfence Exit Alarm")
        else:
            print("No Geofence Exit Alarm")

    def geofence_entry(value):
        if value ==1:
            print("Geonfence Entry Alarm")
        else:
            print("No Geofence Entry Alarm")

    def location_source(value):
        if value ==1:
            print("location via LBS")
        else:
            print("location via GPS")

    def reserved(value):
        pass

    def motor_fault_alarm(value):
        if value ==1:
            print("Motor Fault Alarm")
        else:
            print("No Motor Fault Alarm")

    def back_cap_status(value):
        if value ==1:
            print("Back cap close")
        else:
            print("Back Cap open")

    def open_back_cap_alarm(value):
        if value ==1:
            print("Tamper - Back Cap open")
        else:
            print("No Tamper - Back Cap close")

    def low_battery_alarm(value):
        if value ==1:
            print("Low Battery Alarm")
        else:
            print("Normal Battery")

    def swipe_unauthorized_alarm(value):
        if value ==1:
            print("Tamper - UnAuthorized card swipe")
        else:
            print("No Tamper - Normal Card swipe")

    def wrong_password_alarm(value):
        if value ==1:
            print("Tamper - Wrong Password being sent from Server")
        else:
            print("No Tamper - Normal password")

    def unlocking_alarm(value):
        if value ==1:
            print("Unlocking Alarm")
        else:
            print("Normal Unlocking")

# map the inputs to the function blocks
    options = {0 : motor_lock_state,
           1 : steel_string_state,
           2 : confirmation,
           3 : vibration_alarm,
           4 : steel_string_cut,
           5 : geofence_exit,
           6 : geofence_entry,
           7 : location_source,
           8 : reserved,
           9 : motor_fault_alarm,
           10 : back_cap_status,
           11 : open_back_cap_alarm,
           12 : low_battery_alarm,
           13 : swipe_unauthorized_alarm,
           14 : wrong_password_alarm,
           15 : unlocking_alarm,

    }

    #print(value)
    options[item](int(value))


process(bytes.fromhex("2475803216921711002704031912063025059194055097853f000000000005090000000020c05a66f9107516000f0f0f1b"))
