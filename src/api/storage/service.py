from pydantic import ValidationError


# from .plugins.qdrant import QdrantHandler
# from .plugins.postgres import PostgresHandler
# from .plugins.redis import RedisHandler
# from .plugins.weaviate import WeaviateHandler
# from .plugins.pinecone import PineconeHandler
# from .plugins.elasticsearch import ElasticsearchHandler
from .plugins.mongodb import MongoDBHandler


from _exceptions import StorageConnectionError


class StorageHandler:
    """
    A class used to handle storage operations.
    """

    def __init__(self, connection_info, engine):
        self.connection_info = connection_info
        self.storage_handlers = {
            "mongodb": MongoDBHandler(self.connection_info),
        }
        # Validate connection_info against the appropriate Pydantic model
        try:
            self.storage_handler = self.storage_handlers[engine]
        except ValidationError as e:
            raise StorageConnectionError(f"Invalid connection info: {e}")
        except KeyError:
            raise StorageConnectionError(f"Unsupported storage handler: {engine}")

    async def connect_to_db(self):
        try:
            return await self.storage_handler.connect()
        except Exception as e:
            print(f"Failed to connect to DB: {e}")
            return False

    async def write_to_db(self, data):
        try:
            await self.storage_handler.write(data)
            return True
        except Exception as e:
            print(f"Failed to write to DB: {e}")
            return False

    def handle_payload(self, payload):
        try:
            return self.storage_handler.handle_payload(payload)
        except Exception as e:
            print(f"Failed to handle payload: {e}")
