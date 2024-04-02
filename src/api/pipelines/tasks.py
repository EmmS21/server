from db.service import celery_app

from .service import (
    PipelineProcessor,
    PipelineTaskSyncService,
    process_orchestrator,
    PipelineAsyncService,
)

import asyncio
import json


@celery_app.task(bind=True, max_retries=2, default_retry_delay=5)
def process_pipeline(self, index_id: str, pipeline: dict, payload: dict):
    task_id = self.request.id

    # service for managing the tasks db create task
    pipeline_tasks = PipelineTaskSyncService(index_id, task_id)
    pipeline_tasks.create_one(
        {
            "pipeline_tasks": pipeline,
            "task_id": task_id,
            "payload": payload,
            "status": "PROCESSING",
        }
    )

    # remove _id because its a bson
    pipeline.pop("_id", None)

    # process the pipeline
    asyncio.run(process_orchestrator(index_id, task_id, pipeline, payload))

    # update the task status
    self.update_state(state="COMPLETED")
    pipeline_tasks.update_one({"task_id": task_id}, {"status": "COMPLETED"})
