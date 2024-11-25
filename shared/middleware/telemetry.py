from typing import Optional, Dict, Any
import time
import logging
import psutil
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge
import opentelemetry.trace as trace
from functools import wraps

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'request_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint']
)

MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes'
)

class TelemetryMiddleware:
    """Telemetry and monitoring middleware"""
    def __init__(
        self,
        service_name: str,
        enable_tracing: bool = True,
        enable_metrics: bool = True
    ):
        self.service_name = service_name
        self.enable_tracing = enable_tracing
        self.enable_metrics = enable_metrics
        self.tracer = trace.get_tracer(__name__)

    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect system metrics"""
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count()
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "percent": psutil.disk_usage('/').percent
            }
        }
        
        # Update Prometheus memory metrics
        MEMORY_USAGE.set(psutil.virtual_memory().used)
            
        return metrics

    def instrument(self):
        """Request instrumentation decorator"""
        def decorator(func):
            @wraps(func)
            async def wrapper(request, *args, **kwargs):
                start_time = time.time()
                method = request.method
                endpoint = request.url.path
                
                # Start span if tracing is enabled
                if self.enable_tracing:
                    with self.tracer.start_as_current_span(
                        f"{method} {endpoint}"
                    ) as span:
                        span.set_attribute("http.method", method)
                        span.set_attribute("http.url", str(request.url))
                        
                        try:
                            response = await func(request, *args, **kwargs)
                            status = response.status_code
                            span.set_attribute("http.status_code", status)
                            
                        except Exception as e:
                            span.set_attribute("error", True)
                            span.set_attribute("error.message", str(e))
                            raise
                else:
                    response = await func(request, *args, **kwargs)
                    status = response.status_code
                
                # Record metrics if enabled
                if self.enable_metrics:
                    REQUEST_COUNT.labels(
                        method=method,
                        endpoint=endpoint,
                        status=status
                    ).inc()
                    
                    REQUEST_LATENCY.labels(
                        method=method,
                        endpoint=endpoint
                    ).observe(time.time() - start_time)
                    
                return response
                
            return wrapper
        return decorator 