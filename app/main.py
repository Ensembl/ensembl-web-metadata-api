"""
See the NOTICE file distributed with this work for additional information
regarding copyright ownership.


Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.resources.routes import router
from core.config import API_PREFIX, ALLOWED_HOSTS, VERSION, PROJECT_NAME, DEBUG

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

def get_application() -> FastAPI:
    application = FastAPI(title=PROJECT_NAME, debug=DEBUG, version=VERSION)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_HOSTS or ["*"],
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    application.include_router(router, prefix=API_PREFIX)

    return application

provider = TracerProvider(
        resource=Resource.create({SERVICE_NAME: "web-metadata-api"})
    )
tracer = trace.get_tracer(__name__)

# create a JaegerExporter
jaeger_exporter = JaegerExporter(
    # configure agent
    agent_host_name='localhost',
    agent_port=6831,
    # optional: configure also collector
    #collector_endpoint='http://localhost:16686/api/traces?format=jaeger.thrift',
    # username=xxxx, # optional
    # password=xxxx, # optional
    # max_tag_value_length=None # optional
)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)


# Create a BatchSpanProcessor and add the exporter to it
span_processor = BatchSpanProcessor(jaeger_exporter, max_export_batch_size=10)

# add to the tracer
trace.get_tracer_provider().add_span_processor(span_processor)

#processor = BatchSpanProcessor(ConsoleSpanExporter())
#provider.add_span_processor(processor)


# Creates a tracer from the global tracer provider
tracer = trace.get_tracer("web-metadata-api-tracer")

app = get_application()
FastAPIInstrumentor.instrument_app(app)