/**
 * SemanticHomeView - 语义爬虫首页
 * v2.8.0: 新增语义爬虫功能
 *
 * 功能:
 * - 快速入口：输入主题开始爬取
 * - 任务列表：历史任务卡片
 * - 统计概览
 */
const SemanticHomeView = {
    data() {
        return {
            // 新任务
            showNewModal: false,
            newQuery: '',
            newName: '',
            newConfig: {
                sources: ['duckduckgo', 'rss'],
                max_items: 100,
                relevance_threshold: 0.3
            },
            sourceOptions: [
                { value: 'duckduckgo', label: 'DuckDuckGo搜索' },
                { value: 'rss', label: 'RSS订阅源' },
                { value: 'wikipedia', label: 'Wikipedia' }
            ],

            // 任务列表
            tasks: [],
            loading: false,

            // 统计
            stats: {
                total: 0,
                running: 0,
                completed: 0
            }
        };
    },
    methods: {
        // ===== 任务操作 =====

        async loadTasks() {
            this.loading = true;
            try {
                const res = await API.get('/api/semantic/tasks');
                if (res.code === 200) {
                    this.tasks = res.data || [];
                    this.updateStats();
                }
            } catch (e) {
                console.error('加载任务失败:', e);
            } finally {
                this.loading = false;
            }
        },

        async createTask() {
            if (!this.newQuery.trim()) {
                alert('请输入要分析的主题');
                return;
            }

            const name = this.newName.trim() || this.newQuery.substring(0, 30);

            const res = await API.post('/api/semantic/tasks', {
                name: name,
                user_query: this.newQuery,
                config: this.newConfig
            });

            if (res.code === 200) {
                this.showNewModal = false;
                this.newQuery = '';
                this.newName = '';
                await this.loadTasks();

                // 跳转到详情页
                this.$router.push(`/semantic/${res.data.task_id}`);
            } else {
                alert(res.message || '创建失败');
            }
        },

        async deleteTask(task) {
            if (!confirm(`确定删除任务 "${task.name}" 吗？`)) return;

            const res = await API.del(`/api/semantic/tasks/${task.id}`);
            if (res.code === 200) {
                await this.loadTasks();
            }
        },

        async runTask(task) {
            const res = await API.post(`/api/semantic/tasks/${task.id}/run`);
            if (res.code === 200) {
                alert('任务已启动');
                this.loadTasks();
            } else {
                alert(res.message || '启动失败');
            }
        },

        viewTask(task) {
            this.$router.push(`/semantic/${task.id}`);
        },

        // ===== 工具方法 =====

        updateStats() {
            this.stats = {
                total: this.tasks.length,
                running: this.tasks.filter(t => t.status === 'running').length,
                completed: this.tasks.filter(t => t.status === 'completed').length
            };
        },

        getStatusClass(status) {
            const map = {
                'pending': 'badge-gray',
                'running': 'badge-warning',
                'completed': 'badge-success',
                'failed': 'badge-danger'
            };
            return map[status] || 'badge-gray';
        },

        formatTime(timeStr) {
            if (!timeStr) return '-';
            const d = new Date(timeStr);
            return d.toLocaleString('zh-CN');
        },

        getProgressPercent(progress) {
            return progress || 0;
        },

        toggleSource(source) {
            const idx = this.newConfig.sources.indexOf(source);
            if (idx >= 0) {
                this.newConfig.sources.splice(idx, 1);
            } else {
                this.newConfig.sources.push(source);
            }
        },

        hasSource(source) {
            return this.newConfig.sources.includes(source);
        }
    },
    mounted() {
        this.loadTasks();
    },
    template: `
    <div class="semantic-home">
        <!-- 顶部统计 -->
        <div class="stat-cards">
            <div class="stat-card">
                <div class="stat-number">{{ stats.total }}</div>
                <div class="stat-label">总任务数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number text-warning">{{ stats.running }}</div>
                <div class="stat-label">采集中</div>
            </div>
            <div class="stat-card">
                <div class="stat-number text-success">{{ stats.completed }}</div>
                <div class="stat-label">已完成</div>
            </div>
        </div>

        <!-- 操作区 -->
        <div class="action-section">
            <div class="quick-start">
                <h3>快速开始</h3>
                <p>输入一个主题，让AI自动分析相关内容</p>
                <button class="btn btn-primary btn-lg" @click="showNewModal = true">
                    + 创建语义任务
                </button>
            </div>
        </div>

        <!-- 任务列表 -->
        <div class="tasks-section">
            <h3>任务列表</h3>

            <div v-if="loading" class="loading-state">
                <div class="loading-spinner"></div>
                <p>加载中...</p>
            </div>

            <div v-else-if="tasks.length === 0" class="empty-state">
                <div class="empty-icon">🔍</div>
                <p>暂无任务，点击上方按钮创建第一个语义分析任务</p>
            </div>

            <div v-else class="task-grid">
                <div v-for="task in tasks" :key="task.id" class="task-card">
                    <div class="task-header">
                        <h4>{{ task.name }}</h4>
                        <span :class="getStatusClass(task.status)" class="status-badge">
                            {{ task.status === 'running' ? '采集中' : task.status === 'completed' ? '已完成' : task.status === 'failed' ? '失败' : '等待' }}
                        </span>
                    </div>

                    <div class="task-query">"{{ task.user_query }}"</div>

                    <!-- 进度条 -->
                    <div v-if="task.status === 'running'" class="progress-bar">
                        <div class="progress-fill" :style="{width: getProgressPercent(task.progress) + '%'}"></div>
                    </div>
                    <div class="progress-text" v-if="task.status === 'running'">
                        {{ task.progress || 0 }}% - {{ task.total_items || 0 }}条
                    </div>

                    <div class="task-meta">
                        <span v-if="task.total_items">采集: {{ task.total_items }}条</span>
                        <span v-if="task.relevant_items">相关: {{ task.relevant_items }}条</span>
                        <span>{{ formatTime(task.created_at) }}</span>
                    </div>

                    <div class="task-actions">
                        <button v-if="task.status !== 'running'" class="btn btn-sm btn-primary" @click="runTask(task)">
                            执行
                        </button>
                        <button class="btn btn-sm" @click="viewTask(task)">
                            查看
                        </button>
                        <button class="btn btn-sm btn-danger" @click="deleteTask(task)">
                            删除
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 新建任务弹窗 -->
        <modal-dialog :show="showNewModal" @close="showNewModal = false" title="创建语义任务" width="600px">
            <div class="modal-form">
                <div class="form-group">
                    <label>分析主题 *</label>
                    <textarea v-model="newQuery" placeholder="例如：最近AI大模型有什么最新进展？" rows="3"></textarea>
                </div>

                <div class="form-group">
                    <label>任务名称（可选）</label>
                    <input v-model="newName" placeholder="自动生成或手动输入">
                </div>

                <div class="form-group">
                    <label>数据来源</label>
                    <div class="source-toggles">
                        <button v-for="opt in sourceOptions"
                                :key="opt.value"
                                class="source-toggle"
                                :class="{ active: hasSource(opt.value) }"
                                @click="toggleSource(opt.value)">
                            {{ opt.label }}
                        </button>
                    </div>
                </div>

                <div class="form-group">
                    <label>最大采集量</label>
                    <input v-model.number="newConfig.max_items" type="number" min="10" max="500">
                </div>

                <div class="modal-actions">
                    <button class="btn btn-primary" @click="createTask">创建并执行</button>
                    <button class="btn btn-default" @click="showNewModal = false">取消</button>
                </div>
            </div>
        </modal-dialog>
    </div>
    `
};
