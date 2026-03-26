/**
 * SemanticDetailView - 语义爬虫任务详情页
 * v2.8.0: 新增语义爬虫功能
 *
 * 功能:
 * - 任务状态（进度条）
 * - 词云展示
 * - 热度趋势图
 * - 相关内容列表
 */
const SemanticDetailView = {
    data() {
        return {
            taskId: null,
            task: null,
            results: null,
            sources: [],
            items: [],
            loading: false,
            refreshTimer: null,
            activeTab: 'overview'
        };
    },
    computed: {
        isRunning() {
            return this.task && this.task.status === 'running';
        }
    },
    methods: {
        // ===== 数据加载 =====

        async loadData() {
            this.loading = true;
            try {
                await Promise.all([
                    this.loadTask(),
                    this.loadResults(),
                    this.loadSources(),
                    this.loadItems()
                ]);
            } catch (e) {
                console.error('加载数据失败:', e);
            } finally {
                this.loading = false;
            }
        },

        async loadTask() {
            const res = await API.get(`/api/semantic/tasks/${this.taskId}`);
            if (res.code === 200) {
                this.task = res.data;
            }
        },

        async loadResults() {
            const res = await API.get(`/api/semantic/tasks/${this.taskId}/results`);
            if (res.code === 200) {
                this.results = res.data;
                this.renderTrendChart();
                this.renderWordCloud();
            }
        },

        async loadSources() {
            const res = await API.get(`/api/semantic/tasks/${this.taskId}/sources`);
            if (res.code === 200) {
                this.sources = res.data || [];
            }
        },

        async loadItems() {
            const res = await API.get(`/api/semantic/tasks/${this.taskId}/items?min_relevance=0.3&limit=50`);
            if (res.code === 200) {
                this.items = res.data || [];
            }
        },

        // ===== 图表渲染 =====

        renderTrendChart() {
            if (!this.results || !this.results.trend) return;

            const trend = this.results.trend;
            const ctx = document.getElementById('trendChart');
            if (!ctx) return;

            // 销毁旧图表
            if (this.trendChart) {
                this.trendChart.destroy();
            }

            // 准备数据
            const labels = (trend.dates || []).map(d => {
                const date = new Date(d);
                return `${date.getMonth() + 1}/${date.getDate()}`;
            });
            const data = trend.counts || [];

            // 创建图表
            this.trendChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: '内容量',
                        data: data,
                        borderColor: '#00d2ff',
                        backgroundColor: 'rgba(0, 210, 255, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        },

        renderWordCloud() {
            if (!this.results || !this.results.wordcloud) return;

            const wordcloud = this.results.wordcloud;
            const container = document.getElementById('wordcloudContainer');
            if (!container) return;

            // 清空容器
            container.innerHTML = '';

            // 创建词云文字
            const words = wordcloud.words || [];
            words.forEach(item => {
                const span = document.createElement('span');
                span.textContent = item.text;
                span.className = 'wordcloud-word';
                span.style.fontSize = `${Math.min(item.size || 20, 48)}px`;
                span.style.opacity = 0.5 + (item.size / 72) * 0.5;
                span.onclick = () => {
                    this.$router.push(`/semantic?keyword=${item.text}`);
                };
                container.appendChild(span);
            });
        },

        // ===== 轮询 =====

        startPolling() {
            this.refreshTimer = setInterval(async () => {
                await this.loadTask();
                if (this.task && this.task.status !== 'running') {
                    clearInterval(this.refreshTimer);
                    await this.loadResults();
                    await this.loadSources();
                    await this.loadItems();
                }
            }, 3000);
        },

        stopPolling() {
            if (this.refreshTimer) {
                clearInterval(this.refreshTimer);
                this.refreshTimer = null;
            }
        },

        // ===== 工具方法 =====

        formatTime(timeStr) {
            if (!timeStr) return '-';
            const d = new Date(timeStr);
            return d.toLocaleString('zh-CN');
        },

        goBack() {
            this.$router.push('/semantic');
        }
    },
    mounted() {
        this.taskId = parseInt(this.$route.params.id);
        if (!this.taskId) {
            this.goBack();
            return;
        }
        this.loadData();
        this.startPolling();
    },
    beforeUnmount() {
        this.stopPolling();
        if (this.trendChart) {
            this.trendChart.destroy();
        }
    },
    template: `
    <div class="semantic-detail">
        <!-- 顶部导航 -->
        <div class="detail-header">
            <button class="btn btn-back" @click="goBack">← 返回</button>
            <h2>{{ task ? task.name : '加载中...' }}</h2>
            <span v-if="task" :class="'status-' + task.status">
                {{ task.status === 'running' ? '采集中' : task.status === 'completed' ? '已完成' : task.status === 'failed' ? '失败' : '等待' }}
            </span>
        </div>

        <div v-if="loading && !task" class="loading-state">
            <div class="loading-spinner"></div>
            <p>加载中...</p>
        </div>

        <template v-else-if="task">
            <!-- 任务信息卡片 -->
            <div class="info-card">
                <div class="info-query">
                    <label>查询:</label>
                    <p>"{{ task.user_query }}"</p>
                </div>

                <!-- 进度条 -->
                <div v-if="isRunning" class="progress-section">
                    <div class="progress-bar">
                        <div class="progress-fill" :style="{width: (task.progress || 0) + '%'}"></div>
                    </div>
                    <div class="progress-info">
                        <span>{{ task.progress || 0 }}%</span>
                        <span>{{ task.total_items || 0 }} 条采集</span>
                    </div>
                </div>

                <div class="info-stats">
                    <div class="stat">
                        <span class="stat-value">{{ task.total_items || 0 }}</span>
                        <span class="stat-label">总采集</span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">{{ task.relevant_items || 0 }}</span>
                        <span class="stat-label">相关内容</span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">{{ sources.length }}</span>
                        <span class="stat-label">数据源</span>
                    </div>
                </div>
            </div>

            <!-- Tab 切换 -->
            <div class="inner-tabs">
                <button class="tab-btn" :class="{ active: activeTab === 'overview' }" @click="activeTab = 'overview'">总览</button>
                <button class="tab-btn" :class="{ active: activeTab === 'wordcloud' }" @click="activeTab = 'wordcloud'">词云</button>
                <button class="tab-btn" :class="{ active: activeTab === 'trend' }" @click="activeTab = 'trend'">趋势</button>
                <button class="tab-btn" :class="{ active: activeTab === 'content' }" @click="activeTab = 'content'">内容</button>
            </div>

            <!-- Tab 内容 -->
            <div class="tab-content">
                <!-- 总览 Tab -->
                <div v-show="activeTab === 'overview'" class="overview-tab">
                    <div class="overview-grid">
                        <!-- 摘要 -->
                        <div class="card" v-if="results && results.summary">
                            <h4>内容摘要</h4>
                            <p class="summary-text">{{ results.summary.text || '暂无摘要' }}</p>
                        </div>

                        <!-- 来源分布 -->
                        <div class="card">
                            <h4>来源分布</h4>
                            <div class="sources-list">
                                <div v-for="src in sources" :key="src.id" class="source-item">
                                    <span class="source-name">{{ src.source_name }}</span>
                                    <span class="source-count">{{ src.items_count }}条</span>
                                </div>
                                <div v-if="sources.length === 0" class="empty">暂无数据</div>
                            </div>
                        </div>

                        <!-- 实体 -->
                        <div class="card" v-if="results && results.entities">
                            <h4>关键实体</h4>
                            <div class="entities-section" v-if="results.entities.companies && results.entities.companies.length">
                                <h5>公司/组织</h5>
                                <div class="entity-tags">
                                    <span v-for="e in results.entities.companies.slice(0, 10)" :key="e.name" class="entity-tag">
                                        {{ e.name }} ({{ e.count }})
                                    </span>
                                </div>
                            </div>
                            <div class="entities-section" v-if="results.entities.products && results.entities.products.length">
                                <h5>产品</h5>
                                <div class="entity-tags">
                                    <span v-for="e in results.entities.products.slice(0, 10)" :key="e.name" class="entity-tag product">
                                        {{ e.name }} ({{ e.count }})
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 词云 Tab -->
                <div v-show="activeTab === 'wordcloud'" class="wordcloud-tab">
                    <div class="card">
                        <h4>关键词词云</h4>
                        <div id="wordcloudContainer" class="wordcloud-container">
                            <div v-if="!results || !results.wordcloud || !results.wordcloud.words || results.wordcloud.words.length === 0" class="empty">
                                暂无数据
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 趋势 Tab -->
                <div v-show="activeTab === 'trend'" class="trend-tab">
                    <div class="card">
                        <h4>内容量趋势</h4>
                        <div class="chart-container">
                            <canvas id="trendChart"></canvas>
                        </div>
                        <div v-if="results && results.trend" class="trend-stats">
                            <span>峰值: {{ results.trend.peak_date }} ({{ results.trend.peak_count }}条)</span>
                            <span>总计: {{ results.trend.total }}条</span>
                        </div>
                    </div>
                </div>

                <!-- 内容 Tab -->
                <div v-show="activeTab === 'content'" class="content-tab">
                    <div class="card">
                        <h4>相关内容</h4>
                        <div class="content-list">
                            <div v-for="item in items" :key="item.id" class="content-item">
                                <div class="content-header">
                                    <a :href="item.url" target="_blank" class="content-title">{{ item.title }}</a>
                                    <span class="relevance-badge" :class="{ high: item.relevance_score >= 0.6 }">
                                        {{ (item.relevance_score * 100).toFixed(0) }}%
                                    </span>
                                </div>
                                <p class="content-summary">{{ (item.summary || '').substring(0, 150) }}...</p>
                                <div class="content-meta">
                                    <span>{{ item.source_name }}</span>
                                    <span>{{ formatTime(item.published_at) }}</span>
                                </div>
                            </div>
                            <div v-if="items.length === 0" class="empty">暂无内容</div>
                        </div>
                    </div>
                </div>
            </div>
        </template>
    </div>
    `
};
