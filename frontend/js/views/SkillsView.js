/**
 * SkillsView - Skills listing page.
 */
const SkillsView = {
    data() {
        return {
            skills: [],
            hotSkills: [],
            loading: false,
            loaded: false,
            currentBannerIndex: 0,
            bannerSlides: []
        };
    },
    computed: {
        isEmpty() {
            return this.loaded && this.skills.length === 0;
        }
    },
    methods: {
        async loadSkills() {
            this.loading = true;
            try {
                const data = await API.get('/api/skills/search');
                if (data.code === 200) {
                    this.skills = data.data || [];
                    this.bannerSlides = this.skills.slice(0, 4);
                }
            } finally {
                this.loading = false;
                this.loaded = true;
            }
        },
        async loadHotSkills() {
            try {
                const data = await API.get('/api/skills/search?sort_by=hot_score&sort_order=desc&per_page=10');
                if (data.code === 200) {
                    this.hotSkills = data.data || [];
                }
            } catch (e) {
                console.error('加载热门失败', e);
            }
        },
        openLink(link) {
            if (link) window.open(link, '_blank');
        },
        nextBanner() {
            if (this.bannerSlides.length > 1) {
                this.currentBannerIndex = (this.currentBannerIndex + 1) % this.bannerSlides.length;
            }
        },
        prevBanner() {
            if (this.bannerSlides.length > 1) {
                this.currentBannerIndex = (this.currentBannerIndex - 1 + this.bannerSlides.length) % this.bannerSlides.length;
            }
        }
    },
    mounted() {
        this.loadSkills();
        this.loadHotSkills();
        setInterval(() => {
            if (this.bannerSlides.length > 1) {
                this.nextBanner();
            }
        }, 5000);
    },
    template: `
    <div class="theme-dark">
        <div class="container">
            <!-- Banner -->
            <div v-if="bannerSlides.length > 0" class="hero-banner">
                <div class="hero-content">
                    <div class="hero-badge">🛠️ 热门工具</div>
                    <h1 class="hero-title">{{ bannerSlides[currentBannerIndex]?.name }}</h1>
                    <p class="hero-summary">{{ bannerSlides[currentBannerIndex]?.description?.substring(0, 60) }}...</p>
                    <button class="hero-btn" @click="$router.push('/skill/' + bannerSlides[currentBannerIndex]?.id)">查看详情</button>
                    <div class="hero-dots">
                        <span v-for="(slide, idx) in bannerSlides" :key="idx" 
                              class="hero-dot" :class="{ active: idx === currentBannerIndex }"
                              @click="currentBannerIndex = idx"></span>
                    </div>
                </div>
                <div class="hero-overlay"></div>
            </div>

            <!-- Main Layout -->
            <div class="main-layout">
                <!-- Skills Grid -->
                <div class="main-content">
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
                        <div class="empty-state-text">暂无Skills</div>
                        <div class="empty-state-hint">请联系管理员添加</div>
                    </div>

                    <!-- Skills Grid -->
                    <div v-else class="skills-grid">
                        <div v-for="(s, idx) in skills" :key="s.id" class="skill-card" @click="$router.push('/skill/' + s.id)">
                            <div class="skill-card-icon">🛠️</div>
                            <h3 class="skill-card-name">{{ s.name }}</h3>
                            <p class="skill-card-desc">{{ s.description || '暂无描述' }}</p>
                            <div class="skill-card-footer">
                                <span class="skill-card-tag" v-if="s.category">{{ s.category }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Hot Ranking Sidebar -->
                <aside class="hot-sidebar" v-if="hotSkills.length > 0">
                    <div class="hot-sidebar-title">🔥 热门工具排行</div>
                    <div class="hot-rank-list">
                        <div v-for="(s, idx) in hotSkills" :key="s.id" class="hot-rank-item" @click="$router.push('/skill/' + s.id)">
                            <span class="hot-rank-num" :class="'top-' + (idx + 1)">{{ idx + 1 }}</span>
                            <span class="hot-rank-title">{{ s.name }}</span>
                        </div>
                    </div>
                </aside>
            </div>
        </div>
    </div>
    `
};
