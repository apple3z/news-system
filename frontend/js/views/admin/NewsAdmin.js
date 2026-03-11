/**
 * NewsAdmin - News management admin tab (crawl logs, start crawl).
 */
const NewsAdmin = {
    data() {
        return {
            logs: [],
            total: 0,
            statNew: '-',
            statUpdated: '-'
        };
    },
    methods: {
        async loadCrawlLogs() {
            const data = await API.get('/api/admin/crawl-logs?page=1&per_page=20');
            if (data.code === 200) {
                this.logs = data.data.logs || [];
                this.total = data.data.total || 0;
                if (this.logs.length > 0) {
                    this.statNew = this.logs[0][4];
                    this.statUpdated = this.logs[0][5];
                }
            }
        },
        async startCrawl() {
            if (!confirm('确定要启动爬虫吗？这可能需要几分钟时间。')) return;
            const data = await API.post('/api/admin/start-crawl', {});
            if (data.code === 200) {
                alert('爬虫已启动！请在爬虫日志中查看进度。');
                this.loadCrawlLogs();
            } else {
                alert('启动失败：' + data.message);
            }
        }
    },
    mounted() {
        this.loadCrawlLogs();
    },
    template: `
    <div>
        <div class="stat-cards">
            <div class="stat-card">
                <div class="stat-number">{{ total }}</div>
                <div class="stat-label">总新闻数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ statNew }}</div>
                <div class="stat-label">新增</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ statUpdated }}</div>
                <div class="stat-label">更新</div>
            </div>
        </div>

        <button class="btn btn-success" @click="startCrawl">▶️ 启动爬虫</button>

        <table style="margin-top:20px;">
            <thead>
                <tr><th>ID</th><th>开始时间</th><th>结束时间</th><th>状态</th><th>总数</th><th>新增</th><th>更新</th></tr>
            </thead>
            <tbody>
                <tr v-for="log in logs" :key="log[0]">
                    <td>{{ log[0] }}</td><td>{{ log[1] }}</td><td>{{ log[2] || '进行中' }}</td>
                    <td>{{ log[3] }}</td><td>{{ log[4] }}</td><td>{{ log[5] }}</td><td>{{ log[6] }}</td>
                </tr>
            </tbody>
        </table>
    </div>
    `
};
