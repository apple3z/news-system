/**
 * CrawlerKernelView - 爬虫内核管理界面
 * v2.7.0: 新增爬虫内核管理界面
 *
 * 功能:
 * - 任务管理（创建/编辑/删除/执行）
 * - 实时监控（执行状态/进度）
 * - 执行日志（历史记录/错误查看）
 */
const CrawlerKernelView = {
    data() {
        return {
            // 任务相关
            tasks: [],
            showTaskModal: false,
            editMode: false,
            taskForm: {
                id: null,
                name: '',
                task_type: 'news',
                trigger_type: 'interval',
                trigger_config: { seconds: 3600 },
                source_filter: [],
                pipeline: ['fetch', 'parse', 'store'],
                config: {},
                enabled: true
            },

            // 监控相关
            runningTasks: [],
            stats: {
                tasks: { total: 0, active: 0, pending: 0, completed_today: 0, failed_today: 0 },
                executions: { total: 0, completed: 0, failed: 0, items_total: 0, items_new: 0 }
            },
            recentExecutions: [],
            refreshTimer: null,

            // 活跃Tab
            activeTab: 'tasks',

            // 选项
            taskTypeOptions: [
                { value: 'news', label: '新闻采集' },
                { value: 'skills', label: 'Skills同步' },
                { value: 'rss', label: 'RSS订阅' }
            ],
            triggerTypeOptions: [
                { value: 'manual', label: '手动执行' },
                { value: 'interval', label: '间隔执行' },
                { value: 'cron', label: '定时执行' }
            ],
            pipelineOptions: [
                { value: 'fetch', label: '采集' },
                { value: 'parse', label: '解析' },
                { value: 'store', label: '存储' }
            ],

            // 加载状态
            loading: false
        };
    },
    methods: {
        // ===== 任务管理 =====

        async loadTasks() {
            try {
                const res = await API.get('/api/admin/kernel/tasks');
                if (res.code === 200) {
                    this.tasks = res.data || [];
                }
            } catch (e) {
                console.error('加载任务失败:', e);
            }
        },

        openCreate() {
            this.editMode = false;
            this.taskForm = {
                id: null,
                name: '',
                task_type: 'news',
                trigger_type: 'interval',
                trigger_config: { seconds: 3600 },
                source_filter: [],
                pipeline: ['fetch', 'parse', 'store'],
                config: {},
                enabled: true
            };
            this.showTaskModal = true;
        },

        openEdit(task) {
            this.editMode = true;
            this.taskForm = {
                ...task,
                trigger_config: task.trigger_config || { seconds: 3600 }
            };
            this.showTaskModal = true;
        },

        async saveTask() {
            if (!this.taskForm.name) {
                alert('请输入任务名称');
                return;
            }

            let res;
            if (this.editMode) {
                res = await API.put('/api/admin/kernel/tasks/' + this.taskForm.id, this.taskForm);
            } else {
                res = await API.post('/api/admin/kernel/tasks', this.taskForm);
            }

            if (res.code === 200) {
                this.showTaskModal = false;
                this.loadTasks();
                this.loadStatus();
            } else {
                alert(res.message || '保存失败');
            }
        },

        async deleteTask(task) {
            if (!confirm(`确定删除任务 "${task.name}" 吗？`)) return;

            const res = await API.del('/api/admin/kernel/tasks/' + task.id);
            if (res.code === 200) {
                this.loadTasks();
            } else {
                alert(res.message || '删除失败');
            }
        },

        async toggleTask(task) {
            const res = await API.put('/api/admin/kernel/tasks/' + task.id + '/toggle');
            if (res.code === 200) {
                this.loadTasks();
                this.loadStatus();
            }
        },

        async runTask(task) {
            if (!confirm(`确定执行任务 "${task.name}" 吗？`)) return;

            this.loading = true;
            const res = await API.post('/api/admin/kernel/tasks/' + task.id + '/run');
            this.loading = false;

            if (res.code === 200) {
                alert('任务已启动');
                this.loadTasks();
                this.loadStatus();
            } else {
                alert(res.message || '启动失败');
            }
        },

        // ===== 状态监控 =====

        async loadStatus() {
            try {
                const res = await API.get('/api/admin/kernel/status');
                if (res.code === 200) {
                    this.stats = res.data.stats || this.stats;
                    this.runningTasks = res.data.running || [];
                }
            } catch (e) {
                console.error('加载状态失败:', e);
            }
        },

        async loadExecutions() {
            try {
                const res = await API.get('/api/admin/kernel/executions?limit=50');
                if (res.code === 200) {
                    this.recentExecutions = res.data || [];
                }
            } catch (e) {
                console.error('加载执行记录失败:', e);
            }
        },

        // ===== 工具方法 =====

        getTriggerLabel(task) {
            if (task.trigger_type === 'manual') return '手动';
            if (task.trigger_type === 'interval') {
                const seconds = task.trigger_config?.seconds || 3600;
                if (seconds >= 3600) return `每${Math.round(seconds/3600)}小时`;
                if (seconds >= 60) return `每${Math.round(seconds/60)}分钟`;
                return `每${seconds}秒`;
            }
            if (task.trigger_type === 'cron') {
                const cfg = task.trigger_config || {};
                return `每天 ${cfg.hour || 9}:${String(cfg.minute || 0).padStart(2, '0')}`;
            }
            return task.trigger_type;
        },

        getStatusClass(status) {
            const map = {
                'pending': 'badge-gray',
                'running': 'badge-warning',
                'completed': 'badge-success',
                'failed': 'badge-danger',
                'paused': 'badge-gray'
            };
            return map[status] || 'badge-gray';
        },

        formatTime(timeStr) {
            if (!timeStr) return '-';
            const d = new Date(timeStr);
            return d.toLocaleString('zh-CN');
        },

        startRefresh() {
            this.refreshTimer = setInterval(() => {
                if (this.activeTab === 'monitor') {
                    this.loadStatus();
                    this.loadExecutions();
                }
            }, 5000);
        },

        stopRefresh() {
            if (this.refreshTimer) {
                clearInterval(this.refreshTimer);
                this.refreshTimer = null;
            }
        }
    },
    mounted() {
        this.loadTasks();
        this.loadStatus();
        this.startRefresh();
    },
    beforeUnmount() {
        this.stopRefresh();
    },
    template: `
    <div class="kernel-view">
        <!-- Tab 导航 -->
        <div class="inner-tabs">
            <button class="tab-btn" :class="{ active: activeTab === 'tasks' }" @click="activeTab = 'tasks'">任务管理</button>
            <button class="tab-btn" :class="{ active: activeTab === 'monitor' }" @click="activeTab = 'monitor'; loadStatus(); loadExecutions();">实时监控</button>
            <button class="tab-btn" :class="{ active: activeTab === 'logs' }" @click="activeTab = 'logs'; loadExecutions();">执行日志</button>
        </div>

        <!-- 任务管理 Tab -->
        <div v-show="activeTab === 'tasks'" class="tab-content">
            <div class="page-header">
                <h3>爬虫任务</h3>
                <button class="btn btn-primary" @click="openCreate">+ 新建任务</button>
            </div>

            <table class="admin-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>任务名称</th>
                        <th>类型</th>
                        <th>触发方式</th>
                        <th>状态</th>
                        <th>上次执行</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="task in tasks" :key="task.id">
                        <td>{{ task.id }}</td>
                        <td>{{ task.name }}</td>
                        <td>{{ taskTypeOptions.find(t => t.value === task.task_type)?.label || task.task_type }}</td>
                        <td>{{ getTriggerLabel(task) }}</td>
                        <td>
                            <span :class="getStatusClass(task.status)" @click="toggleTask(task)" style="cursor:pointer" :title="'点击切换状态'">
                                {{ task.status }}
                            </span>
                        </td>
                        <td>{{ task.last_run_time ? formatTime(task.last_run_time) : '从未执行' }}</td>
                        <td class="actions">
                            <a href="#" @click.prevent="runTask(task)">执行</a>
                            <a href="#" @click.prevent="openEdit(task)">编辑</a>
                            <a href="#" @click.prevent="deleteTask(task)" class="text-danger">删除</a>
                        </td>
                    </tr>
                    <tr v-if="tasks.length === 0">
                        <td colspan="7" class="empty-cell">暂无任务</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 实时监控 Tab -->
        <div v-show="activeTab === 'monitor'" class="tab-content">
            <div class="page-header">
                <h3>实时监控</h3>
                <button class="btn btn-default btn-sm" @click="loadStatus(); loadExecutions();">刷新</button>
            </div>

            <!-- 统计卡片 -->
            <div class="stat-cards">
                <div class="stat-card">
                    <div class="stat-number">{{ stats.tasks.total || 0 }}</div>
                    <div class="stat-label">总任务数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ stats.tasks.active || 0 }}</div>
                    <div class="stat-label">执行中</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ stats.tasks.completed_today || 0 }}</div>
                    <div class="stat-label">今日完成</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ stats.tasks.failed_today || 0 }}</div>
                    <div class="stat-label">今日失败</div>
                </div>
            </div>

            <!-- 正在执行 -->
            <div v-if="runningTasks.length > 0" class="section">
                <h4>正在执行</h4>
                <div class="running-list">
                    <div v-for="task in runningTasks" :key="task.id" class="running-item">
                        <span class="badge badge-warning">执行中</span>
                        <span>{{ task.task_name }}</span>
                        <span class="text-muted">- {{ task.source_name }}</span>
                    </div>
                </div>
            </div>

            <!-- 最近执行记录 -->
            <div class="section">
                <h4>最近执行</h4>
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th>时间</th>
                            <th>任务</th>
                            <th>数据源</th>
                            <th>状态</th>
                            <th>采集量</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="exec in recentExecutions.slice(0, 10)" :key="exec.id">
                            <td>{{ formatTime(exec.start_time) }}</td>
                            <td>{{ exec.task_name || exec.task_id }}</td>
                            <td>{{ exec.source_name }}</td>
                            <td><span :class="getStatusClass(exec.status)">{{ exec.status }}</span></td>
                            <td>{{ exec.items_new || 0 }} 新 / {{ exec.items_updated || 0 }} 更新</td>
                        </tr>
                        <tr v-if="recentExecutions.length === 0">
                            <td colspan="5" class="empty-cell">暂无执行记录</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 执行日志 Tab -->
        <div v-show="activeTab === 'logs'" class="tab-content">
            <div class="page-header">
                <h3>执行日志</h3>
                <button class="btn btn-default btn-sm" @click="loadExecutions();">刷新</button>
            </div>

            <table class="admin-table">
                <thead>
                    <tr>
                        <th>时间</th>
                        <th>任务ID</th>
                        <th>数据源</th>
                        <th>状态</th>
                        <th>采集量</th>
                        <th>错误信息</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="exec in recentExecutions" :key="exec.id">
                        <td>{{ formatTime(exec.start_time) }}</td>
                        <td>{{ exec.task_id }}</td>
                        <td>{{ exec.source_name }}</td>
                        <td><span :class="getStatusClass(exec.status)">{{ exec.status }}</span></td>
                        <td>{{ exec.items_new || 0 }} 新 / {{ exec.items_updated || 0 }} 更新</td>
                        <td class="text-danger">{{ exec.error_message || '-' }}</td>
                    </tr>
                    <tr v-if="recentExecutions.length === 0">
                        <td colspan="6" class="empty-cell">暂无执行记录</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 任务编辑弹窗 -->
        <modal-dialog :show="showTaskModal" @close="showTaskModal = false" :title="editMode ? '编辑任务' : '新建任务'" width="600px">
            <div class="modal-form">
                <div class="form-group">
                    <label>任务名称</label>
                    <input v-model="taskForm.name" placeholder="输入任务名称">
                </div>

                <div class="form-group">
                    <label>任务类型</label>
                    <select v-model="taskForm.task_type">
                        <option v-for="opt in taskTypeOptions" :key="opt.value" :value="opt.value">
                            {{ opt.label }}
                        </option>
                    </select>
                </div>

                <div class="form-group">
                    <label>触发方式</label>
                    <select v-model="taskForm.trigger_type">
                        <option v-for="opt in triggerTypeOptions" :key="opt.value" :value="opt.value">
                            {{ opt.label }}
                        </option>
                    </select>
                </div>

                <!-- 间隔配置 -->
                <div class="form-group" v-if="taskForm.trigger_type === 'interval'">
                    <label>执行间隔（秒）</label>
                    <input v-model.number="taskForm.trigger_config.seconds" type="number" min="60" step="60">
                    <small class="form-text">最小60秒</small>
                </div>

                <!-- Cron配置 -->
                <div class="form-group" v-if="taskForm.trigger_type === 'cron'">
                    <label>执行时间</label>
                    <div class="cron-inputs">
                        <input v-model.number="taskForm.trigger_config.hour" type="number" min="0" max="23" placeholder="时">
                        <span>:</span>
                        <input v-model.number="taskForm.trigger_config.minute" type="number" min="0" max="59" placeholder="分">
                    </div>
                    <small class="form-text">每天在指定时间执行</small>
                </div>

                <div class="form-group">
                    <label>处理管道</label>
                    <div class="checkbox-group">
                        <label v-for="opt in pipelineOptions" :key="opt.value">
                            <input type="checkbox" :value="opt.value" v-model="taskForm.pipeline">
                            {{ opt.label }}
                        </label>
                    </div>
                </div>

                <div class="form-group">
                    <label>
                        <input type="checkbox" v-model="taskForm.enabled">
                        启用调度
                    </label>
                </div>

                <div class="modal-actions">
                    <button class="btn btn-primary" @click="saveTask">保存</button>
                    <button class="btn btn-default" @click="showTaskModal = false">取消</button>
                </div>
            </div>
        </modal-dialog>
    </div>
    `
};
