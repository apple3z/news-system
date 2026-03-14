/**
 * SubscribeDigestView - 订阅摘要视图（v2.6.6）
 * 解决信息过载问题，提供快速浏览模式
 */
const SubscribeDigestView = {
    data() {
        return {
            allFeeds: [],
            sources: [],
            sourcesMeta: [], // 源元数据（含id）
            sourceWeights: {}, // 源权重
            timeFilter: 'today', // today/week/month/all
            viewMode: 'digest', // digest/aggregated/sources
            groupedFeeds: {},
            loading: false,
            loaded: false,
            stats: {
                totalFeeds: 0,
                todayFeeds: 0,
                topSources: []
            }
        };
    },
    computed: {
        /**
         * 按源分组并排序
         */
        feedsBySource() {
            const groups = {};
            this.allFeeds.forEach(feed => {
                const source = feed.sub_name;
                if (!groups[source]) {
                    groups[source] = [];
                }
                groups[source].push(feed);
            });
            
            // 每个源按时间排序，只保留 Top 10
            Object.keys(groups).forEach(source => {
                groups[source].sort((a, b) => 
                    new Date(b.detected_at) - new Date(a.detected_at)
                );
                groups[source] = groups[source].slice(0, 10); // 每个源只显示 Top 10
            });
            
            return groups;
        },
        
        /**
         * 今日摘要：后端已按权重×时间衰减排序
         */
        digestFeeds() {
            // 后端已通过 /api/subscribe/digest 返回排好序的数据
            return this.allFeeds;
        },
        
        /**
         * 统计信息
         */
        digestStats() {
            const today = new Date().toISOString().split('T')[0];
            const todayFeeds = this.allFeeds.filter(f => 
                f.detected_at && f.detected_at.startsWith(today)
            ).length;
            
            const topSources = Object.entries(this.feedsBySource)
                .map(([name, feeds]) => ({ name, count: feeds.length }))
                .sort((a, b) => b.count - a.count)
                .slice(0, 5);
            
            return {
                totalFeeds: this.allFeeds.length,
                todayFeeds,
                topSources
            };
        }
    },
    methods: {
        /**
         * 时间评分（越近越高）
         */
        getTimeScore(dateStr) {
            if (!dateStr) return 0;
            const date = new Date(dateStr);
            const hours = (Date.now() - date) / (1000 * 60 * 60);
            // 指数衰减：1 小时内 1.0，24 小时后 0.5，7 天后 0.1
            return Math.exp(-hours / 24);
        },
        
        /**
         * 格式化时间
         */
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
            return dateStr.substring(5, 16); // MM-DD HH:mm
        },
        
        /**
         * 获取源图标
         */
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
        
        /**
         * 设置源权重（同步到后端）
         */
        async setSourceWeight(source, weight) {
            this.sourceWeights[source] = weight;
            // 找到source对应的source_id
            const srcMeta = this.sourcesMeta.find(s => s.name === source);
            if (srcMeta) {
                await API.post('/api/subscribe/source-weights', {
                    source_id: srcMeta.id,
                    weight: weight
                });
            }
            // 重新加载摘要（权重变了排序会变）
            if (this.viewMode === 'digest') {
                this.loadDigestFeeds();
            }
        },

        /**
         * 从后端加载源权重
         */
        async loadSourceWeights() {
            const res = await API.get('/api/subscribe/source-weights');
            if (res.code === 200) {
                const weights = res.data || {};
                // 将 source_id 映射到 source_name
                this.sourcesMeta.forEach(src => {
                    const w = weights[String(src.id)];
                    this.sourceWeights[src.name] = w || 3;
                });
            }
        },

        /**
         * 加载摘要内容（从后端获取已排序的数据）
         */
        async loadDigestFeeds() {
            const res = await API.get(`/api/subscribe/digest?time_range=${this.timeFilter}&limit=50`);
            if (res.code === 200 && res.data) {
                this.allFeeds = res.data.feeds || [];
                if (res.data.stats) {
                    this.stats = res.data.stats;
                }
            }
        },

        /**
         * 加载数据
         */
        async loadData() {
            this.loading = true;
            try {
                // 加载源元数据
                const sourcesMetaRes = await API.get('/api/subscribe/sources-meta');
                if (sourcesMetaRes.code === 200) {
                    this.sourcesMeta = sourcesMetaRes.data || [];
                    this.sources = this.sourcesMeta.map(s => s.name);
                    await this.loadSourceWeights();
                }

                // 加载摘要内容（后端排序）
                await this.loadDigestFeeds();
            } finally {
                this.loading = false;
                this.loaded = true;
            }
        },
        
        /**
         * 打开详情
         */
        openDetail(item) {
            this.$router.push(`/subscribe/${item.id}`);
        },
        
        /**
         * 设置时间筛选（重新从后端加载）
         */
        setTimeFilter(filter) {
            this.timeFilter = filter;
            this.loadDigestFeeds();
        },
        
        /**
         * 设置视图模式
         */
        setViewMode(mode) {
            this.viewMode = mode;
        }
    },
    mounted() {
        this.loadData();
    },
    template: `
    <div class="theme-dark">
        <div class="container" style="max-width:1400px;">
            <!-- Page Header -->
            <div class="page-header">
                <div class="header-top">
                    <div>
                        <h1 class="page-title">📊 今日摘要</h1>
                        <p class="page-subtitle">智能聚合 · 快速浏览 · 拒绝信息过载</p>
                    </div>
                    <div class="header-stats">
                        <div class="stat-box">
                            <span class="stat-number">{{ digestStats.todayFeeds }}</span>
                            <span class="stat-label">今日内容</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-number">{{ sources.length }}</span>
                            <span class="stat-label">订阅源</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-number">{{ digestFeeds.length }}</span>
                            <span class="stat-label">精选内容</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 视图切换 -->
            <div class="skills-tabs">
                <button class="tab-btn" :class="{ active: viewMode === 'digest' }" @click="setViewMode('digest')">
                    <span class="tab-icon">📝</span>
                    <span>今日摘要</span>
                </button>
                <button class="tab-btn" :class="{ active: viewMode === 'sources' }" @click="setViewMode('sources')">
                    <span class="tab-icon">📚</span>
                    <span>按源浏览</span>
                </button>
            </div>

            <!-- 时间筛选 -->
            <div class="advanced-filters">
                <div class="filter-section">
                    <div class="filter-group">
                        <select v-model="timeFilter" class="filter-select">
                            <option value="today">今日</option>
                            <option value="week">本周</option>
                            <option value="month">本月</option>
                            <option value="all">全部</option>
                        </select>
                    </div>
                    <div class="filter-results">
                        <span class="results-count">
                            {{ viewMode === 'digest' ? '精选' : '全部' }} 
                            {{ timeFilter === 'today' ? '今日' : timeFilter === 'week' ? '本周' : '' }} 
                            共 {{ viewMode === 'digest' ? digestFeeds.length : allFeeds.length }} 条
                        </span>
                    </div>
                </div>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="empty-state-large">
                <div class="loading-spinner"></div>
                <p>加载中...</p>
            </div>

            <!-- 今日摘要视图 -->
            <div v-else-if="viewMode === 'digest'" class="subscribe-digest-layout">
                <div v-for="(feed, index) in digestFeeds" :key="feed.id" 
                     class="digest-card" 
                     :class="'priority-' + (sourceWeights[feed.sub_name] || 3)"
                     @click="openDetail(feed)">
                    <div class="digest-card-header">
                        <span class="source-icon">{{ getSourceIcon(feed.sub_name) }}</span>
                        <div class="digest-card-info">
                            <h3 class="digest-card-title">{{ feed.title || '无标题' }}</h3>
                            <div class="digest-card-meta">
                                <span class="source-tag">{{ feed.sub_name }}</span>
                                <span class="time-tag">{{ formatTime(feed.detected_at) }}</span>
                                <span v-if="feed.comments" class="comments-tag">
                                    💬 {{ feed.comments }}
                                </span>
                                <span class="weight-display" :title="'优先级：' + (sourceWeights[feed.sub_name] || 3) + '星'">
                                    <span v-for="w in Math.min(sourceWeights[feed.sub_name] || 3, 3)" :key="w" class="mini-star">⭐</span>
                                </span>
                            </div>
                        </div>
                    </div>
                    <p class="digest-card-summary">
                        {{ (feed.summary || feed.content || '').replace(/<[^>]*>/g, '').substring(0, 150) }}...
                    </p>
                </div>
                
                <div v-if="digestFeeds.length === 0" class="empty-state-large">
                    <div class="empty-state-icon">📭</div>
                    <h3>暂无内容</h3>
                    <p>切换时间范围试试</p>
                </div>
            </div>

            <!-- 按源浏览视图 -->
            <div v-else-if="viewMode === 'sources'" class="subscribe-sources-layout">
                <div v-for="(feeds, source) in feedsBySource" :key="source" class="source-section">
                    <div class="source-section-header">
                        <div class="source-section-title">
                            <span class="source-icon">{{ getSourceIcon(source) }}</span>
                            <h3>{{ source }}</h3>
                            <span class="feed-count">{{ feeds.length }} 条</span>
                        </div>
                        <div class="source-weight-control">
                            <span class="weight-label">优先级:</span>
                            <button v-for="w in 5" :key="w"
                                    class="weight-star"
                                    :class="{ active: (sourceWeights[source] || 3) >= w }"
                                    @click="setSourceWeight(source, w)">
                                ⭐
                            </button>
                        </div>
                    </div>
                    <div class="source-feeds">
                        <div v-for="feed in feeds" :key="feed.id"
                             class="source-feed-item"
                             @click="openDetail(feed)">
                            <div class="source-feed-title">{{ feed.title || '无标题' }}</div>
                            <div class="source-feed-meta">
                                <span class="time-tag">{{ formatTime(feed.detected_at) }}</span>
                                <span v-if="feed.comments" class="comments-tag">💬 {{ feed.comments }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `
};
