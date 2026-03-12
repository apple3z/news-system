/**
 * NewsAdmin - 数据采集工作台
 * 整合新闻、Skills、RSS的采集和数据源管理
 * v2.6.2: 添加每日数据分析图表 + 采集日志详情
 */
const NewsAdmin = {
    data() {
        return {
            // 统计
            stats: { news: 0, skill: 0, rss: 0, total: 0 },
            // 当前Tab: sources / logs / chart
            activeTab: 'sources',
            // 数据源
            sources: [],
            sourceFilter: '',
            // 采集日志
            logs: [],
            logTotal: 0,
            logFilter: '',
            logPage: 1,
            // 弹窗
            showModal: false,
            editMode: false,
            editId: null,
            form: { name: '', type: 'news', url: '', priority: 10, config: {} },
            // 采集状态
            crawling: false,
            // 日志详情展开
            expandedLogId: null,
            // 图表
            chartData: null,
            chartInstance: null
        };
    },
    computed: {
        filteredSources() {
            if (!this.sourceFilter) return this.sources;
            return this.sources.filter(s => s.type === this.sourceFilter);
        }
    },
    methods: {
        async loadStats() {
            const res = await API.get('/api/admin/datasources/stats');
            if (res.code === 200) this.stats = res.data;
        },
        async loadSources() {
            const res = await API.get('/api/admin/datasources');
            if (res.code === 200) this.sources = res.data || [];
        },
        async loadLogs() {
            let url = '/api/admin/crawl/logs?page=' + this.logPage + '&per_page=15';
            if (this.logFilter) url += '&type=' + this.logFilter;
            const res = await API.get(url);
            if (res.code === 200) {
                this.logs = res.data || [];
                this.logTotal = res.total || 0;
            }
        },
        toggleLogDetail(logId) {
            this.expandedLogId = this.expandedLogId === logId ? null : logId;
        },
        getLogNewsDetail(log) {
            if (!log.detail) return [];
            // unified_crawl_log stores detail as {news: 'completed', news_detail: [...]}
            if (Array.isArray(log.detail.news_detail)) return log.detail.news_detail;
            // news.db crawl_log stores detail directly as array
            if (Array.isArray(log.detail)) return log.detail;
            return [];
        },
        // 图表
        async loadChart() {
            const res = await API.get('/api/admin/stats/daily?days=30');
            if (res.code === 200) {
                this.chartData = res.data;
                this.$nextTick(() => this.renderChart());
            }
        },
        renderChart() {
            if (this.chartInstance) {
                this.chartInstance.destroy();
            }
            const canvas = this.$refs.dailyChart;
            if (!canvas || !this.chartData) return;

            const newsData = this.chartData.news || [];
            const rssData = this.chartData.rss || [];
            const skillData = this.chartData.skill || [];

            // 合并所有日期
            const dateSet = new Set();
            newsData.forEach(d => dateSet.add(d.day));
            rssData.forEach(d => dateSet.add(d.day));
            skillData.forEach(d => dateSet.add(d.day));
            const labels = Array.from(dateSet).sort();

            const newsMap = {};
            newsData.forEach(d => newsMap[d.day] = d.count);
            const rssMap = {};
            rssData.forEach(d => rssMap[d.day] = d.count);
            const skillMap = {};
            skillData.forEach(d => skillMap[d.day] = d.count);

            this.chartInstance = new Chart(canvas, {
                type: 'line',
                data: {
                    labels: labels.map(d => d ? d.substring(5) : ''),
                    datasets: [
                        {
                            label: '新闻源',
                            data: labels.map(d => newsMap[d] || 0),
                            borderColor: '#6366f1',
                            backgroundColor: 'rgba(99,102,241,0.1)',
                            fill: true,
                            tension: 0.3
                        },
                        {
                            label: 'RSS源',
                            data: labels.map(d => rssMap[d] || 0),
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16,185,129,0.1)',
                            fill: true,
                            tension: 0.3
                        },
                        {
                            label: 'Skill源',
                            data: labels.map(d => skillMap[d] || 0),
                            borderColor: '#f59e0b',
                            backgroundColor: 'rgba(245,158,11,0.1)',
                            fill: true,
                            tension: 0.3
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            labels: { color: '#ccc' }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#999' },
                            grid: { color: 'rgba(255,255,255,0.05)' }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: { color: '#999' },
                            grid: { color: 'rgba(255,255,255,0.05)' }
                        }
                    }
                }
            });
        },
        // 采集操作
        async startCrawl(type) {
            const names = { full: '全量采集', news: '新闻采集', skill: 'Skills采集', rss: 'RSS采集' };
            if (!confirm('确定要启动' + names[type] + '吗？')) return;
            this.crawling = true;
            const res = await API.post('/api/admin/crawl/start', { type });
            if (res.code === 200) {
                alert(res.message);
                this.loadLogs();
            } else {
                alert('启动失败：' + res.message);
            }
            this.crawling = false;
        },
        // 数据源 CRUD
        openCreate() {
            this.editMode = false;
            this.editId = null;
            this.form = { name: '', type: 'news', url: '', priority: 10, config: {} };
            this.showModal = true;
        },
        openEdit(source) {
            this.editMode = true;
            this.editId = source.id;
            this.form = {
                name: source.name,
                type: source.type,
                url: source.url,
                priority: source.priority,
                config: source.config || {}
            };
            this.showModal = true;
        },
        async saveSource() {
            if (!this.form.name || !this.form.url) { alert('名称和URL必填'); return; }
            let res;
            if (this.editMode) {
                res = await API.put('/api/admin/datasources/' + this.editId, this.form);
            } else {
                res = await API.post('/api/admin/datasources', this.form);
            }
            if (res.code === 200) {
                this.showModal = false;
                this.loadSources();
                this.loadStats();
            } else {
                alert(res.message);
            }
        },
        async toggleSource(source) {
            const res = await API.put('/api/admin/datasources/' + source.id + '/toggle');
            if (res.code === 200) { this.loadSources(); this.loadStats(); }
        },
        async deleteSource(source) {
            if (!confirm('确定删除数据源 "' + source.name + '" 吗？')) return;
            const res = await API.del('/api/admin/datasources/' + source.id);
            if (res.code === 200) { this.loadSources(); this.loadStats(); }
            else alert(res.message);
        },
        typeLabel(t) {
            return { news: '新闻', skill: 'Skill', rss: 'RSS' }[t] || t;
        },
        statusClass(s) {
            return s === 'active' ? 'badge-success' : 'badge-gray';
        },
        logStatusClass(s) {
            if (s === 'completed') return 'badge-success';
            if (s === 'running') return 'badge-warning';
            return 'badge-danger';
        }
    },
    mounted() {
        this.loadStats();
        this.loadSources();
        this.loadLogs();
    },
    beforeUnmount() {
        if (this.chartInstance) this.chartInstance.destroy();
    },
    template: `
    <div>
        <!-- 统计卡片 -->
        <div class="stat-cards">
            <div class="stat-card">
                <div class="stat-number">{{ stats.news }}</div>
                <div class="stat-label">新闻源</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.skill }}</div>
                <div class="stat-label">Skill源</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.rss }}</div>
                <div class="stat-label">RSS源</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.total }}</div>
                <div class="stat-label">总数据源</div>
            </div>
        </div>

        <!-- 采集按钮区 -->
        <div class="crawl-actions">
            <button class="btn btn-success" @click="startCrawl('full')" :disabled="crawling">
                ▶ 全量采集
            </button>
            <button class="btn btn-primary btn-sm" @click="startCrawl('news')" :disabled="crawling">
                采集新闻
            </button>
            <button class="btn btn-primary btn-sm" @click="startCrawl('skill')" :disabled="crawling">
                采集Skills
            </button>
            <button class="btn btn-primary btn-sm" @click="startCrawl('rss')" :disabled="crawling">
                采集RSS
            </button>
        </div>

        <!-- Tab切换 -->
        <div class="inner-tabs">
            <button :class="['tab-btn', activeTab === 'sources' ? 'active' : '']"
                    @click="activeTab = 'sources'">数据源管理</button>
            <button :class="['tab-btn', activeTab === 'logs' ? 'active' : '']"
                    @click="activeTab = 'logs'; loadLogs()">采集日志</button>
            <button :class="['tab-btn', activeTab === 'chart' ? 'active' : '']"
                    @click="activeTab = 'chart'; loadChart()">数据分析</button>
        </div>

        <!-- 数据源管理 -->
        <div v-show="activeTab === 'sources'">
            <div class="toolbar">
                <select v-model="sourceFilter" class="filter-select">
                    <option value="">全部类型</option>
                    <option value="news">新闻源</option>
                    <option value="skill">Skill源</option>
                    <option value="rss">RSS源</option>
                </select>
                <button class="btn btn-primary btn-sm" @click="openCreate">+ 添加数据源</button>
            </div>

            <table class="admin-table">
                <thead>
                    <tr>
                        <th>ID</th><th>名称</th><th>类型</th><th>URL</th>
                        <th>优先级</th><th>状态</th><th>上次采集</th><th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="s in filteredSources" :key="s.id">
                        <td>{{ s.id }}</td>
                        <td>{{ s.name }}</td>
                        <td><span class="badge-info">{{ typeLabel(s.type) }}</span></td>
                        <td class="url-cell" :title="s.url">{{ s.url }}</td>
                        <td>{{ s.priority }}</td>
                        <td>
                            <span :class="statusClass(s.status)" @click="toggleSource(s)" style="cursor:pointer">
                                {{ s.status === 'active' ? '启用' : '禁用' }}
                            </span>
                        </td>
                        <td>{{ s.last_crawl_time || '-' }}</td>
                        <td class="actions">
                            <a href="#" @click.prevent="openEdit(s)">编辑</a>
                            <a href="#" @click.prevent="deleteSource(s)" class="text-danger">删除</a>
                        </td>
                    </tr>
                    <tr v-if="filteredSources.length === 0">
                        <td colspan="8" style="text-align:center;color:#999">暂无数据源</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 采集日志 -->
        <div v-show="activeTab === 'logs'">
            <div class="toolbar">
                <select v-model="logFilter" @change="logPage=1; loadLogs()" class="filter-select">
                    <option value="">全部类型</option>
                    <option value="full">全量采集</option>
                    <option value="news">新闻采集</option>
                    <option value="skill">Skills采集</option>
                    <option value="rss">RSS采集</option>
                </select>
            </div>

            <table class="admin-table">
                <thead>
                    <tr>
                        <th>ID</th><th>类型</th><th>开始时间</th><th>结束时间</th>
                        <th>状态</th><th>总数</th><th>新增</th><th>更新</th><th>详情</th>
                    </tr>
                </thead>
                <tbody>
                    <template v-for="log in logs" :key="log.id">
                        <tr>
                            <td>{{ log.id }}</td>
                            <td><span class="badge-info">{{ typeLabel(log.type) || log.type }}</span></td>
                            <td>{{ log.start_time }}</td>
                            <td>{{ log.end_time || '进行中...' }}</td>
                            <td><span :class="logStatusClass(log.status)">{{ log.status }}</span></td>
                            <td>{{ log.total_news_count || log.total_count || 0 }}</td>
                            <td>{{ log.new_news_count || log.new_count || 0 }}</td>
                            <td>{{ log.updated_news_count || log.updated_count || 0 }}</td>
                            <td>
                                <a v-if="getLogNewsDetail(log).length > 0"
                                   href="#" @click.prevent="toggleLogDetail(log.id)"
                                   style="color:#6366f1;">
                                    {{ expandedLogId === log.id ? '收起' : '展开' }} ({{ getLogNewsDetail(log).length }})
                                </a>
                                <span v-else style="color:#666;">-</span>
                            </td>
                        </tr>
                        <tr v-if="expandedLogId === log.id && getLogNewsDetail(log).length > 0">
                            <td colspan="9" style="padding:0;">
                                <div style="max-height:300px;overflow-y:auto;background:rgba(0,0,0,0.2);padding:12px;">
                                    <table style="width:100%;font-size:12px;color:#ccc;">
                                        <thead>
                                            <tr style="color:#999;">
                                                <th style="padding:4px 8px;text-align:left;">标题</th>
                                                <th style="padding:4px 8px;text-align:left;">来源</th>
                                                <th style="padding:4px 8px;text-align:left;">时间</th>
                                                <th style="padding:4px 8px;text-align:left;">链接</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr v-for="(item, i) in getLogNewsDetail(log)" :key="i" style="border-top:1px solid rgba(255,255,255,0.05);">
                                                <td style="padding:4px 8px;">{{ item.title }}</td>
                                                <td style="padding:4px 8px;">{{ item.source }}</td>
                                                <td style="padding:4px 8px;">{{ item.time }}</td>
                                                <td style="padding:4px 8px;">
                                                    <a :href="item.link" target="_blank" style="color:#6366f1;">查看</a>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </td>
                        </tr>
                    </template>
                    <tr v-if="logs.length === 0">
                        <td colspan="9" style="text-align:center;color:#999">暂无采集日志</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 数据分析图表 -->
        <div v-show="activeTab === 'chart'">
            <div style="background:rgba(255,255,255,0.03);border-radius:12px;padding:24px;margin-top:16px;">
                <h3 style="color:#fff;margin:0 0 16px 0;font-size:16px;">近30天数据趋势</h3>
                <canvas ref="dailyChart" height="100"></canvas>
            </div>
        </div>

        <!-- 数据源编辑弹窗 -->
        <modal-dialog v-if="showModal" @close="showModal = false"
                      :title="editMode ? '编辑数据源' : '添加数据源'">
            <div class="modal-form">
                <div class="form-group">
                    <label>名称</label>
                    <input v-model="form.name" placeholder="数据源名称">
                </div>
                <div class="form-group">
                    <label>类型</label>
                    <select v-model="form.type">
                        <option value="news">新闻源</option>
                        <option value="skill">Skill源</option>
                        <option value="rss">RSS源</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>URL</label>
                    <input v-model="form.url" placeholder="https://...">
                </div>
                <div class="form-group">
                    <label>优先级 (1-20)</label>
                    <input v-model.number="form.priority" type="number" min="1" max="20">
                </div>
                <div class="modal-actions">
                    <button class="btn btn-primary" @click="saveSource">保存</button>
                    <button class="btn btn-default" @click="showModal = false">取消</button>
                </div>
            </div>
        </modal-dialog>
    </div>
    `
};
