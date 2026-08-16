import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from loguru import logger
from src.config import settings
import uuid
import sys

class StructuredLogger:
    def __init__(self, service_name: str = settings.SERVICE_NAME):
        self.service_name = service_name
        self.trace_id = str(uuid.uuid4())
        
        # Remover handler padrão
        logger.remove()
        
        # Configurar formato JSON
        if settings.LOG_FORMAT == "json":
            logger.add(
                sys.stdout,
                format=self._json_format,
                level=settings.LOG_LEVEL,
                colorize=False,
                serialize=False,
            )
        else:
            logger.add(
                sys.stdout,
                format=self._text_format,
                level=settings.LOG_LEVEL,
            )
    
    def _json_format(self, record):
        log_entry = {
            "timestamp": record["time"].isoformat(),
            "service": self.service_name,
            "level": record["level"].name,
            "trace_id": self.trace_id,
            "message": record["message"],
            "module": record["name"],
            "function": record["function"],
            "line": record["line"],
        }
        
        if record["extra"]:
            log_entry["context"] = record["extra"]
        
        if record["exception"]:
            log_entry["error"] = str(record["exception"])
        
        return json.dumps(log_entry) + "\n"
    
    def _text_format(self, record):
        return (
            f"{record['time']} | {self.service_name} | "
            f"{record['level'].name} | {record['message']}"
        )
    
    def info(self, message: str, **context):
        logger.info(message, **context)
    
    def debug(self, message: str, **context):
        logger.debug(message, **context)
    
    def warning(self, message: str, **context):
        logger.warning(message, **context)
    
    def error(self, message: str, error: Optional[Exception] = None, **context):
        if error:
            logger.error(f"{message}: {str(error)}", **context)
        else:
            logger.error(message, **context)
    
    def critical(self, message: str, error: Optional[Exception] = None, **context):
        if error:
            logger.critical(f"{message}: {str(error)}", **context)
        else:
            logger.critical(message, **context)

# Instância global
log = StructuredLogger()
