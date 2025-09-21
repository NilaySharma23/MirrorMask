import pymongo
import os
from dotenv import load_dotenv

load_dotenv()
client = pymongo.MongoClient(os.getenv("MONGODB_URI"))
db = client["mirrormask_db"]
print(list(db["audits"].find({}, {"_id": 0})))