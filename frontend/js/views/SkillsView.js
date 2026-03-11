/**
 * SkillsView - Skills listing page.
 */
const SkillsView = {
    data() {
        return {
            skills: []
        };
    },
    methods: {
        async loadSkills() {
            const data = await API.get('/api/skills/search');
            if (data.code === 200) {
                this.skills = data.data || [];
            }
        }
    },
    mounted() {
        this.loadSkills();
    },
    template: `
    <div class="theme-dark">
        <div class="container" style="max-width:1200px;">
            <div class="skills-grid">
                <div v-for="s in skills" :key="s.id" class="skill-card" @click="$router.push('/skill/' + s.id)">
                    <div class="skill-icon">🛠️</div>
                    <h3 class="skill-name">{{ s.name }}</h3>
                    <p class="skill-desc">{{ s.description || '暂无描述' }}</p>
                </div>
            </div>
        </div>
    </div>
    `
};
