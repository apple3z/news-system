/**
 * SubscribeView - 订阅资讯页面（公开）
 * v2.6.2: 展示RSS订阅的实际内容，而非管理订阅
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
            loading: false
        };
    },
    computed: {
        totalPages() {
            return Math.ceil(this.total / this.perPage);
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
            }
        },
        onFilterChange() {
            this.page = 1;
            this.loadFeeds();
        },
        prevPage() {
            if (this.page > 1) { this.page--; this.loadFeeds(); }
        },
        nextPage() {
            if (this.page < this.totalPages) { this.page++; this.loadFeeds(); }
        },
        formatContent(content) {
            if (!content) return '';
            return content.length > 200 ? content.substring(0, 200) + '...' : content;
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
        <div class="container" style="max-width:1200px;">
            <h2 style="color:#fff;margin-bottom:20px;">订阅资讯</h2>

            <!-- 筛选栏 -->
            <div style="display:flex;gap:12px;margin-bottom:24px;align-items:center;">
                <select v-model="sourceFilter" @change="onFilterChange"
                        style="padding:8px 12px;border-radius:6px;border:1px solid rgba(255,255,255,0.2);background:rgba(255,255,255,0.05);color:#fff;font-size:14px;">
                    <option value="">全部订阅源</option>
                    <option v-for="s in sources" :key="s" :value="s">{{ s }}</option>
                </select>
                <span style="color:#aaa;font-size:13px;">共 {{ total }} 条内容</span>
            </div>

            <!-- 加载状态 -->
            <div v-if="loading" style="text-align:center;padding:40px;color:#aaa;">加载中...</div>

            <!-- 内容列表 -->
            <div v-else class="rss-feed-list">
                <div v-for="item in feeds" :key="item.id" class="rss-feed-card">
                    <div class="rss-feed-header">
                        <span class="rss-source-tag">{{ item.sub_name }}</span>
                        <span class="rss-date">{{ formatDate(item.detected_at) }}</span>
                    </div>
                    <p>{{ formatContent(item.content) }}</p>
                    <a v-if="item.source_url" :href="item.source_url" target="_blank" class="rss-read-more">
                        查看原文 →
                    </a>
                </div>

                <div v-if="feeds.length === 0" style="text-align:center;padding:60px;color:#888;">
                    <p>暂无订阅内容</p>
                    <p style="font-size:13px;">请在后台添加RSS订阅源并执行采集</p>
                </div>
            </div>

            <!-- 分页 -->
            <div v-if="totalPages > 1" style="display:flex;justify-content:center;gap:16px;margin-top:24px;">
                <button @click="prevPage" :disabled="page <= 1"
                        style="padding:8px 16px;border-radius:4px;border:1px solid rgba(255,255,255,0.2);background:transparent;color:#fff;cursor:pointer;">
                    上一页
                </button>
                <span style="color:#aaa;line-height:36px;">{{ page }} / {{ totalPages }}</span>
                <button @click="nextPage" :disabled="page >= totalPages"
                        style="padding:8px 16px;border-radius:4px;border:1px solid rgba(255,255,255,0.2);background:transparent;color:#fff;cursor:pointer;">
                    下一页
                </button>
            </div>
        </div>
    </div>
    `
};
