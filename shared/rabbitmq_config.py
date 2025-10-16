"""
Configuración centralizada de RabbitMQ para todos los microservicios
"""
import os
from typing import Dict, List, Any

# Configuración de RabbitMQ
RABBITMQ_CONFIG = {
    "url": os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/"),
    
    # Exchanges por tipo de evento 
    "exchanges": {
        "user_events": {
            "name": "user.events",
            "type": "topic",
            "durable": True,
            "description": "Eventos del microservicio de Autenticación de Usuario"
        },
        "content_events": {
            "name": "content.events", 
            "type": "topic",
            "durable": True,
            "description": "Eventos del microservicio de Gestión de Contenidos"
        },
        "collaboration_events": {
            "name": "collaboration.events",
            "type": "topic", 
            "durable": True,
            "description": "Eventos del microservicio de Colaboración de Usuarios"
        },
        "communication_events": {
            "name": "communication.events",
            "type": "topic",
            "durable": True,
            "description": "Eventos del microservicio de Comunicación de Usuarios"
        },
        "moderation_events": {
            "name": "moderation.events",
            "type": "topic",
            "durable": True,
            "description": "Eventos del microservicio de Moderación y Control de Calidad"
        }
    },
    
    # Colas específicas por evento
    "queues": {
        # Eventos de Usuario (Auth Service)
        "user_registered": {
            "name": "user.registered.queue",
            "exchange": "user.events",
            "routing_key": "user.registered",
            "durable": True
        },
        "user_updated": {
            "name": "user.updated.queue",
            "exchange": "user.events", 
            "routing_key": "user.updated",
            "durable": True
        },
        "user_deleted": {
            "name": "user.deleted.queue",
            "exchange": "user.events",
            "routing_key": "user.deleted",
            "durable": True
        },
        
        # Eventos de Contenido (Content Management)
        "content_created": {
            "name": "content.created.queue",
            "exchange": "content.events",
            "routing_key": "content.created",
            "durable": True
        },
        "content_updated": {
            "name": "content.updated.queue",
            "exchange": "content.events",
            "routing_key": "content.updated", 
            "durable": True
        },
        "content_deleted": {
            "name": "content.deleted.queue",
            "exchange": "content.events",
            "routing_key": "content.deleted",
            "durable": True
        },
        
        # Eventos de Colaboración (User Collaboration)
        "collaboration_started": {
            "name": "collaboration.started.queue",
            "exchange": "collaboration.events",
            "routing_key": "collaboration.started",
            "durable": True
        },
        "collaboration_ended": {
            "name": "collaboration.ended.queue",
            "exchange": "collaboration.events",
            "routing_key": "collaboration.ended",
            "durable": True
        },
        
        # Eventos de Comunicación (User Communication)
        "message_sent": {
            "name": "message.sent.queue",
            "exchange": "communication.events",
            "routing_key": "message.sent",
            "durable": True
        },
        "message_edited": {
            "name": "message.edited.queue",
            "exchange": "communication.events",
            "routing_key": "message.edited",
            "durable": True
        },
        
        # Eventos de Moderación (Moderation & QC)
        "moderation_review": {
            "name": "moderation.review.queue",
            "exchange": "moderation.events",
            "routing_key": "moderation.review",
            "durable": True
        },
        "moderation_approved": {
            "name": "moderation.approved.queue",
            "exchange": "moderation.events",
            "routing_key": "moderation.approved",
            "durable": True
        },
        "moderation_rejected": {
            "name": "moderation.rejected.queue",
            "exchange": "moderation.events",
            "routing_key": "moderation.rejected",
            "durable": True
        }
    },
    
    # Configuración de retry y dead letter
    "retry_config": {
        "max_retries": 3,
        "retry_delay": 1000,  # ms
        "dead_letter_exchange": "dlx",
        "dead_letter_queue": "dlq"
    },
    
    # Configuración de logging
    "logging_config": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
}

# Eventos específicos del sistema
class SystemEvents:
    """Eventos del sistema según la arquitectura"""
    
    # Auth Service Events
    USER_REGISTERED = "user.registered"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    
    # Content Management Events
    CONTENT_CREATED = "content.created"
    CONTENT_UPDATED = "content.updated"
    CONTENT_DELETED = "content.deleted"
    CONTENT_UPLOADED = "content.uploaded"
    
    # Collaboration Events
    COLLABORATION_STARTED = "collaboration.started"
    COLLABORATION_ENDED = "collaboration.ended"
    FORUM_CREATED = "forum.created"
    COMMENT_ADDED = "comment.added"
    
    # Communication Events
    MESSAGE_SENT = "message.sent"
    MESSAGE_EDITED = "message.edited"
    MESSAGE_DELETED = "message.deleted"
    CHAT_CREATED = "chat.created"
    
    # Moderation Events
    MODERATION_REVIEW = "moderation.review"
    MODERATION_APPROVED = "moderation.approved"
    MODERATION_REJECTED = "moderation.rejected"
    CONTENT_FLAGGED = "content.flagged"

# Configuración de servicios por microservicio
SERVICE_CONFIGS = {
    "auth-service": {
        "publishes": [
            SystemEvents.USER_REGISTERED,
            SystemEvents.USER_UPDATED,
            SystemEvents.USER_LOGIN,
            SystemEvents.USER_LOGOUT
        ],
        "consumes": [
            SystemEvents.MODERATION_APPROVED,
            SystemEvents.MODERATION_REJECTED
        ]
    },
    "content-service": {
        "publishes": [
            SystemEvents.CONTENT_CREATED,
            SystemEvents.CONTENT_UPDATED,
            SystemEvents.CONTENT_UPLOADED
        ],
        "consumes": [
            SystemEvents.MODERATION_APPROVED,
            SystemEvents.MODERATION_REJECTED
        ]
    },
    "collaboration-service": {
        "publishes": [
            SystemEvents.COLLABORATION_STARTED,
            SystemEvents.FORUM_CREATED,
            SystemEvents.COMMENT_ADDED
        ],
        "consumes": [
            SystemEvents.USER_REGISTERED,
            SystemEvents.MODERATION_REJECTED
        ]
    },
    "communication-service": {
        "publishes": [
            SystemEvents.MESSAGE_SENT,
            SystemEvents.CHAT_CREATED
        ],
        "consumes": [
            SystemEvents.USER_REGISTERED,
            SystemEvents.MODERATION_REJECTED
        ]
    },
    "moderation-service": {
        "publishes": [
            SystemEvents.MODERATION_REVIEW,
            SystemEvents.MODERATION_APPROVED,
            SystemEvents.MODERATION_REJECTED
        ],
        "consumes": [
            SystemEvents.CONTENT_CREATED,
            SystemEvents.MESSAGE_SENT,
            SystemEvents.COLLABORATION_STARTED
        ]
    }
}
