<p align="center">
  <img height="60" src="https://mixpeek.com/static/img/logo-dark.png" alt="Mixpeek Logo">
</p>
<p align="center">
<strong><a href="https://mixpeek.com/start">Sign Up</a> | <a href="https://docs.mixpeek.com/">Documentation</a> | <a href="https://learn.mixpeek.com">Email List</a>
</strong>
</p>

<p align="center">
    <a href="https://github.com/mixpeek/server/stargazers">
        <img src="https://img.shields.io/github/stars/mixpeek/server.svg?style=flat&color=yellow" alt="Github stars"/>
    </a>
    <a href="https://github.com/mixpeek/mixpeek-python/issues">
        <img src="https://img.shields.io/github/issues/mixpeek/server.svg?style=flat&color=success" alt="GitHub issues"/>
    </a>
    <a href="https://join.slack.com/t/mixpeek/shared_invite/zt-2edc3l6t2-H8VxHFAIl0cnpqDmyFGt0A">
        <img src="https://img.shields.io/badge/slack-join-green.svg?logo=slack" alt="Join Slack"/>
    </a>
</p>

<h2 align="center">
    <b>real-time multimodal inference pipeline. set and forget.</b>
</h2>

## Overview

Mixpeek listens in on changes to your database then processes each change (`file_url` or `inline`) through an inference pipeline of: `extraction`, `generation` and `embedding` leaving your database with fresh multimodal data always.

It removes the need of setting up architecture to track database changes, extracting content, processing and embedding it then treating each change as its' own atomic unit

We support every modality: **documents, images, video, audio and of course text.**

### Integrations

- MongoDB: https://docs.mixpeek.com/integrations/mongodb

## Architecture

Mixpeek is structured into two main services, each designed to handle a specific part of the process:

- **API Orchestrator**: Coordinates the flow between services, ensuring smooth operation and handling failures gracefully.
- **Distributed Queue**:
- **Inference Service**: Extraction, embedding, and generation of payloads

These services are containerized and can be deployed on separate servers for optimal performance and scalability.

## Getting Started

Clone the Mixpeek repository and navigate to the SDK directory:

```bash
git clone git@github.com:mixpeek/server.git
cd server
```

We use poetry for all services, but there is an optional Dockerfile in each. We'll use poetry in the setup for quick deployment.

### Setup

For each service you'll do the following:

1. **Create a virtual environment**

```
poetry env use python3.10
```

2. **Activate the virtual environment**

```
poetry shell
```

3. **Install the requirements**

```
poetry install
```

#### API

.env file:

```bash
SERVICES_CONTAINER_URL=http://localhost:8001
PYTHON_VERSION=3.11.6
OPENAI_KEY=
ENCRYPTION_KEY=

REDIS_URL=

MONGO_URL=
MONGODB_ATLAS_PUBLIC_KEY=
MONGODB_ATLAS_PRIVATE_KEY=
MONGODB_ATLAS_GROUP_ID=

AWS_ACCESS_KEY=
AWS_SECRET_KEY=
AWS_REGION=
AWS_ARN_LAMBDA=

MIXPEEK_ADMIN_TOKEN=
```

Then run it:

```bash
poetry run python3 -m uvicorn main:app --reload
```

#### Inference Service

.env file:

```bash
S3_BUCKET=
AWS_ACCESS_KEY=
AWS_SECRET_KEY=
AWS_REGION=
PYTHON_VERSION=
```

```bash
poetry run python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

#### Distributed Queue

Also runs inside the api folder and uses the same .env file as `api`

```bash
celery -A db.service.celery_app worker --loglevel=info
```

You now have 3 services running !

### API Interface

All methods are exposed as HTTP endpoints.

- API swagger: https://api.mixpeek.com/docs/openapi.json
- API Documentation: https://docs.mixpeek.com
- Python SDK: https://github.com/mixpeek/mixpeek-python

You'll first need to generate an api key via POST `/user`
Use the `MIXPEEK_ADMIN_TOKEN` you defined in the api env file.

```curl
curl --location 'http://localhost:8000/users/private' \
--header 'Authorization: MIXPEEK_ADMIN_TOKEN' \
--header 'Content-Type: application/json' \
--data-raw '{"email":"ethan@mixpeek.com"}'
```

You can use any email, doesn't matter

### Cloud Service

If you want a completely managed version of Mixpeek: https://mixpeek.com/start

We also have a transparent and predictible billing model: https://mixpeek.com/pricing

#### Are we missing anything?

- Email: ethan@mixpeek.com
- Meeting: https://mixpeek.com/contact
