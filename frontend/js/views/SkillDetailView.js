/**
 * SkillDetailView - Single skill detail page with full content, download, and source link.
 */
const SkillDetailView = {
    data() {
        return {
            skill: null,
            loading: true
        };
    },
    computed: {
        hasMetadata() {
            return this.skill && (
                this.skill.tags || 
                this.skill.languages || 
                this.skill.frameworks || 
                this.skill.tech_stack
            );
        }
    },
    methods: {
        parseList(value) {
            if (!value) return [];
            if (typeof value === 'string') {
                return value.split(',').map(item => item.trim()).filter(item => item);
            }
            if (Array.isArray(value)) {
                return value;
            }
            return [value];
        },
        async loadSkill() {
            this.loading = true;
            const id = this.$route.params.id;
            try {
                const data = await API.get('/api/skills/' + id);
                if (data.code === 200) {
                    this.skill = data.data;
                }
            } finally {
                this.loading = false;
            }
        },
        formatReadme(content) {
            if (!content) return '';
            let formatted = content
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/### (.*?)\n/g, '<h4>$1</h4>')
                .replace(/## (.*?)\n/g, '<h3>$1</h3>')
                .replace(/\n/g, '<br>');
            return formatted;
        },
        downloadSkill() {
            if (this.skill && this.skill.download_url) {
                window.open(this.skill.download_url, '_blank');
            }
        },
        openGithub() {
            if (this.skill && this.skill.github_url) {
                window.open(this.skill.github_url, '_blank');
            }
        },
        openSource() {
            if (this.skill && this.skill.url) {
                window.open(this.skill.url, '_blank');
            }
        }
    },
    mounted() {
        this.loadSkill();
    },
    template: `
    <div class="theme-dark">
        <div class="container" style="max-width:1200px;">
            <div v-if="loading" class="loading-state">
                <div class="loading-spinner"></div>
                <p>加载中...</p>
            </div>
            <div v-else-if="skill" class="skill-detail-page">
                <!-- Header Section -->
                <div class="skill-detail-header">
                    <div class="skill-title-section">
                        <h1 class="skill-detail-title">{{ skill.name }}</h1>
                        <div class="skill-badges">
                            <span v-if="skill.skill_level" class="skill-badge-type">{{ skill.skill_level }}</span>
                            <span v-if="skill.category" class="skill-badge-category">{{ skill.category }}</span>
                        </div>
                    </div>
                    <div class="skill-actions-header">
                        <button class="btn-download-primary" @click="downloadSkill" v-if="skill.download_url">
                            <span>⬇️</span> Download
                        </button>
                    </div>
                </div>

                <!-- Info Bar -->
                <div class="skill-info-bar">
                    <div class="info-item">
                        <span class="info-icon">👤</span>
                        <span class="info-label">Author</span>
                        <span class="info-value">{{ skill.owner || 'Unknown' }}</span>
                    </div>
                    <div class="info-item" v-if="skill.stars !== undefined">
                        <span class="info-icon">⭐</span>
                        <span class="info-label">Stars</span>
                        <span class="info-value">{{ skill.stars }}</span>
                    </div>
                    <div class="info-item" v-if="skill.downloads !== undefined">
                        <span class="info-icon">📦</span>
                        <span class="info-label">Downloads</span>
                        <span class="info-value">{{ skill.downloads }}</span>
                    </div>
                    <div class="info-item" v-if="skill.created_at">
                        <span class="info-icon">📅</span>
                        <span class="info-label">Created</span>
                        <span class="info-value">{{ skill.created_at }}</span>
                    </div>
                </div>

                <!-- Main Content -->
                <div class="skill-detail-content">
                    <!-- Left Sidebar - Table of Contents -->
                    <div class="skill-sidebar">
                        <div class="toc-section">
                            <h4 class="toc-title">Contents</h4>
                            <ul class="toc-list">
                                <li><a href="#overview" class="toc-link">Overview</a></li>
                                <li><a href="#metadata" class="toc-link" v-if="hasMetadata">Metadata</a></li>
                                <li><a href="#features" class="toc-link" v-if="skill.features">Features</a></li>
                                <li><a href="#capabilities" class="toc-link" v-if="skill.capabilities">Capabilities</a></li>
                                <li><a href="#implementation" class="toc-link" v-if="skill.implementation">Implementation</a></li>
                                <li><a href="#use-cases" class="toc-link" v-if="skill.use_cases">Use Cases</a></li>
                                <li><a href="#scenarios" class="toc-link" v-if="skill.scenarios">Scenarios</a></li>
                                <li><a href="#readme" class="toc-link" v-if="skill.readme_content">Documentation</a></li>
                            </ul>
                        </div>
                        
                        <div class="links-section" v-if="skill.url || skill.github_url">
                            <h4 class="toc-title">Links</h4>
                            <a :href="skill.url" target="_blank" class="external-link" v-if="skill.url">
                                <span>🌐</span> Source
                            </a>
                            <a :href="skill.github_url" target="_blank" class="external-link" v-if="skill.github_url">
                                <span>🐙</span> GitHub
                            </a>
                        </div>
                    </div>

                    <!-- Main Content Area -->
                    <div class="skill-main-content">
                        <div id="overview" class="content-section">
                            <h2 class="section-title">Overview</h2>
                            <p class="skill-description">{{ skill.chinese_intro || skill.description || 'No description available' }}</p>
                            
                            <div v-if="skill.title && skill.title !== skill.name" class="skill-title-info">
                                <strong>Full Title:</strong> {{ skill.title }}
                            </div>

                            <div v-if="skill.source" class="skill-source-info">
                                <strong>Source:</strong> {{ skill.source }}
                            </div>
                        </div>

                        <div id="metadata" class="content-section" v-if="hasMetadata">
                            <h2 class="section-title">Metadata</h2>
                            <div class="metadata-grid">
                                <div v-if="skill.tags" class="metadata-item">
                                    <span class="metadata-label">Tags</span>
                                    <div class="metadata-tags">
                                        <span v-for="(tag, idx) in parseList(skill.tags)" :key="idx" class="metadata-tag">
                                            {{ tag }}
                                        </span>
                                    </div>
                                </div>
                                <div v-if="skill.languages" class="metadata-item">
                                    <span class="metadata-label">Languages</span>
                                    <div class="metadata-tags">
                                        <span v-for="(lang, idx) in parseList(skill.languages)" :key="idx" class="metadata-tag">
                                            {{ lang }}
                                        </span>
                                    </div>
                                </div>
                                <div v-if="skill.frameworks" class="metadata-item">
                                    <span class="metadata-label">Frameworks</span>
                                    <div class="metadata-tags">
                                        <span v-for="(fw, idx) in parseList(skill.frameworks)" :key="idx" class="metadata-tag">
                                            {{ fw }}
                                        </span>
                                    </div>
                                </div>
                                <div v-if="skill.tech_stack" class="metadata-item">
                                    <span class="metadata-label">Tech Stack</span>
                                    <div class="metadata-tags">
                                        <span v-for="(tech, idx) in parseList(skill.tech_stack)" :key="idx" class="metadata-tag">
                                            {{ tech }}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div id="features" v-if="skill.features" class="content-section">
                            <h2 class="section-title">Features</h2>
                            <div class="feature-tags">
                                <span v-for="(tag, idx) in parseList(skill.features)" :key="idx" class="feature-tag">
                                    {{ tag }}
                                </span>
                            </div>
                        </div>

                        <div id="capabilities" v-if="skill.capabilities" class="content-section">
                            <h2 class="section-title">Capabilities</h2>
                            <p class="capability-text">{{ skill.capabilities }}</p>
                        </div>

                        <div id="implementation" v-if="skill.implementation" class="content-section">
                            <h2 class="section-title">Implementation</h2>
                            <p class="capability-text">{{ skill.implementation }}</p>
                        </div>

                        <div id="use-cases" v-if="skill.use_cases" class="content-section">
                            <h2 class="section-title">Use Cases</h2>
                            <p class="use-case-text">{{ skill.use_cases }}</p>
                        </div>

                        <div id="scenarios" v-if="skill.scenarios" class="content-section">
                            <h2 class="section-title">Application Scenarios</h2>
                            <p class="use-case-text">{{ skill.scenarios }}</p>
                        </div>

                        <div id="readme" v-if="skill.readme_content && skill.readme_content !== '404: Not Found'" class="content-section">
                            <h2 class="section-title">Documentation</h2>
                            <div class="readme-content" v-html="formatReadme(skill.readme_content)"></div>
                        </div>
                    </div>
                </div>
            </div>
            <div v-else class="empty-state">
                <p>Skill not found</p>
            </div>
        </div>
    </div>
    `
};
