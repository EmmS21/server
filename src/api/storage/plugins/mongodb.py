from pydantic import BaseModel

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from _exceptions import NotFoundError

from users.model import Connection

# changes
# insert
{
    "_id": {"_data": "..."},
    "operationType": "insert",
    "clusterTime": {"$timestamp": {"t": 1711225660, "i": 1}},
    "wallTime": "2024-03-23T20:27:40.270Z",
    "fullDocument": {"_id": "65ff3b3ac3dfd5ef4fb1d2f7"},
    "ns": {"db": "use_cases", "coll": "legal_cases"},
    "documentKey": {"_id": "65ff3b3ac3dfd5ef4fb1d2f7"},
}


class MongoDBHandler:
    def __init__(self, connection_info):
        self.connection_info = Connection(**connection_info)
        self.client = None

    async def connect(self):
        try:
            connection_string = f"mongodb+srv://{self.connection_info.username}:{self.connection_info.password}@{self.connection_info.host}"
            self.client = AsyncIOMotorClient(connection_string)
            self.db = self.client[self.connection_info.database]
            return self.db
        except Exception as e:
            print("Connection Failure:", e)

    def handle_payload(self, payload):
        operation_type = payload.get("operationType")

        if operation_type == "insert":
            return payload.get("fullDocument")
        else:
            raise NotFoundError("Operation type not found for MongoDB payload.")

    async def insert(self, data):
        await self.collection.insert_one(data)

    async def delete(self, parent_id):
        await self.collection.delete_many({"parent_id": parent_id})
