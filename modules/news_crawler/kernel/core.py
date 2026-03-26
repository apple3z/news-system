"""
CrawlerKernel - 爬虫内核核心

管理所有爬虫任务的调度和执行
单例模式，全局唯一
"""

import threading
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class TaskStatus:
    """任务状态常量"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class TriggerType:
    """触发类型常量"""
    MANUAL = "manual"
    INTERVAL = "interval"
    CRON = "cron"


class CrawlerKernel:
    """
    爬虫内核单例

    管理功能:
    - 任务 CRUD
    - 插件注册
    - 任务调度
    - 任务执行（管道编排）
    """

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if CrawlerKernel._initialized:
            return

        CrawlerKernel._initialized = True

        self._plugins: Dict[str, any] = {}
        self._scheduler = None
        self._running_tasks: Dict[int, threading.Thread] = {}
        self._kernel_initialized = False

        # 初始化调度器
        self._init_scheduler()
        # 注册默认插件
        self._register_default_plugins()
        # 初始化内核表
        self._ensure_kernel_initialized()

    def _init_scheduler(self):
        """初始化调度器"""
        from modules.news_crawler.kernel.scheduler import TaskScheduler
        self._scheduler = TaskScheduler()
        if not self._scheduler.is_running():
            self._scheduler.start()

    def _ensure_kernel_initialized(self):
        """确保内核表已初始化"""
        if self._kernel_initialized:
            return
        try:
            from modules.news_crawler.kernel.dal.task_dal import ensure_kernel_tables
            ensure_kernel_tables()
            self._kernel_initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize kernel tables: {e}")

    def _register_default_plugins(self):
        """注册默认插件"""
        try:
            from modules.news_crawler.kernel.plugins.news_plugin import NewsPlugin
            from modules.news_crawler.kernel.plugins.skills_plugin import SkillsPlugin
            from modules.news_crawler.kernel.plugins.rss_plugin import RSSPlugin

            self.register_plugin('news', NewsPlugin())
            self.register_plugin('skills', SkillsPlugin())
            self.register_plugin('rss', RSSPlugin())

            logger.info("Default plugins registered: news, skills, rss")
        except Exception as e:
            logger.error(f"Failed to register default plugins: {e}")

    def register_plugin(self, name: str, plugin):
        """注册爬虫插件"""
        self._plugins[name] = plugin
        logger.info(f"Plugin registered: {name}")

    def get_plugin(self, name: str):
        """获取插件"""
        return self._plugins.get(name)

    # ===== 任务管理 =====

    def create_task(self, task_data: dict) -> dict:
        """
        创建新任务

        Returns:
            dict: {code, message, task_id}
        """
        try:
            from modules.news_crawler.kernel.dal.task_dal import create_task

            task_id = create_task(task_data)

            # 如果是定时任务，添加到调度器
            if task_data.get('trigger_type') != TriggerType.MANUAL and task_data.get('enabled', True):
                self._schedule_task(task_id, task_data)

            logger.info(f"Task created: {task_id} - {task_data.get('name')}")
            return {'code': 200, 'message': '任务创建成功', 'task_id': task_id}
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return {'code': 500, 'message': str(e)}

    def update_task(self, task_id: int, task_data: dict) -> dict:
        """更新任务"""
        try:
            from modules.news_crawler.kernel.dal.task_dal import update_task, get_task

            # 先获取旧任务
            old_task = get_task(task_id)
            if not old_task:
                return {'code': 404, 'message': '任务不存在'}

            # 从调度器移除旧任务
            self._unschedule_task(task_id)

            # 更新任务
            update_task(task_id, task_data)

            # 如果是定时任务且启用，重新添加
            if task_data.get('trigger_type') != TriggerType.MANUAL and task_data.get('enabled', True):
                self._schedule_task(task_id, task_data)

            logger.info(f"Task updated: {task_id}")
            return {'code': 200, 'message': '任务更新成功'}
        except Exception as e:
            logger.error(f"Failed to update task: {e}")
            return {'code': 500, 'message': str(e)}

    def delete_task(self, task_id: int) -> dict:
        """删除任务"""
        try:
            from modules.news_crawler.kernel.dal.task_dal import delete_task

            self._unschedule_task(task_id)
            delete_task(task_id)

            logger.info(f"Task deleted: {task_id}")
            return {'code': 200, 'message': '任务删除成功'}
        except Exception as e:
            logger.error(f"Failed to delete task: {e}")
            return {'code': 500, 'message': str(e)}

    def get_task(self, task_id: int) -> Optional[dict]:
        """获取任务"""
        try:
            from modules.news_crawler.kernel.dal.task_dal import get_task
            return get_task(task_id)
        except Exception as e:
            logger.error(f"Failed to get task: {e}")
            return None

    def list_tasks(self, task_type: str = None, status: str = None) -> list:
        """列出任务"""
        try:
            from modules.news_crawler.kernel.dal.task_dal import list_tasks
            return list_tasks(task_type, status)
        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            return []

    def toggle_task(self, task_id: int) -> dict:
        """暂停/恢复任务"""
        try:
            from modules.news_crawler.kernel.dal.task_dal import get_task, update_task_status

            task = get_task(task_id)
            if not task:
                return {'code': 404, 'message': '任务不存在'}

            if task['status'] == TaskStatus.PAUSED:
                # 恢复
                update_task_status(task_id, TaskStatus.PENDING)
                if task.get('trigger_type') != TriggerType.MANUAL and task.get('enabled'):
                    self._scheduler.resume_job(task_id)
                return {'code': 200, 'message': '任务已恢复'}
            else:
                # 暂停
                update_task_status(task_id, TaskStatus.PAUSED)
                self._scheduler.pause_job(task_id)
                return {'code': 200, 'message': '任务已暂停'}
        except Exception as e:
            logger.error(f"Failed to toggle task: {e}")
            return {'code': 500, 'message': str(e)}

    # ===== 调度控制 =====

    def _schedule_task(self, task_id: int, task_data: dict = None):
        """将任务加入调度器"""
        if not task_data:
            task_data = self.get_task(task_id)
        if not task_data:
            return

        trigger_type = task_data.get('trigger_type')
        trigger_config = task_data.get('trigger_config', {})

        if trigger_type == TriggerType.INTERVAL:
            seconds = trigger_config.get('seconds', 3600)
            self._scheduler.add_interval_job(task_id, seconds)
        elif trigger_type == TriggerType.CRON:
            hour = trigger_config.get('hour', 9)
            minute = trigger_config.get('minute', 0)
            self._scheduler.add_cron_job(task_id, hour, minute)

    def _unschedule_task(self, task_id: int):
        """从调度器移除任务"""
        self._scheduler.remove_job(task_id)

    # ===== 任务执行 =====

    def execute_task(self, task_id: int, async_mode: bool = True) -> dict:
        """
        执行任务（对外入口）

        Args:
            task_id: 任务ID
            async_mode: True=后台线程执行，False=同步等待

        Returns:
            dict: {code, message, task_id}
        """
        task = self.get_task(task_id)
        if not task:
            return {'code': 404, 'message': '任务不存在'}

        if task['status'] == TaskStatus.RUNNING:
            return {'code': 409, 'message': '任务正在执行中'}

        if async_mode:
            thread = threading.Thread(
                target=self._execute_task,
                args=(task_id,),
                daemon=True
            )
            thread.start()
            return {'code': 200, 'message': '任务已启动', 'task_id': task_id}
        else:
            return self._execute_task(task_id)

    def _execute_task(self, task_id: int) -> dict:
        """任务执行主逻辑（内部调用）"""
        from modules.news_crawler.kernel.dal.task_dal import update_task_status
        from modules.news_crawler.kernel.dal.execution_dal import create_execution, update_execution
        from modules.news_crawler.dal.datasource_dal import list_sources
        from datetime import datetime

        task = self.get_task(task_id)
        if not task:
            return {'code': 404, 'message': '任务不存在'}

        # 更新任务状态为运行中
        update_task_status(task_id, TaskStatus.RUNNING)

        # 获取插件
        plugin = self._plugins.get(task['task_type'])
        if not plugin:
            update_task_status(task_id, TaskStatus.FAILED)
            return {'code': 500, 'message': f'未找到插件: {task["task_type"]}'}

        # 获取数据源列表
        sources = self._get_task_sources(task)

        # 汇总结果
        total_items = 0
        total_new = 0
        total_updated = 0
        errors = []

        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for source in sources:
            exec_id = create_execution(task_id, source['id'], source.get('name', ''))

            try:
                # 执行采集
                fetch_result = plugin.fetch(source, task.get('config', {}))

                if not fetch_result.success:
                    update_execution(exec_id, {
                        'status': 'failed',
                        'error_message': fetch_result.error or '采集失败'
                    })
                    errors.append({'source': source.get('name'), 'error': fetch_result.error})
                    continue

                # 解析
                if hasattr(plugin, 'parse'):
                    fetch_result = plugin.parse(fetch_result, task.get('config', {}))

                # 验证
                if hasattr(plugin, 'validate'):
                    fetch_result = plugin.validate(fetch_result, task.get('config', {}))

                # 存储
                store_result = plugin.store(fetch_result, task.get('config', {}))

                # 更新执行记录
                update_execution(exec_id, {
                    'status': 'completed',
                    'items_total': store_result.get('total', 0),
                    'items_new': store_result.get('new', 0),
                    'items_updated': store_result.get('updated', 0),
                    'detail': fetch_result.metadata or {}
                })

                total_items += store_result.get('total', 0)
                total_new += store_result.get('new', 0)
                total_updated += store_result.get('updated', 0)

            except Exception as e:
                update_execution(exec_id, {
                    'status': 'failed',
                    'error_message': str(e)
                })
                errors.append({'source': source.get('name'), 'error': str(e)})
                logger.error(f"Source {source.get('name')} failed: {e}")

        # 更新任务状态
        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        final_status = TaskStatus.COMPLETED if not errors else TaskStatus.FAILED

        update_task_status(task_id, final_status, end_time, {
            'total': total_items,
            'new': total_new,
            'updated': total_updated,
            'errors': len(errors)
        })

        return {
            'code': 200,
            'task_id': task_id,
            'status': final_status,
            'total': total_items,
            'new': total_new,
            'updated': total_updated,
            'errors': errors
        }

    def _get_task_sources(self, task: dict) -> List[dict]:
        """获取任务对应的数据源"""
        from modules.news_crawler.dal.datasource_dal import list_sources

        source_filter = task.get('source_filter', [])
        task_type = task.get('task_type')

        if source_filter:
            # 指定数据源
            all_sources = list_sources()
            return [
                s for s in all_sources
                if s['id'] in source_filter and s['status'] == 'active'
            ]
        else:
            # 全部数据源（按类型筛选）
            if task_type == 'rss':
                return list_sources(status='active')
            else:
                return list_sources(source_type=task_type, status='active')

    # ===== 状态查询 =====

    def get_running_tasks(self) -> List[dict]:
        """获取正在执行的任务"""
        from modules.news_crawler.kernel.dal.execution_dal import get_running_executions
        return get_running_executions()

    def get_task_executions(self, task_id: int, limit: int = 50) -> list:
        """获取任务的执行历史"""
        from modules.news_crawler.kernel.dal.execution_dal import get_executions_by_task
        return get_executions_by_task(task_id, limit)

    def get_recent_executions(self, limit: int = 100) -> list:
        """获取最近的执行记录"""
        from modules.news_crawler.kernel.dal.execution_dal import get_recent_executions
        return get_recent_executions(limit)

    def get_stats(self) -> dict:
        """获取统计信息"""
        from modules.news_crawler.kernel.dal.task_dal import get_task_stats
        from modules.news_crawler.kernel.dal.execution_dal import get_execution_stats

        task_stats = get_task_stats()
        exec_stats = get_execution_stats(date_from=None)
        running = self.get_running_tasks()

        return {
            'tasks': task_stats,
            'executions': exec_stats,
            'running': len(running)
        }
