import json
from db.service import BaseAsyncDBService, BaseSyncDBService
from _exceptions import BadRequestError, NotFoundError, InternalServerError
from bson import ObjectId

from users.service import UserService

from .model import Pipeline, SourceDestinationMapping

from extract.service import ExtractHandler
from extract.model import ExtractRequest
from embed.model import EmbeddingRequest

from embed.service import EmbeddingHandler
from storage.service import StorageHandler


async def process_orchestrator(
    index_id: str, task_id: str, pipeline: dict, payload: dict
):
    if pipeline["enabled"]:
        pipeline_processor = PipelineProcessor(index_id, task_id, pipeline)
        return await pipeline_processor.process(payload)
    else:
        raise BadRequestError(
            {"error": f"pipeline_id: {pipeline['pipeline_id']} is disabled"}
        )


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

        if user is None or not user.connections or len(user.connections) == 0:
            raise NotFoundError({"error": "Connection information not found"})

        connection_information = user.connections[0]

        # make a connection request
        storage_handler = StorageHandler(connection_information, "mongodb")
        await storage_handler.connect_to_db()

        new_pipeline = Pipeline(
            connection=connection_information,
            source_destination_mappings=pipeline_request.source_destination_mappings,
            metadata=pipeline_request.metadata,
        )

        obj = new_pipeline.model_dump()

        await self.create_one(obj)

        return obj


class PipelineProcessor:
    def __init__(self, index_id, task_id, pipeline):
        self.index_id = index_id
        self.pipeline = pipeline
        self.task_id = task_id

        self.storage_handler = StorageHandler(
            connection_info=self.pipeline["connection"],
            engine=self.pipeline["connection"]["engine"],
        )
        self.pipeline_tasks = PipelineTaskSyncService(index_id, task_id)

    async def connect_to_storage(self):
        await self.storage_handler.connect_to_db()

        if self.storage_handler.client is None:
            raise BadRequestError({"error": "Failed to connect to the database"})

        print("Connected to the database!")

    def log_error_in_tasks_db(self, error: InternalServerError):
        error_dict = {
            "task_id": self.task_id,
            "status_code": error.status,
            "error": error.error.get("message", ""),
        }
        # rest of your code
        print(f"Insert failed: {error.error.get('message', '')}")
        self.pipeline_tasks.update_one(
            {"task_id": self.task_id}, {"status": "FAILURE", "error": error_dict}
        )

    async def insert_into_destination(self, obj, destination):
        try:
            if self.storage_handler.client is not None:
                collection = self.storage_handler.client[destination["collection"]]
                print("inserting into collection")
                await collection.insert_one(obj)
            else:
                raise Exception("Storage handler client is not available.")

        except Exception as e:
            error = InternalServerError({"message": str(e)})
            self.log_error_in_tasks_db(error)

    async def parse_file(self, parser_request):
        parse_handler = ExtractHandler()
        parse_request = ExtractRequest(**parser_request)
        parse_response = await parse_handler.parse(parse_request)
        # need to decode because its a success response
        return parse_response

    async def process_chunks(self, embedding_model, chunks, destination, parent_id):
        # TODO: add support for other modalities
        embed_handler = EmbeddingHandler()

        # iterate over each chunk and embed the text
        for chunk in chunks:

            try:
                embedding_response = await embed_handler.encode(
                    EmbeddingRequest(input=chunk["text"], model=embedding_model)
                )
            except Exception as e:
                error = InternalServerError({"message": embedding_response["message"]})
                self.log_error_in_tasks_db(error)
                continue

            embedding = embedding_response["embedding"]
            obj = {
                destination["field"]: chunk["text"],
                destination["embedding"]: embedding,
                "metadata": chunk["metadata"],
                "parent_id": parent_id,
            }
            await self.insert_into_destination(obj, destination)

    async def process(self, payload):
        # connect to the DB defined in the pipeline configuration
        await self.connect_to_storage()

        # normalize the client supplied payload to a common format
        prepared_payload = self.storage_handler.handle_payload(payload)

        # iterate over each source_destination mapping in the pipeline configuration
        for mapping in self.pipeline["source_destination_mappings"]:

            # the source configuration from the pipeline
            source_configuration = mapping["source"]

            # grab the pipeline source value from the client supplied payload
            client_payload_value = prepared_payload.get(source_configuration["field"])

            # prepare the parse request
            parse_request = {
                source_configuration["type"]: client_payload_value,
                **source_configuration["settings"],
            }

            # response from the parse request
            try:
                parse_response = await self.parse_file(parse_request)
            except Exception as e:
                error = InternalServerError({"message": str(e)})
                self.log_error_in_tasks_db(error)
                return None

            await self.process_chunks(
                embedding_model=mapping["embedding_model"],
                # Prepare the chunks for processing. If the output from the parse request is a string,
                # convert it into a list. If it's already a list, use it as is.
                chunks=(
                    [parse_response["output"]]
                    if isinstance(parse_response["output"], str)
                    else parse_response["output"]
                ),
                destination=mapping["destination"],
                parent_id=prepared_payload["parent_id"],
            )
