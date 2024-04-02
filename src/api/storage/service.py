from pydantic import ValidationError
import base64


# from .plugins.qdrant import QdrantHandler
# from .plugins.postgres import PostgresHandler
# from .plugins.redis import RedisHandler
# from .plugins.weaviate import WeaviateHandler
# from .plugins.pinecone import PineconeHandler
# from .plugins.elasticsearch import ElasticsearchHandler
from .plugins.mongodb import MongoDBHandler


from users.model import Connection


from _exceptions import BadRequestError


class StorageHandler:
    """
    A class used to handle storage operations.
    """

    def __init__(self, connection_info, engine):
        # Create a dictionary mapping each storage engine to its corresponding handler, initialized with the connection info
        if isinstance(connection_info, dict):

            # convert the password from a dictionary to bytes so Connection can parse it
            password_dict = connection_info["password"]["$binary"]
            password_bytes = base64.b64decode(password_dict["base64"])
            connection_info["password"] = password_bytes

            self.connection_info = Connection(**connection_info)
        else:
            self.connection_info = connection_info

        self.client = None
        self.storage_handlers = {
            "mongodb": MongoDBHandler(self.connection_info),
        }
        # Validate connection_info against the appropriate Pydantic model
        try:
            self.storage_handler = self.storage_handlers[engine]
        except ValidationError as e:
            raise BadRequestError(f"Invalid connection info: {e}")
        except KeyError:
            raise BadRequestError(f"Unsupported storage handler: {engine}")

    async def connect_to_db(self):
        try:
            # now we have a self.db attribute that we can use to interact with the database
            self.client = await self.storage_handler.connect()
        except Exception as e:
            raise BadRequestError(f"Failed to connect to the database: {e}")

    def handle_payload(self, payload):
        try:
            return self.storage_handler.handle_payload(payload)
        except Exception as e:
            raise BadRequestError(f"Failed to handle payload: {e}")
