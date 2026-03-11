/**
 * NewsView - News listing page with filters, sorting, pagination.
 */
const NewsView = {
    data() {
        return {
            newsList: [],
            total: 0,
            categories: [],
            sources: [],
            keyword: '',
            category: '',
            source: '',
            sortBy: 'time',
            sortOrder: 'desc',
            page: 1,
            perPage: 20
        };
    },
    computed: {
        totalPages() {
            return Math.ceil(this.total / this.perPage);
        }
    },
    methods: {
        async loadNews() {
            const params = new URLSearchParams({
                keyword: this.keyword,
                category: this.category,
                source: this.source,
                sort_by: this.sortBy,
                sort_order: this.sortOrder,
                page: this.page,
                per_page: this.perPage
            });
            const data = await API.get('/api/news/search?' + params);
            if (data.code === 200) {
                this.newsList = data.data || [];
                this.total = data.total || 0;
            }
        },
        async loadFilters() {
            const [catRes, srcRes] = await Promise.all([
                API.get('/api/news/categories'),
                API.get('/api/news/sources')
            ]);
            this.categories = catRes.data || [];
            this.sources = srcRes.data || [];
        },
        applyFilters() {
            this.page = 1;
            this.loadNews();
        },
        clearFilters() {
            this.keyword = '';
            this.category = '';
            this.source = '';
            this.sortBy = 'time';
            this.sortOrder = 'desc';
            this.page = 1;
            this.loadNews();
        },
        goToPage(p) {
            this.page = p;
            this.loadNews();
        },
        openLink(link) {
            if (link) window.open(link, '_blank');
        }
    },
    mounted() {
        this.loadFilters();
        this.loadNews();
    },
    template: `
    <div class="theme-dark">
        <div class="container">
            <div class="filters-bar">
                <div class="filters-row">
                    <div class="filter-group">
                        <label>关键词</label>
                        <input type="text" v-model="keyword" placeholder="搜索标题、摘要..." @keyup.enter="applyFilters">
                    </div>
                    <div class="filter-group">
                        <label>分类</label>
                        <select v-model="category">
                            <option value="">全部分类</option>
                            <option v-for="cat in categories" :key="cat.name" :value="cat.name">{{ cat.name }} ({{ cat.count }})</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>来源</label>
                        <select v-model="source">
                            <option value="">全部来源</option>
                            <option v-for="src in sources" :key="src.name" :value="src.name">{{ src.name }} ({{ src.count }})</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>排序</label>
                        <select v-model="sortBy">
                            <option value="time">时间</option>
                            <option value="hot_score">热度</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>顺序</label>
                        <select v-model="sortOrder">
                            <option value="desc">降序</option>
                            <option value="asc">升序</option>
                        </select>
                    </div>
                    <button class="btn-filter" @click="applyFilters">搜索</button>
                    <button class="btn-clear" @click="clearFilters">清除</button>
                </div>
                <div class="filters-row" style="justify-content:space-between;">
                    <div class="stats">{{ total }} 条新闻</div>
                    <pagination :current-page="page" :total-pages="totalPages" @page-change="goToPage"></pagination>
                </div>
            </div>

            <div class="news-grid">
                <div v-for="item in newsList" :key="item.id" class="news-card" @click="openLink(item.link)">
                    <h3>{{ item.title }}</h3>
                    <p class="summary">{{ item.summary || '暂无摘要' }}</p>
                    <div class="meta">
                        <span class="source">{{ item.source }}</span>
                        <span class="category-tag">{{ item.category || '未分类' }}</span>
                        <span>{{ (item.time || '').substring(0, 16) }}</span>
                    </div>
                </div>
            </div>

            <pagination :current-page="page" :total-pages="totalPages" @page-change="goToPage"></pagination>
        </div>
    </div>
    `
};
