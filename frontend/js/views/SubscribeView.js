/**
 * SubscribeView - Subscription listing page (public).
 */
const SubscribeView = {
    data() {
        return {
            subs: []
        };
    },
    methods: {
        async loadSubs() {
            const data = await API.get('/api/admin/subscriptions?status=all');
            if (data.code === 200) {
                this.subs = data.data || [];
            }
        },
        async deleteSub(id) {
            if (!confirm('确定删除？')) return;
            await API.del('/api/subscribe/' + id);
            this.loadSubs();
        }
    },
    mounted() {
        this.loadSubs();
    },
    template: `
    <div class="theme-dark">
        <div class="container" style="max-width:1200px;">
            <button class="add-btn" @click="$router.push('/sys/subscribe')">+ 管理订阅</button>
            <div class="sub-list">
                <div v-for="sub in subs" :key="sub.id" class="sub-card">
                    <div class="sub-info">
                        <h3>{{ sub.name }}</h3>
                        <p>URL: {{ sub.url }} | 类型: {{ sub.sub_type }} | 状态: {{ sub.is_active ? '启用' : '禁用' }}</p>
                    </div>
                    <div class="sub-actions">
                        <button class="btn-delete-dark" @click="deleteSub(sub.id)">删除</button>
                    </div>
                </div>
                <div v-if="subs.length === 0" style="color:#888;text-align:center;padding:40px;">暂无订阅</div>
            </div>
        </div>
    </div>
    `
};
