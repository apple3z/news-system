/**
 * NewsView - News listing page with filters, sorting, pagination.
 */
const NewsView = {
    data() {
        return {
            newsList: [],
            total: 0,
            hotNews: [],
            categories: [],
            sources: [],
            keyword: '',
            category: '',
            source: '',
            sortBy: 'time',
            sortOrder: 'desc',
            page: 1,
            perPage: 20,
            loading: false,
            loaded: false,
            bannerSlides: [],
            currentBannerIndex: 0
        };
    },
    computed: {
        totalPages() {
            return Math.ceil(this.total / this.perPage);
        },
        isEmpty() {
            return this.loaded && this.newsList.length === 0;
        },
        topCategories() {
            return this.categories.slice(0, 6);
        }
    },
    methods: {
        async loadNews() {
            this.loading = true;
            try {
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
            } finally {
                this.loading = false;
                this.loaded = true;
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
        async loadHotNews() {
            try {
                const data = await API.get('/api/news/search?sort_by=hot_score&sort_order=desc&per_page=10');
                if (data.code === 200) {
                    this.hotNews = data.data || [];
                    this.bannerSlides = this.hotNews.slice(0, 4);
                }
            } catch (e) {
                console.error('加载热点失败', e);
            }
        },
        selectCategory(cat) {
            this.category = cat;
            this.page = 1;
            this.loadNews();
        },
        clearCategory() {
            this.category = '';
            this.page = 1;
            this.loadNews();
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
        },
        nextBanner() {
            if (this.bannerSlides.length > 0) {
                this.currentBannerIndex = (this.currentBannerIndex + 1) % this.bannerSlides.length;
            }
        },
        getReadingTime(content) {
            if (!content) return '1分钟';
            const len = content.length;
            const minutes = Math.max(1, Math.ceil(len / 500));
            return minutes + '分钟阅读';
        }
    },
    mounted() {
        this.loadFilters();
        this.loadHotNews();
        this.loadNews();
        this._bannerTimer = setInterval(() => {
            if (this.bannerSlides.length > 1) {
                this.nextBanner();
            }
        }, 5000);
    },
    beforeUnmount() {
        clearInterval(this._bannerTimer);
    },
    template: `
    <div class="theme-dark">
        <div class="container">
            <!-- Banner -->
            <div v-if="bannerSlides.length > 0" class="hero-banner">
                <div class="hero-content">
                    <div class="hero-badge">🚀 科技热点</div>
                    <h1 class="hero-title">{{ bannerSlides[currentBannerIndex]?.title }}</h1>
                    <p class="hero-summary">{{ bannerSlides[currentBannerIndex]?.summary?.substring(0, 80) }}...</p>
                    <button class="hero-btn" @click="openLink(bannerSlides[currentBannerIndex]?.link)">阅读全文</button>
                    <div class="hero-dots">
                        <span v-for="(slide, idx) in bannerSlides" :key="idx" 
                              class="hero-dot" :class="{ active: idx === currentBannerIndex }"
                              @click="currentBannerIndex = idx"></span>
                    </div>
                </div>
                <div class="hero-overlay"></div>
            </div>

            <!-- Category Tags -->
            <div class="category-tags">
                <span class="category-tag-item" :class="{ active: category === '' }" @click="clearCategory">
                    精选
                </span>
                <span v-for="cat in topCategories" :key="cat.name" 
                      class="category-tag-item" 
                      :class="{ active: category === cat.name }"
                      @click="selectCategory(cat.name)">
                    {{ cat.name }}
                </span>
            </div>

            <!-- Hot Ranking Sidebar + Main Content -->
            <div class="news-layout">
                <!-- Main Grid -->
                <div class="news-main">
                    <!-- Filters -->
                    <div class="filters-bar">
                        <div class="filters-row">
                            <div class="filter-group">
                                <input type="text" v-model="keyword" placeholder="搜索新闻..." @keyup.enter="applyFilters" class="search-input">
                            </div>
                            <div class="filter-group">
                                <select v-model="source">
                                    <option value="">全部来源</option>
                                    <option v-for="src in sources" :key="src.name" :value="src.name">{{ src.name }}</option>
                                </select>
                            </div>
                            <div class="filter-group">
                                <select v-model="sortBy">
                                    <option value="time">时间优先</option>
                                    <option value="hot_score">热度优先</option>
                                </select>
                            </div>
                            <button class="btn-filter" @click="applyFilters">搜索</button>
                            <button class="btn-clear" @click="clearFilters">清除</button>
                        </div>
                    </div>

                    <!-- Stats -->
                    <div class="content-stats">
                        <span>{{ total }} 条新闻</span>
                        <span v-if="category" class="current-filter">筛选: {{ category }}</span>
                    </div>

                    <!-- Loading -->
                    <div v-if="loading" class="news-grid">
                        <div v-for="i in 6" :key="i" class="news-card">
                            <div class="loading-skeleton" style="height: 160px; width: 100%; border-radius: 8px 8px 0 0; margin-bottom: 12px;"></div>
                            <div class="loading-skeleton" style="height: 24px; width: 80%; margin-bottom: 12px;"></div>
                            <div class="loading-skeleton" style="height: 16px; width: 100%; margin-bottom: 8px;"></div>
                            <div class="loading-skeleton" style="height: 16px; width: 60%;"></div>
                        </div>
                    </div>

                    <!-- Empty -->
                    <div v-else-if="isEmpty" class="empty-state">
                        <div class="empty-state-icon">📰</div>
                        <div class="empty-state-text">暂无新闻</div>
                        <div class="empty-state-hint">试试调整筛选条件</div>
                    </div>

                    <!-- News Grid -->
                    <div v-else class="news-grid">
                        <div v-for="item in newsList" :key="item.id" class="news-card" @click="openLink(item.link)">
                            <div v-if="item.image" class="news-card-image" :style="{ backgroundImage: 'url(' + item.image + ')' }"></div>
                            <div v-else class="news-card-image news-card-image-placeholder">
                                <span>{{ item.category?.charAt(0) || '新' }}</span>
                            </div>
                            <div class="news-card-content">
                                <h3>{{ item.title }}</h3>
                                <p class="summary">{{ item.summary || '暂无摘要' }}</p>
                                <div class="meta">
                                    <span class="source">{{ item.source }}</span>
                                    <span class="category-tag">{{ item.category || '未分类' }}</span>
                                    <span class="read-time">{{ getReadingTime(item.content) }}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Pagination -->
                    <pagination v-if="!loading && !isEmpty" :current-page="page" :total-pages="totalPages" @page-change="goToPage"></pagination>
                </div>

                <!-- Hot Ranking Sidebar -->
                <div v-if="hotNews.length > 0" class="news-sidebar">
                    <div class="hot-rank">
                        <h3 class="hot-rank-title">🔥 热门排行</h3>
                        <div class="hot-rank-list">
                            <div v-for="(item, idx) in hotNews" :key="item.id" class="hot-rank-item" @click="openLink(item.link)">
                                <span class="hot-rank-num" :class="'top-' + (idx + 1)">{{ idx + 1 }}</span>
                                <span class="hot-rank-title-text">{{ item.title }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `
};
