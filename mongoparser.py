from pymongo import MongoClient
import bceparser


client = MongoClient()
client = MongoClient("mongodb+srv://admin:W1nd0ws87@cluster0-wkvwq.gcp.mongodb.net/test?retryWrites=true")
mydb = client["mydatabase"]
mycol = mydb["jointechraw-smoothflow"]



with client:

    docs = client.mydatabase["jointechraw-smoothflow"].find()
    print(client.mydatabase["jointechraw-smoothflow"].count_documents({}))

    for doc in docs:
        if doc:
            try:
                print ("{}".format(doc['0']))
            except:
                print("Error")
        else:
            print("Dont know")

