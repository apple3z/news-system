"""
TaskScheduler - 基于 APScheduler 的任务调度器

功能:
- Interval 调度（间隔执行）
- Cron 调度（定时执行）
- 持久化任务队列（SQLite）
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

logger = logging.getLogger(__name__)


class TaskScheduler:
    """
    任务调度器

    使用 APScheduler 实现，支持:
    - interval: 间隔执行（如每小时）
    - cron: 定时执行（如每天9:00）
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if TaskScheduler._initialized:
            return

        TaskScheduler._initialized = True

        self._scheduler = BackgroundScheduler(
            jobstores={'default': MemoryJobStore()},
            executors={'default': ThreadPoolExecutor(max_workers=10)},
            job_defaults={
                'coalesce': False,
                'max_instances': 1,
                'misfire_grace_time': 300
            }
        )

        self._setup_listeners()
        self._running = False

    def _setup_listeners(self):
        """设置执行监听"""
        self._scheduler.add_listener(
            self._on_job_executed,
            EVENT_JOB_EXECUTED
        )
        self._scheduler.add_listener(
            self._on_job_error,
            EVENT_JOB_ERROR
        )

    def _on_job_executed(self, event):
        """任务执行完成回调"""
        task_id = event.job.args[0] if event.job.args else None
        if task_id:
            self._log_schedule_event(task_id, 'completed',
                                     str(event.exception) if event.exception else 'success')

    def _on_job_error(self, event):
        """任务执行失败回调"""
        task_id = event.job.args[0] if event.job.args else None
        if task_id:
            self._log_schedule_event(task_id, 'failed', str(event.exception))

    def _log_schedule_event(self, task_id: int, event_type: str, message: str):
        """记录调度事件到数据库"""
        try:
            from modules.news_crawler.kernel.dal.task_dal import log_schedule_event
            log_schedule_event(task_id, event_type, message)
        except Exception as e:
            logger.warning(f"Failed to log schedule event: {e}")

    def start(self):
        """启动调度器"""
        if not self._running:
            self._scheduler.start()
            self._running = True
            logger.info("TaskScheduler started")

    def stop(self):
        """停止调度器"""
        if self._running:
            self._scheduler.shutdown(wait=False)
            self._running = False
            logger.info("TaskScheduler stopped")

    def is_running(self) -> bool:
        return self._running

    def add_interval_job(self, task_id: int, seconds: int, **kwargs):
        """添加间隔任务"""
        job_id = f"crawl_task_{task_id}"
        try:
            self._scheduler.add_job(
                func=self._execute_crawl_task,
                trigger='interval',
                seconds=seconds,
                id=job_id,
                args=[task_id],
                replace_existing=True,
                **kwargs
            )
            self._log_schedule_event(task_id, 'scheduled', f'Interval job added: every {seconds}s')
            logger.info(f"Added interval job for task {task_id}: every {seconds}s")
        except Exception as e:
            logger.error(f"Failed to add interval job: {e}")

    def add_cron_job(self, task_id: int, hour: int, minute: int, **kwargs):
        """添加定时任务"""
        job_id = f"crawl_task_{task_id}"
        try:
            self._scheduler.add_job(
                func=self._execute_crawl_task,
                trigger='cron',
                hour=hour,
                minute=minute,
                id=job_id,
                args=[task_id],
                replace_existing=True,
                **kwargs
            )
            self._log_schedule_event(task_id, 'scheduled', f'Cron job added: {hour}:{minute:02d}')
            logger.info(f"Added cron job for task {task_id}: at {hour}:{minute:02d}")
        except Exception as e:
            logger.error(f"Failed to add cron job: {e}")

    def remove_job(self, task_id: int):
        """移除任务"""
        job_id = f"crawl_task_{task_id}"
        try:
            self._scheduler.remove_job(job_id)
            self._log_schedule_event(task_id, 'unscheduled', 'Job removed')
            logger.info(f"Removed job for task {task_id}")
        except Exception as e:
            logger.warning(f"Failed to remove job {job_id}: {e}")

    def pause_job(self, task_id: int):
        """暂停任务"""
        job_id = f"crawl_task_{task_id}"
        try:
            self._scheduler.pause_job(job_id)
            self._log_schedule_event(task_id, 'paused', 'Job paused')
            logger.info(f"Paused job for task {task_id}")
        except Exception as e:
            logger.warning(f"Failed to pause job {job_id}: {e}")

    def resume_job(self, task_id: int):
        """恢复任务"""
        job_id = f"crawl_task_{task_id}"
        try:
            self._scheduler.resume_job(job_id)
            self._log_schedule_event(task_id, 'resumed', 'Job resumed')
            logger.info(f"Resumed job for task {task_id}")
        except Exception as e:
            logger.warning(f"Failed to resume job {job_id}: {e}")

    def get_jobs(self) -> list:
        """获取所有调度中的任务"""
        jobs = self._scheduler.get_jobs()
        return [{
            'id': j.id,
            'name': j.name,
            'next_run_time': str(j.next_run_time) if j.next_run_time else None
        } for j in jobs]

    @staticmethod
    def _execute_crawl_task(task_id: int):
        """执行爬虫任务的静态方法（APScheduler调用）"""
        try:
            from modules.news_crawler.kernel.core import CrawlerKernel
            kernel = CrawlerKernel()
            kernel._execute_task(task_id)
        except Exception as e:
            logger.error(f"Failed to execute task {task_id}: {e}")
