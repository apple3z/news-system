/**
 * SubscribeView - 订阅资讯页面（公开）
 * v2.6.2: 改为新闻卡片样式展示
 */
const SubscribeView = {
    data() {
        return {
            feeds: [],
            sources: [],
            sourceFilter: '',
            page: 1,
            total: 0,
            perPage: 20,
            loading: false,
            loaded: false
        };
    },
    computed: {
        totalPages() {
            return Math.ceil(this.total / this.perPage);
        },
        isEmpty() {
            return this.loaded && this.feeds.length === 0;
        }
    },
    methods: {
        async loadSources() {
            const res = await API.get('/api/subscribe/sources');
            if (res.code === 200) this.sources = res.data || [];
        },
        async loadFeeds() {
            this.loading = true;
            let url = '/api/subscribe/feed?page=' + this.page + '&per_page=' + this.perPage;
            if (this.sourceFilter) url += '&source=' + encodeURIComponent(this.sourceFilter);
            try {
                const res = await API.get(url);
                if (res.code === 200) {
                    this.feeds = res.data || [];
                    this.total = res.total || 0;
                }
            } finally {
                this.loading = false;
                this.loaded = true;
            }
        },
        onFilterChange() {
            this.page = 1;
            this.loadFeeds();
        },
        goToPage(p) {
            this.page = p;
            this.loadFeeds();
        },
        openLink(url) {
            if (url) window.open(url, '_blank');
        },
        parseTitle(content) {
            if (!content) return '无标题';
            const first = content.split('\n')[0].trim();
            return first.length > 60 ? first.substring(0, 60) + '...' : first;
        },
        formatSummary(content) {
            if (!content) return '暂无内容';
            const text = content.replace(/^[^\n]*\n?/, '').trim();
            return text.length > 150 ? text.substring(0, 150) + '...' : (text || content.substring(0, 150));
        },
        formatDate(dt) {
            if (!dt) return '';
            return dt.substring(0, 16);
        }
    },
    mounted() {
        this.loadSources();
        this.loadFeeds();
    },
    template: `
    <div class="theme-dark">
        <div class="container">
            <h2 style="color:#fff;margin-bottom:8px;">订阅资讯</h2>
            <p style="color:#999;margin-bottom:20px;font-size:14px;">来自RSS订阅源的最新内容</p>

            <!-- 筛选栏 -->
            <div class="filters-bar">
                <div class="filters-row">
                    <div class="filter-group">
                        <select v-model="sourceFilter" @change="onFilterChange">
                            <option value="">全部订阅源</option>
                            <option v-for="s in sources" :key="s" :value="s">{{ s }}</option>
                        </select>
                    </div>
                    <div class="content-stats" style="margin:0;">
                        <span>{{ total }} 条内容</span>
                    </div>
                </div>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="news-grid">
                <div v-for="i in 6" :key="i" class="news-card">
                    <div class="loading-skeleton" style="height: 24px; width: 80%; margin-bottom: 12px;"></div>
                    <div class="loading-skeleton" style="height: 16px; width: 100%; margin-bottom: 8px;"></div>
                    <div class="loading-skeleton" style="height: 16px; width: 60%;"></div>
                </div>
            </div>

            <!-- Empty -->
            <div v-else-if="isEmpty" class="empty-state">
                <div class="empty-state-icon">📡</div>
                <div class="empty-state-text">暂无订阅内容</div>
                <div class="empty-state-hint">请在后台添加RSS订阅源并执行采集</div>
            </div>

            <!-- Feed Cards Grid -->
            <div v-else class="news-grid">
                <div v-for="item in feeds" :key="item.id" class="news-card" @click="openLink(item.source_url)">
                    <div class="news-card-image news-card-image-placeholder">
                        <span>📡</span>
                    </div>
                    <div class="news-card-content">
                        <h3>{{ parseTitle(item.content) }}</h3>
                        <p class="summary">{{ formatSummary(item.content) }}</p>
                        <div class="meta">
                            <span class="source">{{ item.sub_name }}</span>
                            <span class="time-info" v-if="item.detected_at">{{ formatDate(item.detected_at) }}</span>
                            <a v-if="item.source_url" :href="item.source_url" target="_blank" @click.stop class="read-time" style="color:#6366f1;">
                                查看原文
                            </a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Pagination -->
            <pagination v-if="!loading && !isEmpty && totalPages > 1" :current-page="page" :total-pages="totalPages" @page-change="goToPage"></pagination>
        </div>
    </div>
    `
};
