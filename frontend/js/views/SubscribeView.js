/**
 * SubscribeView - 订阅资讯页面（公开）
 * v2.6.2: 重构设计，参考Skills页面风格
 */
const SubscribeView = {
    data() {
        return {
            allFeeds: [],
            sources: [],
            keyword: '',
            sourceFilter: '',
            timeFilter: '',
            sortBy: 'latest',
            activeTab: 'all',
            page: 1,
            perPage: 50,
            loading: false,
            loaded: false,
            stats: {
                totalFeeds: 0,
                totalSources: 0,
                todayFeeds: 0
            }
        };
    },
    computed: {
        filteredFeeds() {
            let list = [...this.allFeeds];
            
            if (this.activeTab === 'today') {
                const today = new Date().toISOString().split('T')[0];
                list = list.filter(f => f.detected_at && f.detected_at.startsWith(today));
            } else if (this.activeTab === 'unread') {
                list = list;
            }
            
            if (this.keyword) {
                const kw = this.keyword.toLowerCase();
                list = list.filter(f =>
                    (f.title && f.title.toLowerCase().includes(kw)) ||
                    (f.summary && f.summary.toLowerCase().includes(kw)) ||
                    (f.sub_name && f.sub_name.toLowerCase().includes(kw))
                );
            }
            
            if (this.sourceFilter) {
                list = list.filter(f => f.sub_name === this.sourceFilter);
            }
            
            if (this.timeFilter) {
                const now = new Date();
                if (this.timeFilter === 'today') {
                    const today = now.toISOString().split('T')[0];
                    list = list.filter(f => f.detected_at && f.detected_at.startsWith(today));
                } else if (this.timeFilter === 'week') {
                    const weekAgo = new Date(now - 7 * 24 * 60 * 60 * 1000);
                    list = list.filter(f => f.detected_at && new Date(f.detected_at) >= weekAgo);
                } else if (this.timeFilter === 'month') {
                    const monthAgo = new Date(now - 30 * 24 * 60 * 60 * 1000);
                    list = list.filter(f => f.detected_at && new Date(f.detected_at) >= monthAgo);
                }
            }
            
            if (this.sortBy === 'latest') {
                list.sort((a, b) => new Date(b.detected_at || 0) - new Date(a.detected_at || 0));
            } else if (this.sortBy === 'source') {
                list.sort((a, b) => (a.sub_name || '').localeCompare(b.sub_name || ''));
            }
            
            return list;
        },
        isEmpty() {
            return this.loaded && this.filteredFeeds.length === 0;
        },
        totalPages() {
            return Math.ceil(this.filteredFeeds.length / this.perPage);
        },
        paginatedFeeds() {
            const start = (this.page - 1) * this.perPage;
            return this.filteredFeeds.slice(start, start + this.perPage);
        },
        hasActiveFilters() {
            return this.keyword || this.sourceFilter || this.timeFilter || this.sortBy !== 'latest' || this.activeTab !== 'all';
        }
    },
    methods: {
        async loadSources() {
            const res = await API.get('/api/subscribe/sources');
            if (res.code === 200) this.sources = res.data || [];
        },
        async loadFeeds() {
            this.loading = true;
            try {
                const res = await API.get('/api/subscribe/feed?per_page=200');
                if (res.code === 200) {
                    this.allFeeds = res.data || [];
                    this.stats.totalFeeds = res.total || 0;
                    this.stats.totalSources = this.sources.length;
                    const today = new Date().toISOString().split('T')[0];
                    this.stats.todayFeeds = this.allFeeds.filter(f => f.detected_at && f.detected_at.startsWith(today)).length;
                }
            } finally {
                this.loading = false;
                this.loaded = true;
            }
        },
        onFilterChange() {
            this.page = 1;
        },
        goToPage(p) {
            this.page = p;
        },
        openFeed(item) {
            this.$router.push('/subscribe/' + item.id);
        },
        stripHtml(html) {
            if (!html) return '';
            return html.replace(/<[^>]*>/g, '').trim();
        },
        getTitle(item) {
            if (item.title) {
                const title = this.stripHtml(item.title);
                if (title) return title.length > 60 ? title.substring(0, 60) + '...' : title;
            }
            if (item.content) {
                const text = this.stripHtml(item.content);
                const firstLine = text.split('\n')[0].trim();
                return firstLine.length > 60 ? firstLine.substring(0, 60) + '...' : (firstLine || '无标题');
            }
            return '无标题';
        },
        getSummary(item) {
            if (item.summary) {
                const summary = this.stripHtml(item.summary);
                if (summary) return summary.length > 120 ? summary.substring(0, 120) + '...' : summary;
            }
            if (item.content) {
                const text = this.stripHtml(item.content);
                const lines = text.split('\n').filter(l => l.trim());
                const summary = lines.slice(1).join(' ').trim();
                return summary.length > 120 ? summary.substring(0, 120) + '...' : (summary || text.substring(0, 120));
            }
            return '暂无摘要';
        },
        formatDate(dt) {
            if (!dt) return '';
            const date = new Date(dt);
            const now = new Date();
            const diff = now - date;
            const minutes = Math.floor(diff / (1000 * 60));
            const hours = Math.floor(diff / (1000 * 60 * 60));
            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            
            if (minutes < 1) return '刚刚';
            if (minutes < 60) return minutes + '分钟前';
            if (hours < 24) return hours + '小时前';
            if (days < 7) return days + '天前';
            return dt.substring(0, 10);
        },
        getSourceIcon(subName) {
            if (!subName) return '📡';
            const name = subName.toLowerCase();
            if (name.includes('github')) return '🐙';
            if (name.includes('twitter') || name.includes('x.com')) return '🐦';
            if (name.includes('reddit')) return '🤖';
            if (name.includes('hacker')) return '💻';
            if (name.includes('tech') || name.includes('技术')) return '🔧';
            if (name.includes('news') || name.includes('新闻')) return '📰';
            if (name.includes('blog')) return '📝';
            return '📡';
        },
        setTab(tab) {
            this.activeTab = tab;
            this.page = 1;
        },
        clearAllFilters() {
            this.keyword = '';
            this.sourceFilter = '';
            this.timeFilter = '';
            this.sortBy = 'latest';
            this.activeTab = 'all';
            this.page = 1;
        }
    },
    mounted() {
        this.loadSources().then(() => this.loadFeeds());
    },
    template: `
    <div class="theme-dark">
        <div class="container" style="max-width:1400px;">
            <div class="page-header">
                <div class="header-top">
                    <div>
                        <h1 class="page-title">我的订阅</h1>
                        <p class="page-subtitle">订阅你感兴趣的RSS源，获取最新资讯</p>
                    </div>
                    <div class="header-stats">
                        <div class="stat-box">
                            <span class="stat-number">{{ stats.totalFeeds }}</span>
                            <span class="stat-label">总内容数</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-number">{{ stats.totalSources }}</span>
                            <span class="stat-label">订阅源数</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-number">{{ stats.todayFeeds }}</span>
                            <span class="stat-label">今日更新</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="skills-tabs">
                <button class="tab-btn" :class="{ active: activeTab === 'all' }" @click="setTab('all')">
                    <span class="tab-icon">📦</span>
                    <span>全部内容</span>
                </button>
                <button class="tab-btn" :class="{ active: activeTab === 'today' }" @click="setTab('today')">
                    <span class="tab-icon">🆕</span>
                    <span>今日更新</span>
                </button>
                <button class="tab-btn" :class="{ active: activeTab === 'unread' }" @click="setTab('unread')">
                    <span class="tab-icon">📌</span>
                    <span>全部内容</span>
                </button>
            </div>

            <div class="advanced-filters">
                <div class="filter-section">
                    <div class="search-box">
                        <input type="text" v-model="keyword" @input="onFilterChange" placeholder="搜索订阅内容、标题或来源..." class="search-input-large">
                    </div>
                    
                    <div class="filter-group">
                        <select v-model="sourceFilter" @change="onFilterChange" class="filter-select">
                            <option value="">全部来源</option>
                            <option v-for="src in sources" :key="src" :value="src">{{ src }}</option>
                        </select>
                        
                        <select v-model="timeFilter" @change="onFilterChange" class="filter-select">
                            <option value="">全部时间</option>
                            <option value="today">今日</option>
                            <option value="week">本周</option>
                            <option value="month">本月</option>
                        </select>
                        
                        <select v-model="sortBy" @change="onFilterChange" class="filter-select">
                            <option value="latest">🕐 最新发布</option>
                            <option value="source">📂 按来源</option>
                        </select>
                    </div>
                    
                    <button class="btn-clear-filters" @click="clearAllFilters" v-if="hasActiveFilters">
                        清除所有筛选
                    </button>
                </div>
                
                <div class="filter-results">
                    <span class="results-count">显示 {{ paginatedFeeds.length }} / {{ filteredFeeds.length }} 条内容</span>
                    <span class="active-filters-tags" v-if="sourceFilter || timeFilter || keyword">
                        <span v-if="sourceFilter" class="filter-tag">
                            {{ sourceFilter }}
                            <button @click="sourceFilter = ''; onFilterChange()">×</button>
                        </span>
                        <span v-if="timeFilter" class="filter-tag">
                            {{ timeFilter === 'today' ? '今日' : timeFilter === 'week' ? '本周' : '本月' }}
                            <button @click="timeFilter = ''; onFilterChange()">×</button>
                        </span>
                    </span>
                </div>
            </div>

            <div class="skills-layout">
                <div class="skills-main">
                    <div v-if="loading" class="skills-grid">
                        <div v-for="i in 6" :key="i" class="skill-card">
                            <div class="loading-skeleton" style="height: 140px; width: 100%; border-radius: 12px; margin-bottom: 16px;"></div>
                            <div class="loading-skeleton" style="height: 24px; width: 80%; margin-bottom: 12px;"></div>
                            <div class="loading-skeleton" style="height: 16px; width: 100%; margin-bottom: 8px;"></div>
                            <div class="loading-skeleton" style="height: 16px; width: 60%;"></div>
                        </div>
                    </div>

                    <div v-else-if="isEmpty" class="empty-state-large">
                        <div class="empty-state-icon">📡</div>
                        <h3>暂无订阅内容</h3>
                        <p>试试调整筛选条件或稍后再来查看</p>
                        <button class="btn-reset" @click="clearAllFilters">重置筛选</button>
                    </div>

                    <div v-else class="subscribe-grid-enhanced">
                        <div v-for="item in paginatedFeeds" :key="item.id" class="subscribe-card-enhanced" @click="openFeed(item)">
                            <div class="subscribe-card-top">
                                <div class="subscribe-card-header">
                                    <span class="source-icon-large">{{ getSourceIcon(item.sub_name) }}</span>
                                    <div class="subscribe-card-info">
                                        <h3 class="subscribe-card-title">{{ getTitle(item) }}</h3>
                                        <p class="subscribe-card-source">{{ item.sub_name }}</p>
                                    </div>
                                </div>
                            </div>
                            
                            <p class="subscribe-card-desc">{{ getSummary(item) }}</p>
                            
                            <div class="subscribe-card-meta">
                                <span class="source-tag">{{ item.sub_name }}</span>
                                <span class="time-tag">{{ formatDate(item.detected_at) }}</span>
                            </div>
                        </div>
                    </div>

                    <pagination v-if="!loading && !isEmpty && totalPages > 1" :current-page="page" :total-pages="totalPages" @page-change="goToPage"></pagination>
                </div>

                <div v-if="sources.length > 0" class="skills-sidebar">
                    <div class="hot-rank">
                        <h3 class="hot-rank-title">
                            <span class="trophy-icon">📚</span>
                            我的订阅源
                        </h3>
                        <div class="hot-rank-list">
                            <div v-for="(src, idx) in sources.slice(0, 10)" :key="src" 
                                 class="hot-rank-item" 
                                 :class="{ active: sourceFilter === src }"
                                 @click="sourceFilter = sourceFilter === src ? '' : src; onFilterChange()">
                                <span class="hot-rank-num" :class="'top-' + (idx + 1)">{{ getSourceIcon(src) }}</span>
                                <span class="hot-rank-title-text">{{ src }}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="quick-categories">
                        <h4 class="sidebar-title">快速筛选</h4>
                        <div class="category-cloud">
                            <span class="category-cloud-item" :class="{ active: timeFilter === 'today' }" @click="timeFilter = timeFilter === 'today' ? '' : 'today'; onFilterChange()">
                                今日
                            </span>
                            <span class="category-cloud-item" :class="{ active: timeFilter === 'week' }" @click="timeFilter = timeFilter === 'week' ? '' : 'week'; onFilterChange()">
                                本周
                            </span>
                            <span class="category-cloud-item" :class="{ active: timeFilter === 'month' }" @click="timeFilter = timeFilter === 'month' ? '' : 'month'; onFilterChange()">
                                本月
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `
};
