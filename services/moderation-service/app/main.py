from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from app.moderation import moderate_text
from shared.rabbitmq_client import create_rabbitmq_client, EventPublisher
from shared.rabbitmq_config import SystemEvents

app = FastAPI(title="Moderation Service", version="1.0.0")

# Initialize Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# RabbitMQ global client
rabbitmq_client = None
event_publisher = None

@app.get("/api/moderation/health")
async def health():
    return {"status": "ok"}


@app.on_event("startup")
async def on_startup():
    """Connect to RabbitMQ on startup"""
    global rabbitmq_client, event_publisher
    
    # Connect to RabbitMQ (with error handling)
    try:
        rabbitmq_client = create_rabbitmq_client("moderation-service")
        await rabbitmq_client.connect()
        event_publisher = EventPublisher(rabbitmq_client)
        
        # Subscribe to content and collaboration events for automatic moderation
        await rabbitmq_client.consume_events(
            [
                SystemEvents.CONTENT_CREATED,
                SystemEvents.COLLABORATION_STARTED,
                "collaboration.thread_created",
                "collaboration.comment_created"
            ],
            handle_content_event
        )
        print("Moderation service connected to RabbitMQ")
    except Exception as e:
        print(f"Warning: Could not connect to RabbitMQ: {e}")
        print("Service will continue without async events")
        rabbitmq_client = None
        event_publisher = None


@app.on_event("shutdown")
async def on_shutdown():
    """Disconnect from RabbitMQ"""
    global rabbitmq_client
    
    if rabbitmq_client:
        await rabbitmq_client.disconnect()


async def handle_content_event(event_type: str, event_data: dict):
    """Handle content/collaboration events for automatic moderation"""
    print(f"Moderation Service received event: {event_type}")
    data = event_data.get('data', {})
    print(f"Data: {data}")
    
    # TODO: Implement automatic moderation logic
    # For now, auto-approve everything
    global event_publisher
    if event_publisher:
        await event_publisher.publish_event(
            "moderation.approved",
            {
                "original_event": event_type,
                "content_id": data.get("material_id") or data.get("thread_id") or data.get("comment_id"),
                "action": "auto_approved"
            }
        )


@app.post("/api/moderation/text")
async def moderate_input(text: str = Form(...)):
    result = moderate_text(text)
    
    # Publish moderation result event
    global event_publisher
    if event_publisher:
        event_type = "moderation.approved" if result.get("approved", False) else "moderation.rejected"
        await event_publisher.publish_event(
            event_type,
            {
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
                "result": result,
                "action": "text_moderated"
            }
        )
    
    return JSONResponse(content=result)

@app.post("/api/moderation/file")
async def moderate_file(file: UploadFile = File(...)):
    content = (await file.read()).decode("utf-8", errors="ignore")
    result = moderate_text(content)
    
    # Publish moderation result event
    global event_publisher
    if event_publisher:
        event_type = "moderation.approved" if result.get("approved", False) else "moderation.rejected"
        await event_publisher.publish_event(
            event_type,
            {
                "filename": file.filename,
                "result": result,
                "action": "file_moderated"
            }
        )
    
    return JSONResponse(content=result)
