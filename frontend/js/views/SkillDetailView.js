/**
 * SkillDetailView - Single skill detail page.
 */
const SkillDetailView = {
    data() {
        return {
            skill: null
        };
    },
    methods: {
        async loadSkill() {
            const id = this.$route.params.id;
            const data = await API.get('/api/admin/skills/' + id);
            if (data.code === 200) {
                this.skill = data.data;
            }
        }
    },
    mounted() {
        this.loadSkill();
    },
    template: `
    <div class="theme-dark">
        <div class="container" style="max-width:900px;">
            <div v-if="skill" class="skill-content">
                <h2>{{ skill.name }}</h2>
                <p>{{ skill.chinese_intro || skill.description || skill.content || '暂无内容' }}</p>
            </div>
            <div v-else style="color:#888;">加载中...</div>
        </div>
    </div>
    `
};
