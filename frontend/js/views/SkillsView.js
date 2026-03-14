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
            sortBy: 'popular', // popular, latest, stars, downloads
            skillLevel: '',
            loading: false,
            loaded: false,
            currentAdIndex: 0,
            rankings: [],
            activeTab: 'popular', // popular, latest, all
            ads: [
                { badge: '📢 推荐', title: 'Claude Code — AI 编程助手', summary: '让 AI 帮你写代码、审查代码、重构项目，开发效率提升 10 倍', btnText: '立即体验', link: 'https://claude.ai' },
                { badge: '🔥 热门', title: 'Cursor — 下一代 AI 编辑器', summary: '内置 AI 对话，代码补全、调试、重构一站搞定', btnText: '了解更多', link: 'https://cursor.com' },
                { badge: '⚡ 新品', title: 'Vercel v0 — AI 生成前端界面', summary: '用自然语言描述需求，秒级生成 React 组件和页面', btnText: '免费试用', link: 'https://v0.dev' }
            ]
        };
    },
    computed: {
        filteredSkills() {
            let list = [...this.allSkills];
            
            console.log('=== filteredSkills 计算开始 ===');
            console.log('activeTab:', this.activeTab);
            console.log('总技能数:', list.length);
            console.log('sortBy:', this.sortBy);
            console.log('category:', this.category);
            console.log('skillLevel:', this.skillLevel);
            console.log('keyword:', this.keyword);
            
            // 按 Tab 筛选
            let tabHandledSort = false;
            if (this.activeTab === 'popular') {
                // 热门推荐：stars >= 10000，按 stars 降序
                const before = list.length;
                list = list.filter(s => s.stars && s.stars >= 10000);
                console.log('热门筛选后:', list.length, '(从', before, '筛选)');
                list.sort((a, b) => (b.stars || 0) - (a.stars || 0));
                tabHandledSort = true;
            } else if (this.activeTab === 'latest') {
                // 最新发布：按 created_at 降序
                console.log('最新发布排序');
                list.sort((a, b) => {
                    const dateA = a.created_at ? new Date(a.created_at) : new Date('2000-01-01');
                    const dateB = b.created_at ? new Date(b.created_at) : new Date('2000-01-01');
                    return dateB - dateA;
                });
                tabHandledSort = true;
            }
            // activeTab === 'all'：不过滤，由 sortBy 控制排序

            // 关键词搜索
            if (this.keyword) {
                const kw = this.keyword.toLowerCase();
                list = list.filter(s =>
                    (s.name && s.name.toLowerCase().includes(kw)) ||
                    (s.description && s.description.toLowerCase().includes(kw)) ||
                    (s.chinese_intro && s.chinese_intro.toLowerCase().includes(kw)) ||
                    (s.owner && s.owner.toLowerCase().includes(kw))
                );
                console.log('关键词筛选后:', list.length);
            }
            
            // 分类筛选
            if (this.category) {
                list = list.filter(s => s.category === this.category);
                console.log('分类筛选后:', list.length);
            }
            
            // 技能等级筛选
            if (this.skillLevel) {
                list = list.filter(s => s.skill_level === this.skillLevel);
                console.log('等级筛选后:', list.length);
            }
            
            // 排序（仅在 Tab 未处理排序时生效）
            if (!tabHandledSort) {
                console.log('sortBy 排序:', this.sortBy);
                if (this.sortBy === 'stars') {
                    list.sort((a, b) => (b.stars || 0) - (a.stars || 0));
                } else if (this.sortBy === 'downloads') {
                    list.sort((a, b) => (b.downloads || 0) - (a.downloads || 0));
                } else if (this.sortBy === 'latest') {
                    list.sort((a, b) => {
                        const dateA = a.created_at ? new Date(a.created_at) : new Date('2000-01-01');
                        const dateB = b.created_at ? new Date(b.created_at) : new Date('2000-01-01');
                        return dateB - dateA;
                    });
                } else if (this.sortBy === 'popular') {
                    // 综合评分 = stars * 0.7 + downloads * 0.3
                    list.sort((a, b) => {
                        const scoreA = (a.stars || 0) * 0.7 + (a.downloads || 0) * 0.3;
                        const scoreB = (b.stars || 0) * 0.7 + (b.downloads || 0) * 0.3;
                        return scoreB - scoreA;
                    });
                }
            }
            
            console.log('最终结果:', list.length);
            console.log('前3个:', list.slice(0, 3).map(s => s.name));
            console.log('=== filteredSkills 计算结束 ===');
            return list;
        },
        isEmpty() {
            return this.loaded && this.filteredSkills.length === 0;
        },
        currentAd() {
            return this.ads[this.currentAdIndex];
        },
        skillLevels() {
            // 提取所有技能等级
            const levels = new Set(this.allSkills.map(s => s.skill_level).filter(l => l));
            return Array.from(levels);
        },
        stats() {
            return {
                total: this.allSkills.length,
                showing: this.filteredSkills.length,
                categories: this.categories.length
            };
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
        },
        formatDate(dateStr) {
            if (!dateStr) return '';
            const date = new Date(dateStr);
            const now = new Date();
            const diff = now - date;
            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            
            if (days === 0) return 'Today';
            if (days === 1) return 'Yesterday';
            if (days < 7) return days + ' days ago';
            if (days < 30) return Math.floor(days / 7) + ' weeks ago';
            if (days < 365) return Math.floor(days / 30) + ' months ago';
            return Math.floor(days / 365) + ' years ago';
        },
        clearAllFilters() {
            this.keyword = '';
            this.category = '';
            this.skillLevel = '';
            this.sortBy = 'popular';
            this.activeTab = 'popular';
        },
        setTab(tab) {
            console.log('Setting tab to:', tab);
            this.activeTab = tab;
        },
        hasActiveFilters() {
            return this.keyword || this.category || this.skillLevel || this.sortBy !== 'popular' || this.activeTab !== 'popular';
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
        <div class="container" style="max-width:1400px;">
            <!-- Page Header -->
            <div class="page-header">
                <div class="header-top">
                    <div>
                        <h1 class="page-title">Skills 工具市场</h1>
                        <p class="page-subtitle">发现并安装适合你的 AI 助手的技能工具</p>
                    </div>
                    <div class="header-stats">
                        <div class="stat-box">
                            <span class="stat-number">{{ stats.total }}</span>
                            <span class="stat-label">总工具数</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-number">{{ stats.categories }}</span>
                            <span class="stat-label">分类数量</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Main Tabs -->
            <div class="skills-tabs">
                <button class="tab-btn" :class="{ active: activeTab === 'popular' }" @click="setTab('popular')">
                    <span class="tab-icon">🔥</span>
                    <span>热门推荐</span>
                </button>
                <button class="tab-btn" :class="{ active: activeTab === 'latest' }" @click="setTab('latest')">
                    <span class="tab-icon">✨</span>
                    <span>最新发布</span>
                </button>
                <button class="tab-btn" :class="{ active: activeTab === 'all' }" @click="setTab('all')">
                    <span class="tab-icon">📦</span>
                    <span>全部工具</span>
                </button>
            </div>

            <!-- Advanced Filters Bar -->
            <div class="advanced-filters">
                <div class="filter-section">
                    <div class="search-box">
                        <input type="text" v-model="keyword" placeholder="搜索工具名称、描述或作者..." class="search-input-large">
                    </div>
                    
                    <div class="filter-group">
                        <select v-model="category" class="filter-select">
                            <option value="">全部分类</option>
                            <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                        </select>
                        
                        <select v-model="skillLevel" class="filter-select">
                            <option value="">全部等级</option>
                            <option v-for="level in skillLevels" :key="level" :value="level">{{ level }}</option>
                        </select>
                        
                        <select v-model="sortBy" class="filter-select">
                            <option value="popular">🔥 最受欢迎</option>
                            <option value="stars">⭐ 最多星标</option>
                            <option value="downloads">📦 最多下载</option>
                            <option value="latest">🕐 最新发布</option>
                        </select>
                    </div>
                    
                    <button class="btn-clear-filters" @click="clearAllFilters" v-if="hasActiveFilters">
                        清除所有筛选
                    </button>
                </div>
                
                <div class="filter-results">
                    <span class="results-count">显示 {{ filteredSkills.length }} / {{ stats.total }} 个工具</span>
                    <span class="active-filters-tags" v-if="category || skillLevel || keyword">
                        <span v-if="category" class="filter-tag">
                            {{ category }}
                            <button @click="category = ''">×</button>
                        </span>
                        <span v-if="skillLevel" class="filter-tag">
                            {{ skillLevel }}
                            <button @click="skillLevel = ''">×</button>
                        </span>
                    </span>
                </div>
            </div>

            <!-- Main + Sidebar Layout -->
            <div class="skills-layout">
                <div class="skills-main">
                    <!-- Loading -->
                    <div v-if="loading" class="skills-grid">
                        <div v-for="i in 9" :key="i" class="skill-card">
                            <div class="loading-skeleton" style="height: 60px; width: 60px; border-radius: 12px; margin-bottom: 16px;"></div>
                            <div class="loading-skeleton" style="height: 22px; width: 70%; margin-bottom: 12px;"></div>
                            <div class="loading-skeleton" style="height: 16px; width: 90%;"></div>
                        </div>
                    </div>

                    <!-- Empty -->
                    <div v-else-if="isEmpty" class="empty-state-large">
                        <div class="empty-state-icon">🔍</div>
                        <h3>未找到相关工具</h3>
                        <p>试试调整筛选条件或搜索关键词</p>
                        <button class="btn-reset" @click="clearAllFilters">重置筛选</button>
                    </div>

                    <!-- Skills Grid -->
                    <div v-else class="skills-grid-enhanced">
                        <div v-for="s in filteredSkills" :key="s.id" class="skill-card-enhanced" @click="$router.push('/skill/' + s.id)">
                            <div class="skill-card-top">
                                <div class="skill-card-header">
                                    <span class="author-avatar-small" v-if="s.owner">
                                        <img :src="getAvatarUrl(s.owner)" :alt="s.owner" @error="handleAvatarError">
                                    </span>
                                    <div class="skill-card-info">
                                        <h3 class="skill-card-name">{{ s.name }}</h3>
                                        <p class="skill-card-owner">@{{ s.owner }}</p>
                                    </div>
                                </div>
                                <div class="skill-badges-top">
                                    <span v-if="s.stars && s.stars > 100" class="badge-highlighted">
                                        <span>⭐</span> 精选
                                    </span>
                                    <span v-if="s.skill_level" :class="['badge-level', 'badge-level-' + s.skill_level.toLowerCase()]">
                                        {{ s.skill_level }}
                                    </span>
                                </div>
                            </div>
                            
                            <p class="skill-card-desc">{{ s.chinese_intro || s.description || '暂无描述' }}</p>
                            
                            <div class="skill-card-meta">
                                <span class="skill-category-tag">{{ s.category }}</span>
                            </div>
                            
                            <div class="skill-card-stats-enhanced">
                                <div class="stat-item">
                                    <span class="stat-icon">⭐</span>
                                    <span class="stat-value">{{ formatNumber(s.stars || 0) }}</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-icon">📦</span>
                                    <span class="stat-value">{{ formatNumber(s.downloads || 0) }}</span>
                                </div>
                                <div class="stat-item" v-if="s.created_at">
                                    <span class="stat-icon">📅</span>
                                    <span class="stat-value">{{ formatDate(s.created_at) }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Ranking Sidebar -->
                <div v-if="rankings.length > 0" class="skills-sidebar">
                    <div class="hot-rank">
                        <h3 class="hot-rank-title">
                            <span class="trophy-icon">🏆</span>
                            本周热门排行
                        </h3>
                        <div class="hot-rank-list">
                            <div v-for="(item, idx) in rankings" :key="item.id" class="hot-rank-item" @click="$router.push('/skill/' + item.id)">
                                <span class="hot-rank-num" :class="'top-' + (idx + 1)">{{ idx + 1 }}</span>
                                <div style="flex:1;min-width:0;">
                                    <span class="hot-rank-title-text">{{ item.name }}</span>
                                    <div style="font-size:11px;color:#999;margin-top:2px;">
                                        ⭐ {{ item.stars }}
                                        <span v-if="item.downloads"> · 📦 {{ item.downloads }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Quick Category Filter -->
                    <div class="quick-categories">
                        <h4 class="sidebar-title">按分类浏览</h4>
                        <div class="category-cloud">
                            <span v-for="cat in categories" :key="cat" 
                                  class="category-cloud-item"
                                  :class="{ active: category === cat }"
                                  @click="category = cat">
                                {{ cat }}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `
};
