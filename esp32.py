from pymongo import MongoClient

client = MongoClient()
client = MongoClient("mongodb+srv://admin:W1nd0ws87@cluster0-wkvwq.gcp.mongodb.net/test?retryWrites=true")
mydb = client["mydatabase"]
mycol = mydb["jointechraw-smoothflow"]



def process_data(data):
    try:

        print("------------------------------------------------")

        print(data.hex())


    except:
        print("Error")



def process_ack(data):
    #checking if it is a lock or unlock

    return 0


def process(data):

   process_data(data)



