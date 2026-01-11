
import logging
import time
import functools
import uuid
from typing import Optional, Callable, Any
from contextlib import contextmanager
from contextvars import ContextVar

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("performance")
if not logger.handlers:
    # Ensure performance logs are output if not already configured
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - [PERF] %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Context var to store request ID for correlation
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="system")

def get_request_id() -> str:
    return request_id_ctx.get()

class RequestTimeMiddleware(BaseHTTPMiddleware):
    """Middleware to log total request time and inject request ID."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        req_id = str(uuid.uuid4())[:8]
        token = request_id_ctx.set(req_id)
        
        start_time = time.perf_counter()
        logger.info(f"[{req_id}] START {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            
            process_time = time.perf_counter() - start_time
            logger.info(f"[{req_id}] END {request.method} {request.url.path} - took {process_time:.3f}s")
            
            response.headers["X-Request-ID"] = req_id
            response.headers["X-Process-Time"] = str(process_time)
            return response
            
        except Exception as e:
            process_time = time.perf_counter() - start_time
            logger.error(f"[{req_id}] ERROR {request.method} {request.url.path} - took {process_time:.3f}s: {e}")
            raise
        finally:
            request_id_ctx.reset(token)

def timed_operation(name: Optional[str] = None):
    """Decorator to measure execution time of a function."""
    def decorator(func: Callable):
        op_name = name or func.__name__
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            req_id = get_request_id()
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                elapsed = time.perf_counter() - start
                logger.info(f"[{req_id}] Op '{op_name}' took {elapsed:.3f}s")
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            req_id = get_request_id()
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed = time.perf_counter() - start
                logger.info(f"[{req_id}] Op '{op_name}' took {elapsed:.3f}s")

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator

@contextmanager
def measure_time(operation_name: str):
    """Context manager to measure execution time of a block."""
    req_id = get_request_id()
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.info(f"[{req_id}] Block '{operation_name}' took {elapsed:.3f}s")

import asyncio
