import json
from db.service import BaseAsyncDBService, BaseSyncDBService
from _exceptions import BadRequestError, NotFoundError
from bson import ObjectId


from users.service import UserService

from .model import PipelineCreateRequest

from parsers.service import ParseHandler
from parsers.model import ParseFileRequest

from embed.service import EmbeddingHandler
from storage.service import StorageHandler


async def process_orchestrator(
    index_id: str, task_id: str, pipeline: dict, payload: dict
):
    if pipeline["enabled"]:
        pipeline_processor = PipelineProcessor(index_id, task_id, pipeline)
        return await pipeline_processor.process(payload)


class PipelineTaskSyncService(BaseSyncDBService):
    def __init__(self, index_id, task_id):
        self.task_id = task_id
        super().__init__("pipeline_tasks", index_id)


class PipelineAsyncService(BaseAsyncDBService):
    def __init__(self, index_id):
        super().__init__("pipelines", index_id)

    async def create(self, pipeline_request):
        # grab connection_id from the pipeline_request
        user_service = UserService()
        user = user_service.get_user_by_index_id(self.index_id)

        # connection_information = user.get("connections", None)
        # if not connection_information:
        #     raise NotFoundError("Connection information found")

        print(type(user))

        # connection_information = user.get("connections", None)
        # if not connection_information:
        #     raise NotFoundError("Connection information found")

        # # make a connection request
        # storage_handler = StorageHandler(connection_information, "mongodb")
        # if not storage_handler.connect_to_db():
        #     raise BadRequestError("Failed to connect to the database")

        # new_pipeline = PipelineCreateRequest(
        #     connection=connection_information, source=pipeline_request.source
        # )

        # print(new_pipeline.model_dump())

        # return self.create_one("obj")
        return "ok"


class PipelineProcessor:
    def __init__(self, index_id, task_id, pipeline):
        self.index_id = index_id
        self.pipeline = pipeline
        self.task_id = task_id
        self.storage_handler = StorageHandler(
            connection_info=self.pipeline["connection"],
            engine=self.pipeline["connection"]["engine"],
        )

    async def connect_to_db(self):
        self.storage_client = await self.storage_handler.connect_to_db()
        if self.storage_client is None:
            raise BadRequestError("Failed to connect to the database")
        else:
            print("Connected to the database")

    def log_error_in_tasks_db(self, response):
        # this is where we log the customers db errors
        # await self.storage_client["mixpeek_errors"].insert(response)
        print(f"Insert failed: {response}")

    async def insert_into_destination(self, obj, destination):
        try:
            collection = self.storage_client[destination["collection"]]
            print("inserting into collection")
            await collection.insert_one(obj)

        except Exception as e:
            self.log_error_in_tasks_db(
                {
                    "task_id": self.task_id,
                    # "object": obj,
                    "error": str(e),
                }
            )

    async def parse_file(self, parser_request):
        parse_handler = ParseHandler()
        parse_request = ParseFileRequest(**parser_request)
        parse_response = await parse_handler.parse(parse_request)
        # need to decode because its a success response
        return json.loads(parse_response.body.decode())

    async def process_chunks(self, embedding_model, chunks, destination):
        # TODO: add support for other modalities
        embed_handler = EmbeddingHandler(modality="text", model=embedding_model)
        for chunk in chunks:
            embedding_response = await embed_handler.encode({"input": chunk["text"]})
            # need to decode because its a success response
            embedding_response_content = json.loads(embedding_response.body.decode())

            # if it failed just continue to the next one
            if not embedding_response_content.get("success"):
                await self.log_error_in_tasks_db(
                    {
                        "task_id": self.task_id,
                        "status_code": embedding_response_content["status"],
                        "error": embedding_response_content["message"],
                    }
                )
                continue

            embedding = embedding_response_content["response"]["embedding"]
            obj = {
                destination["field"]: chunk["text"],
                destination["embedding"]: embedding,
                "metadata": chunk["metadata"],
            }
            await self.insert_into_destination(obj, destination)

    async def process(self, payload):
        # connect to the db
        await self.connect_to_db()

        # normalize the client supplied payload to a common format
        prepared_payload = self.storage_handler.handle_payload(payload)

        # iterate over each source_destination mapping in the pipeline configuration
        for source_destination_mapping in self.pipeline["source_destination_mappings"]:

            # the source configuration from the pipeline
            source_configuration = source_destination_mapping["source"]

            # grab the pipeline source value from the client supplied payload
            client_payload_value = prepared_payload.get(
                source_configuration.get("name", {}), {}
            )

            # prepare the parse request
            parse_request = {
                source_configuration["type"]: client_payload_value,
                **source_configuration.get("settings", {}),
            }

            # response from the parse request
            parse_response_content = await self.parse_file(parse_request)

            # if it failed, end the process
            if not parse_response_content.get("success"):
                await self.log_error_in_tasks_db(
                    {
                        "task_id": self.task_id,
                        "status_code": parse_response_content["status"],
                        "error": parse_response_content["message"],
                    }
                )
                return None

            await self.process_chunks(
                embedding_model=source_destination_mapping["embedding_model"],
                chunks=parse_response_content["response"]["output"],
                destination=source_destination_mapping["destination"],
            )
