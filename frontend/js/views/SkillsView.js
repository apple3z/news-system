/**
 * SkillsView - Skills listing page with ad banner carousel, filters, and ranking sidebar.
 * v2.6.2: Added skills ranking sidebar
 */
const SkillsView = {
    data() {
        return {
            allSkills: [],
            categories: [],
            keyword: '',
            category: '',
            loading: false,
            loaded: false,
            currentAdIndex: 0,
            rankings: [],
            ads: [
                { badge: '📢 推荐', title: 'Claude Code — AI 编程助手', summary: '让 AI 帮你写代码、审查代码、重构项目，开发效率提升 10 倍', btnText: '立即体验', link: 'https://claude.ai' },
                { badge: '🔥 热门', title: 'Cursor — 下一代 AI 编辑器', summary: '内置 AI 对话，代码补全、调试、重构一站搞定', btnText: '了解更多', link: 'https://cursor.com' },
                { badge: '⚡ 新品', title: 'Vercel v0 — AI 生成前端界面', summary: '用自然语言描述需求，秒级生成 React 组件和页面', btnText: '免费试用', link: 'https://v0.dev' }
            ]
        };
    },
    computed: {
        filteredSkills() {
            let list = this.allSkills;
            if (this.keyword) {
                const kw = this.keyword.toLowerCase();
                list = list.filter(s =>
                    (s.name && s.name.toLowerCase().includes(kw)) ||
                    (s.description && s.description.toLowerCase().includes(kw))
                );
            }
            if (this.category) {
                list = list.filter(s => s.category === this.category);
            }
            return list;
        },
        isEmpty() {
            return this.loaded && this.filteredSkills.length === 0;
        },
        currentAd() {
            return this.ads[this.currentAdIndex];
        }
    },
    methods: {
        async loadSkills() {
            this.loading = true;
            try {
                const data = await API.get('/api/skills/search');
                if (data.code === 200) {
                    this.allSkills = data.data || [];
                }
            } finally {
                this.loading = false;
                this.loaded = true;
            }
        },
        async loadCategories() {
            try {
                const data = await API.get('/api/skills/categories');
                if (data.code === 200) {
                    this.categories = data.data || [];
                }
            } catch (e) {
                console.error('加载分类失败', e);
            }
        },
        async loadRankings() {
            try {
                const data = await API.get('/api/skills/rankings?limit=10');
                if (data.code === 200) {
                    this.rankings = data.data || [];
                }
            } catch (e) {
                console.error('加载排行失败', e);
            }
        },
        selectCategory(cat) {
            this.category = this.category === cat ? '' : cat;
        },
        clearFilters() {
            this.keyword = '';
            this.category = '';
        },
        nextAd() {
            this.currentAdIndex = (this.currentAdIndex + 1) % this.ads.length;
        },
        openAd(link) {
            if (link) window.open(link, '_blank');
        },
        openSource(url) {
            if (url) window.open(url, '_blank');
        },
        getAvatarUrl(owner) {
            // 使用 GitHub 风格的头像服务
            return `https://ui-avatars.com/api/?name=${encodeURIComponent(owner)}&background=random&size=32`;
        },
        handleAvatarError(e) {
            // 头像加载失败时显示默认样式
            e.target.style.display = 'none';
        },
        formatNumber(num) {
            if (num >= 1000000) {
                return (num / 1000000).toFixed(1) + 'M';
            }
            if (num >= 1000) {
                return (num / 1000).toFixed(1) + 'k';
            }
            return num.toString();
        }
    },
    mounted() {
        this.loadSkills();
        this.loadCategories();
        this.loadRankings();
        this._adTimer = setInterval(() => this.nextAd(), 5000);
    },
    beforeUnmount() {
        clearInterval(this._adTimer);
    },
    template: `
    <div class="theme-dark">
        <div class="container">
            <!-- Page Header -->
            <div class="page-header">
                <h2 class="page-title">Skills</h2>
                <p class="page-subtitle">Discover skills for your agents</p>
            </div>

            <!-- Category Tags -->
            <div class="category-tags" v-if="categories.length > 0">
                <span class="category-tag-item" :class="{ active: category === '' }" @click="category = ''">
                    All
                </span>
                <span v-for="cat in categories" :key="cat"
                      class="category-tag-item"
                      :class="{ active: category === cat }"
                      @click="selectCategory(cat)">
                    {{ cat }}
                </span>
            </div>

            <!-- Filters Bar -->
            <div class="filters-bar">
                <div class="filters-row">
                    <div class="filter-group">
                        <input type="text" v-model="keyword" placeholder="Search skills..." class="search-input">
                    </div>
                    <div class="filter-group">
                        <select v-model="category">
                            <option value="">All categories</option>
                            <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                        </select>
                    </div>
                    <button class="btn-clear" @click="clearFilters" v-if="keyword || category">Clear</button>
                </div>
            </div>

            <!-- Stats -->
            <div class="content-stats">
                <span>{{ filteredSkills.length }} skills</span>
                <span v-if="category" class="current-filter">Category: {{ category }}</span>
            </div>

            <!-- Main + Sidebar Layout -->
            <div class="news-layout">
                <div class="news-main">
                    <!-- Loading -->
                    <div v-if="loading" class="skills-grid">
                        <div v-for="i in 8" :key="i" class="skill-card">
                            <div class="loading-skeleton" style="height: 60px; width: 60px; border-radius: 12px; margin-bottom: 16px;"></div>
                            <div class="loading-skeleton" style="height: 22px; width: 70%; margin-bottom: 12px;"></div>
                            <div class="loading-skeleton" style="height: 16px; width: 90%;"></div>
                        </div>
                    </div>

                    <!-- Empty -->
                    <div v-else-if="isEmpty" class="empty-state">
                        <div class="empty-state-icon">🛠️</div>
                        <div class="empty-state-text">No skills found</div>
                        <div class="empty-state-hint">Try adjusting your filters</div>
                    </div>

                    <!-- Skills Grid -->
                    <div v-else class="skills-grid">
                        <div v-for="s in filteredSkills" :key="s.id" class="skill-card" @click="$router.push('/skill/' + s.id)">
                            <div class="skill-badge" v-if="s.stars && s.stars > 100">
                                <span>⭐ Highlighted</span>
                            </div>
                            <h3 class="skill-name">{{ s.name }}</h3>
                            <p class="skill-desc">{{ s.chinese_intro || s.description || 'A powerful skill for your agent' }}</p>
                            <div class="skill-footer">
                                <div class="skill-author">
                                    <span class="author-avatar" v-if="s.owner">
                                        <img :src="getAvatarUrl(s.owner)" :alt="s.owner" @error="handleAvatarError">
                                    </span>
                                    <span class="author-name" v-if="s.owner">@{{ s.owner }}</span>
                                </div>
                                <div class="skill-stats">
                                    <span class="skill-stat" title="Stars">
                                        <span class="stat-icon">⭐</span>
                                        <span class="stat-value">{{ formatNumber(s.stars || 0) }}</span>
                                    </span>
                                    <span class="skill-stat" title="Downloads">
                                        <span class="stat-icon">📦</span>
                                        <span class="stat-value">{{ formatNumber(s.downloads || 0) }}</span>
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Ranking Sidebar -->
                <div v-if="rankings.length > 0" class="news-sidebar">
                    <div class="hot-rank">
                        <h3 class="hot-rank-title">⭐ Popular</h3>
                        <div class="hot-rank-list">
                            <div v-for="(item, idx) in rankings" :key="item.id" class="hot-rank-item" @click="$router.push('/skill/' + item.id)">
                                <span class="hot-rank-num" :class="'top-' + (idx + 1)">{{ idx + 1 }}</span>
                                <div style="flex:1;min-width:0;">
                                    <span class="hot-rank-title-text">{{ item.name }}</span>
                                    <div style="font-size:11px;color:#999;margin-top:2px;">
                                        ⭐ {{ item.stars }}
                                        <span v-if="item.downloads"> · {{ item.downloads }} downloads</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `
};
