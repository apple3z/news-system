/**
 * SubscribeDetailView - 订阅详情页
 * v2.6.2: 重构为RSS阅读器风格
 */
const SubscribeDetailView = {
    data() {
        return {
            feed: null,
            loading: true,
            error: '',
            fontSize: 16,
            showToc: false
        };
    },
    computed: {
        contentStyle() {
            return {
                fontSize: this.fontSize + 'px',
                lineHeight: (this.fontSize * 1.8) + 'px'
            };
        },
        readingTime() {
            if (!this.feed) return '1分钟';
            let text = '';
            if (this.feed.summary) text += this.feed.summary;
            if (this.feed.content) text += this.feed.content;
            const words = text.replace(/<[^>]*>/g, '').length;
            return Math.max(1, Math.ceil(words / 300)) + '分钟';
        },
        hasContent() {
            return this.feed && (this.feed.content || this.feed.summary);
        },
        getSourceIcon() {
            if (!this.feed || !this.feed.sub_name) return '📡';
            const name = this.feed.sub_name.toLowerCase();
            if (name.includes('github')) return '🐙';
            if (name.includes('twitter') || name.includes('x.com')) return '🐦';
            if (name.includes('reddit')) return '🤖';
            if (name.includes('hacker')) return '💻';
            if (name.includes('tech') || name.includes('技术')) return '🔧';
            if (name.includes('news') || name.includes('新闻')) return '📰';
            if (name.includes('blog')) return '📝';
            return '📡';
        }
    },
    methods: {
        stripHtml(html) {
            if (!html) return '';
            return html.replace(/<[^>]*>/g, '\n').replace(/\n+/g, '\n').trim();
        },
        formatContent(html) {
            if (!html) return '';
            let content = html;
            content = content.replace(/<!\[CDATA\[/g, '').replace(/\]\]>/g, '');
            return content;
        },
        async loadFeed() {
            this.loading = true;
            this.error = '';
            try {
                const id = this.$route.params.id;
                const res = await API.get('/api/subscribe/' + id);
                if (res.code === 200 && res.data) {
                    this.feed = res.data;
                } else {
                    this.error = res.message || '内容不存在';
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
            const link = this.extractArticleLink();
            if (link) {
                window.open(link, '_blank');
            }
        },
        extractArticleLink() {
            if (this.feed && this.feed.link) {
                return this.feed.link;
            }
            if (this.feed && this.feed.content) {
                const content = this.feed.content;
                const cdataLinkMatch = content.match(/<link><!\[CDATA\[([^\]]+)\]\]><\/link>/);
                if (cdataLinkMatch) {
                    return cdataLinkMatch[1].replace(/\?f=rss$/, '').replace(/\?f=feed$/, '');
                }
                const linkMatch = content.match(/<link>([^<\[]+)<\/link>/);
                if (linkMatch) {
                    return linkMatch[1].replace(/\?f=rss$/, '').replace(/\?f=feed$/, '');
                }
                const descCdataMatch = content.match(/<description><!\[CDATA\[([\s\S]*?)\]\]><\/description>/);
                if (descCdataMatch) {
                    const urlMatch = descCdataMatch[1].match(/https?:\/\/[^\s"'<>]+/);
                    if (urlMatch) {
                        return urlMatch[0].replace(/\?f=rss$/, '').replace(/\?f=feed$/, '');
                    }
                }
            }
            return this.feed?.source_url;
        },
        getTitle() {
            if (this.feed && this.feed.title) {
                const title = this.stripHtml(this.feed.title);
                if (title) return title;
            }
            if (this.feed && this.feed.content) {
                const text = this.stripHtml(this.feed.content);
                const firstLine = text.split('\n')[0].trim();
                return firstLine || '无标题';
            }
            return '无标题';
        },
        getSummary() {
            if (this.feed && this.feed.summary) {
                const summary = this.stripHtml(this.feed.summary);
                if (summary) return summary;
            }
            if (this.feed && this.feed.content) {
                const text = this.stripHtml(this.feed.content);
                const lines = text.split('\n').filter(l => l.trim());
                return lines.slice(1, 4).join(' ').trim();
            }
            return '';
        },
        formatDate(dt) {
            if (!dt) return '';
            return dt;
        },
        increaseFont() {
            if (this.fontSize < 24) this.fontSize += 2;
        },
        decreaseFont() {
            if (this.fontSize > 12) this.fontSize -= 2;
        },
        resetFont() {
            this.fontSize = 16;
        },
        shareContent() {
            const url = this.extractArticleLink() || window.location.href;
            const title = this.getTitle();
            if (navigator.share) {
                navigator.share({
                    title: title,
                    url: url
                });
            } else {
                navigator.clipboard.writeText(url).then(() => {
                    alert('链接已复制到剪贴板');
                });
            }
        }
    },
    mounted() {
        this.loadFeed();
    },
    watch: {
        '$route.params.id'() {
            this.loadFeed();
        }
    },
    template: `
    <div class="theme-dark">
        <div class="container" style="max-width:1000px;">
            <div v-if="loading" class="subscribe-detail-loading">
                <div class="loading-spinner"></div>
                <p>加载中...</p>
            </div>

            <div v-else-if="error" class="subscribe-detail-error">
                <div class="empty-state-large">
                    <div class="empty-state-icon">😞</div>
                    <h3>{{ error }}</h3>
                    <p>请返回列表页重试</p>
                    <button class="btn-reset" @click="goBack">返回列表</button>
                </div>
            </div>

            <div v-else-if="feed" class="subscribe-detail-page">
                <div class="subscribe-detail-nav">
                    <button class="btn-back" @click="goBack">
                        <span>←</span> 返回列表
                    </button>
                    <div class="reading-toolbar">
                        <button class="toolbar-btn" @click="decreaseFont" title="减小字体">A-</button>
                        <button class="toolbar-btn" @click="resetFont" title="重置字体">A</button>
                        <button class="toolbar-btn" @click="increaseFont" title="增大字体">A+</button>
                        <button class="toolbar-btn" @click="shareContent" title="分享">📤</button>
                    </div>
                </div>

                <article class="subscribe-article">
                    <header class="article-header">
                        <div class="article-source-badge">
                            <span class="source-icon">{{ getSourceIcon }}</span>
                            <span class="source-name">{{ feed.sub_name }}</span>
                        </div>
                        <h1 class="article-title">{{ getTitle() }}</h1>
                        <div class="article-meta">
                            <span class="meta-item">
                                <span class="meta-icon">📅</span>
                                <span>{{ formatDate(feed.detected_at) }}</span>
                            </span>
                            <span class="meta-item">
                                <span class="meta-icon">⏱️</span>
                                <span>约 {{ readingTime }}阅读</span>
                            </span>
                        </div>
                    </header>

                    <div v-if="getSummary()" class="article-summary">
                        <p>{{ getSummary() }}</p>
                    </div>

                    <div class="article-content" :style="contentStyle">
                        <div v-if="feed.content" v-html="formatContent(feed.content)"></div>
                        <div v-else-if="feed.summary" v-html="formatContent(feed.summary)"></div>
                        <div v-else class="article-no-content">
                            <div class="no-content-icon">📄</div>
                            <p>本文内容暂未获取</p>
                            <p class="no-content-hint">请点击下方按钮查看原文</p>
                        </div>
                    </div>

                    <footer class="article-footer">
                        <div class="footer-actions">
                            <button class="btn-primary" @click="openSource">
                                <span>🌐</span> 查看原文
                            </button>
                            <button class="btn-secondary" @click="goBack">
                                <span>←</span> 返回列表
                            </button>
                        </div>
                    </footer>
                </article>
            </div>
        </div>
    </div>
    `
};
