/**
 * NewsDetailView - News detail page showing full article content.
 */
const NewsDetailView = {
    data() {
        return {
            news: null,
            loading: true,
            error: ''
        };
    },
    computed: {
        keywords() {
            if (!this.news || !this.news.keywords) return [];
            try {
                const parsed = JSON.parse(this.news.keywords);
                return Array.isArray(parsed) ? parsed : [];
            } catch { return []; }
        },
        formattedTime() {
            if (!this.news || !this.news.time) return '';
            return this.news.time;
        },
        readingTime() {
            if (!this.news || !this.news.content) return '1分钟';
            const len = this.news.content.length;
            return Math.max(1, Math.ceil(len / 500)) + '分钟';
        },
        contentParagraphs() {
            if (!this.news || !this.news.content) return [];
            return this.news.content.split('\n').filter(p => p.trim().length > 0);
        }
    },
    methods: {
        async loadNews() {
            this.loading = true;
            this.error = '';
            try {
                const id = this.$route.params.id;
                const data = await API.get('/api/news/' + id);
                if (data.code === 200) {
                    this.news = data.data;
                } else {
                    this.error = data.message || '新闻不存在';
                }
            } catch (e) {
                this.error = '加载失败';
            } finally {
                this.loading = false;
            }
        },
        goBack() {
            this.$router.back();
        },
        openSource() {
            if (this.news && this.news.link) {
                window.open(this.news.link, '_blank');
            }
        }
    },
    mounted() {
        this.loadNews();
    },
    watch: {
        '$route.params.id'() {
            this.loadNews();
        }
    },
    template: `
    <div class="theme-dark">
        <div class="container">
            <!-- Loading -->
            <div v-if="loading" class="news-detail-loading">
                <div class="loading-skeleton" style="height: 40px; width: 60%; margin-bottom: 20px;"></div>
                <div class="loading-skeleton" style="height: 20px; width: 40%; margin-bottom: 40px;"></div>
                <div class="loading-skeleton" style="height: 16px; width: 100%; margin-bottom: 12px;" v-for="i in 8" :key="i"></div>
            </div>

            <!-- Error -->
            <div v-else-if="error" class="news-detail-error">
                <div class="empty-state">
                    <div class="empty-state-icon">😞</div>
                    <div class="empty-state-text">{{ error }}</div>
                    <button class="hero-btn" @click="goBack" style="margin-top: 16px;">返回列表</button>
                </div>
            </div>

            <!-- Detail Content -->
            <div v-else-if="news" class="news-detail">
                <!-- Back button -->
                <div class="news-detail-nav">
                    <a class="news-detail-back" @click.prevent="goBack">&larr; 返回新闻列表</a>
                </div>

                <!-- Header -->
                <article class="news-detail-article">
                    <h1 class="news-detail-title">{{ news.title }}</h1>

                    <div class="news-detail-meta">
                        <span class="news-detail-source">{{ news.source }}</span>
                        <span class="news-detail-category" v-if="news.category">{{ news.category }}</span>
                        <span class="news-detail-time" v-if="news.time">{{ news.time }}</span>
                        <span class="news-detail-reading">约 {{ readingTime }}阅读</span>
                    </div>

                    <!-- Cover Image -->
                    <div v-if="news.image && news.image.startsWith('http')" class="news-detail-cover">
                        <img :src="news.image" :alt="news.title" @error="$event.target.style.display='none'">
                    </div>

                    <!-- Summary -->
                    <div v-if="news.summary" class="news-detail-summary">
                        {{ news.summary }}
                    </div>

                    <!-- Content -->
                    <div class="news-detail-content">
                        <p v-for="(para, idx) in contentParagraphs" :key="idx">{{ para }}</p>
                        <div v-if="contentParagraphs.length === 0" class="news-detail-no-content">
                            <p>本文内容暂未获取，请查看原文。</p>
                        </div>
                    </div>

                    <!-- Keywords -->
                    <div v-if="keywords.length > 0" class="news-detail-keywords">
                        <span v-for="kw in keywords" :key="kw" class="news-detail-kw-tag">{{ kw }}</span>
                    </div>

                    <!-- Source link -->
                    <div class="news-detail-actions">
                        <button class="hero-btn" @click="openSource">查看原文</button>
                        <button class="btn-clear" @click="goBack">返回列表</button>
                    </div>
                </article>
            </div>
        </div>
    </div>
    `
};
