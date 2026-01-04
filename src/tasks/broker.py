import taskiq_fastapi
from taskiq import SmartRetryMiddleware, TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import ListQueueBroker

from src.config import settings

broker = ListQueueBroker(settings.redis.REDIS_URL).with_middlewares(
    SmartRetryMiddleware(
        default_retry_count=settings.taskiq.DEFAULT_RETRY_COUNT,
        default_delay=settings.taskiq.DEFAULT_DELAY,
        use_jitter=settings.taskiq.USE_JITTER,
        use_delay_exponent=settings.taskiq.USE_DELAY_EXPONENT,
        max_delay_exponent=settings.taskiq.MAX_DELAY_EXPONENT,
    ),
)

taskiq_fastapi.init(broker=broker, app_or_path="src.main:app")
scheduler = TaskiqScheduler(broker=broker, sources=[LabelScheduleSource(broker)])
