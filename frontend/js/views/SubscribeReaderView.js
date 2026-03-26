/**
 * SubscribeReaderView - RSS阅读器风格（三栏布局）
 * v2.6.8: 真正的RSS阅读器体验
 */
const SubscribeReaderView = {
    data() {
        return {
            allFeeds: [],
            sources: [],
            sourcesMeta: [],
            sourceWeights: {},
            selectedSource: null,
            selectedFeed: null,
            timeFilter: 'week',
            loading: false,
            loaded: false,
            sidebarCollapsed: false
        };
    },
    computed: {
        feedsBySource() {
            const groups = {};
            this.sources.forEach(source => {
                const sourceFeeds = this.allFeeds.filter(f => f.sub_name === source);
                if (sourceFeeds.length > 0) {
                    groups[source] = sourceFeeds
                        .sort((a, b) => new Date(b.detected_at) - new Date(a.detected_at))
                        .slice(0, 50);
                }
            });
            return groups;
        },
        currentSourceFeeds() {
            if (!this.selectedSource) return this.allFeeds.slice(0, 100);
            return this.feedsBySource[this.selectedSource] || [];
        },
        unreadCount() {
            return this.allFeeds.length;
        }
    },
    methods: {
        formatTime(dateStr) {
            if (!dateStr) return '';
            const date = new Date(dateStr);
            const now = new Date();
            const diff = now - date;
            const minutes = Math.floor(diff / (1000 * 60));
            const hours = Math.floor(diff / (1000 * 60 * 60));
            
            if (minutes < 1) return '刚刚';
            if (minutes < 60) return `${minutes}分钟前`;
            if (hours < 24) return `${hours}小时前`;
            return dateStr.substring(5, 16);
        },
        getSourceIcon(source) {
            if (!source) return '📡';
            const name = source.toLowerCase();
            if (name.includes('openai') || name.includes('deepmind') || name.includes('anthropic')) return '🤖';
            if (name.includes('github') || name.includes('stack')) return '💻';
            if (name.includes('hacker') || name.includes('news')) return '📰';
            if (name.includes('tech') || name.includes('verge') || name.includes('wired')) return '🔧';
            if (name.includes('ai')) return '🧠';
            if (name.includes('量子位') || name.includes('机器之心') || name.includes('新智元')) return '🇨🇳';
            return '📡';
        },
        stripHtml(html) {
            if (!html) return '';
            return html.replace(/<[^>]*>/g, '').trim();
        },
        async loadData() {
            this.loading = true;
            try {
                const [sourcesMetaRes, digestRes] = await Promise.all([
                    API.get('/api/subscribe/sources-meta'),
                    API.get(`/api/subscribe/digest?time_range=${this.timeFilter}&limit=200`)
                ]);
                
                if (sourcesMetaRes.code === 200) {
                    this.sourcesMeta = sourcesMetaRes.data || [];
                    this.sources = this.sourcesMeta.map(s => s.name).filter(Boolean);
                }
                
                if (digestRes.code === 200 && digestRes.data) {
                    this.allFeeds = digestRes.data.feeds || [];
                }
                
                await this.loadSourceWeights();
            } finally {
                this.loading = false;
                this.loaded = true;
            }
        },
        async loadSourceWeights() {
            const res = await API.get('/api/subscribe/source-weights');
            if (res.code === 200) {
                const weights = res.data || {};
                this.sourcesMeta.forEach(src => {
                    const w = weights[String(src.id)];
                    this.sourceWeights[src.name] = w || 3;
                });
            }
        },
        selectSource(source) {
            this.selectedSource = source;
            this.selectedFeed = null;
        },
        selectFeed(feed) {
            this.selectedFeed = feed;
        },
        async setSourceWeight(source, weight) {
            this.sourceWeights[source] = weight;
            const srcMeta = this.sourcesMeta.find(s => s.name === source);
            if (srcMeta) {
                await API.post('/api/subscribe/source-weights', {
                    source_id: srcMeta.id,
                    weight: weight
                });
            }
        },
        openExternal(link) {
            if (link) window.open(link, '_blank');
        },
        setTimeFilter(filter) {
            this.timeFilter = filter;
            this.loadData();
        }
    },
    mounted() {
        this.loadData();
    },
    template: `
    <div class="theme-dark">
        <div class="rss-reader-container">
            
            <!-- 左侧：源列表 -->
            <div class="rss-sidebar" :class="{ collapsed: sidebarCollapsed }">
                <div class="sidebar-header">
                    <h2>订阅源</h2>
                    <button class="collapse-btn" @click="sidebarCollapsed = !sidebarCollapsed">
                        {{ sidebarCollapsed ? '→' : '←' }}
                    </button>
                </div>
                
                <div class="time-filters">
                    <button v-for="f in ['today', 'week', 'month']" 
                            :key="f"
                            class="time-filter-btn"
                            :class="{ active: timeFilter === f }"
                            @click="setTimeFilter(f)">
                        {{ f === 'today' ? '今日' : f === 'week' ? '本周' : '本月' }}
                    </button>
                </div>
                
                <div class="source-list">
                    <div class="source-item all-sources"
                         :class="{ active: !selectedSource }"
                         @click="selectSource(null)">
                        <span class="source-icon">📚</span>
                        <span class="source-name">全部内容</span>
                        <span class="feed-count">{{ allFeeds.length }}</span>
                    </div>
                    
                    <div v-for="(feeds, source) in feedsBySource" 
                         :key="source"
                         class="source-item"
                         :class="{ active: selectedSource === source }"
                         @click="selectSource(source)">
                        <span class="source-icon">{{ getSourceIcon(source) }}</span>
                        <span class="source-name">{{ source }}</span>
                        <span class="feed-count">{{ feeds.length }}</span>
                    </div>
                </div>
            </div>
            
            <!-- 中间：文章列表 -->
            <div class="rss-article-list">
                <div class="article-list-header">
                    <h3>{{ selectedSource || '全部内容' }}</h3>
                    <span class="article-count">{{ currentSourceFeeds.length }} 篇</span>
                </div>
                
                <div v-if="loading" class="loading-state">
                    <div class="loading-spinner"></div>
                    <p>加载中...</p>
                </div>
                
                <div v-else class="article-list">
                    <div v-for="feed in currentSourceFeeds" :key="feed.id"
                         class="article-item"
                         :class="{ active: selectedFeed && selectedFeed.id === feed.id }"
                         @click="selectFeed(feed)">
                        <div class="article-item-header">
                            <span class="source-badge">{{ feed.sub_name }}</span>
                            <span class="time-badge">{{ formatTime(feed.detected_at) }}</span>
                        </div>
                        <h4 class="article-title">{{ feed.title || '无标题' }}</h4>
                        <p class="article-preview">
                            {{ stripHtml(feed.summary || feed.content).substring(0, 100) }}...
                        </p>
                        <div class="weight-display-inline" v-if="sourceWeights[feed.sub_name]">
                            <span v-for="w in (sourceWeights[feed.sub_name] || 3)" :key="w" class="mini-star">⭐</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 右侧：文章详情 -->
            <div class="rss-article-detail" :class="{ 'no-selection': !selectedFeed }">
                <div v-if="!selectedFeed" class="empty-detail">
                    <div class="empty-icon">📖</div>
                    <p>选择一篇文章查看详情</p>
                </div>
                
                <div v-else class="article-detail-content">
                    <div class="detail-header">
                        <div class="detail-source">
                            <span class="source-icon">{{ getSourceIcon(selectedFeed.sub_name) }}</span>
                            <span>{{ selectedFeed.sub_name }}</span>
                        </div>
                        <div class="detail-actions">
                            <button class="action-btn" @click="openExternal(selectedFeed.link)">
                                🌐 原文
                            </button>
                        </div>
                    </div>
                    
                    <h1 class="detail-title">{{ selectedFeed.title || '无标题' }}</h1>
                    
                    <div class="detail-meta">
                        <span class="meta-item">
                            <span class="meta-icon">📅</span>
                            {{ formatTime(selectedFeed.detected_at) }}
                        </span>
                        <span v-if="selectedFeed.author" class="meta-item">
                            <span class="meta-icon">👤</span>
                            {{ selectedFeed.author }}
                        </span>
                    </div>
                    
                    <div v-if="selectedFeed.thumbnail" class="detail-thumbnail">
                        <img :src="selectedFeed.thumbnail" alt="thumbnail" @error="$event.target.style.display='none'">
                    </div>
                    
                    <div class="detail-body" v-html="selectedFeed.content || selectedFeed.summary"></div>
                    
                    <div class="detail-footer">
                        <button class="primary-btn" @click="openExternal(selectedFeed.link)">
                            查看原文
                        </button>
                    </div>
                </div>
            </div>
            
        </div>
    </div>
    `
};
