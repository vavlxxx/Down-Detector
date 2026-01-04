import taskiq_fastapi
from taskiq import SmartRetryMiddleware, TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import ListQueueBroker

broker = ListQueueBroker("redis://localhost:7379/0").with_middlewares(
    SmartRetryMiddleware(
        default_retry_count=1,
        default_delay=10,
        use_jitter=True,
        use_delay_exponent=True,
        max_delay_exponent=120,
    ),
)

taskiq_fastapi.init(broker=broker, app_or_path="src.main:app")
scheduler = TaskiqScheduler(broker=broker, sources=[LabelScheduleSource(broker)])
