```bash
taskiq scheduler src.tasks.broker:scheduler src.tasks.schedule
taskiq worker src.tasks.broker:broker src.tasks.worker src.tasks.schedule --workers 1
```