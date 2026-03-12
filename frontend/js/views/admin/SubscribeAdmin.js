/**
 * SubscribeAdmin - 订阅管理（统一列表风格 v2.6.2）
 */
const SubscribeAdmin = {
    data() {
        return {
            subs: [],
            totalSubs: 0,
            activeSubs: 0,
            statusFilter: 'all',
            showModal: false,
            editId: null,
            form: { name:'', url:'', sub_type:'website', check_interval: 300 },
            showHistoryPanel: false,
            historyTitle: '',
            historyRows: []
        };
    },
    methods: {
        async loadSubscriptions() {
            const data = await API.get('/api/admin/subscriptions?status=' + this.statusFilter);
            if (data.code === 200) {
                this.subs = data.data || [];
                this.totalSubs = data.total || 0;
                this.activeSubs = data.active_count || 0;
            }
        },
        showAddModal() {
            this.editId = null;
            this.form = { name:'', url:'', sub_type:'website', check_interval: 300 };
            this.showModal = true;
        },
        async showEditModal(id) {
            const data = await API.get('/api/admin/subscriptions/' + id);
            if (data.code === 200) {
                const s = data.data;
                this.editId = s.id;
                this.form = { name: s.name||'', url: s.url||'', sub_type: s.sub_type||'website', check_interval: s.check_interval||300 };
                this.showModal = true;
            }
        },
        async saveSubscription() {
            if (!this.form.name || !this.form.url) { alert('名称和URL不能为空'); return; }
            let data;
            if (this.editId) {
                data = await API.put('/api/admin/subscriptions/' + this.editId, this.form);
            } else {
                data = await API.post('/api/admin/subscriptions', this.form);
            }
            if (data.code === 200) {
                this.showModal = false;
                this.loadSubscriptions();
            } else {
                alert('操作失败：' + data.message);
            }
        },
        async deleteSubscription(id, name) {
            if (!confirm('确定要删除订阅 "' + name + '" 吗？相关历史记录也会被删除。')) return;
            const data = await API.del('/api/admin/subscriptions/' + id);
            if (data.code === 200) this.loadSubscriptions();
        },
        async toggleActive(id) {
            const data = await API.put('/api/admin/subscriptions/' + id + '/toggle', {});
            if (data.code === 200) this.loadSubscriptions();
        },
        async viewHistory(id) {
            const data = await API.get('/api/admin/subscriptions/' + id + '/history');
            if (data.code === 200) {
                this.historyTitle = '更新历史 (ID: ' + id + ')';
                this.historyRows = data.data || [];
                this.showHistoryPanel = true;
            }
        },
        async triggerCheckAll() {
            if (!confirm('确定要检查所有订阅的更新吗？')) return;
            const data = await API.post('/api/admin/subscriptions/check-all', {});
            if (data.code === 200) alert('订阅检查已启动！请稍后刷新查看结果。');
            else alert('启动失败：' + data.message);
        },
        subTypeName(t) {
            return {website:'网站',rss:'RSS订阅',video:'视频',forum:'论坛'}[t] || t;
        }
    },
    mounted() {
        this.loadSubscriptions();
    },
    template: `
    <div>
        <div class="stat-cards">
            <div class="stat-card"><div class="stat-number">{{ totalSubs }}</div><div class="stat-label">总订阅数</div></div>
            <div class="stat-card"><div class="stat-number">{{ activeSubs }}</div><div class="stat-label">活跃订阅</div></div>
        </div>

        <div class="toolbar">
            <select v-model="statusFilter" @change="loadSubscriptions" class="filter-select">
                <option value="all">全部</option><option value="active">活跃</option><option value="inactive">已停用</option>
            </select>
            <button class="btn btn-success btn-sm" @click="showAddModal">+ 新增订阅</button>
            <button class="btn btn-primary btn-sm" @click="triggerCheckAll">检查更新</button>
        </div>

        <table class="admin-table">
            <thead>
                <tr><th>ID</th><th>名称</th><th>URL</th><th>类型</th><th>间隔(秒)</th><th>上次检查</th><th>状态</th><th>操作</th></tr>
            </thead>
            <tbody>
                <tr v-for="s in subs" :key="s.id">
                    <td>{{ s.id }}</td>
                    <td><strong>{{ s.name }}</strong></td>
                    <td class="url-cell" :title="s.url">{{ s.url }}</td>
                    <td><span class="badge-info">{{ subTypeName(s.sub_type) }}</span></td>
                    <td>{{ s.check_interval || 300 }}</td>
                    <td>{{ s.last_check || '-' }}</td>
                    <td>
                        <span :class="s.is_active ? 'badge-success' : 'badge-gray'" @click="toggleActive(s.id)" style="cursor:pointer">
                            {{ s.is_active ? '活跃' : '停用' }}
                        </span>
                    </td>
                    <td class="actions">
                        <a href="#" @click.prevent="showEditModal(s.id)">编辑</a>
                        <a href="#" @click.prevent="viewHistory(s.id)">历史</a>
                        <a href="#" @click.prevent="deleteSubscription(s.id, s.name)" class="text-danger">删除</a>
                    </td>
                </tr>
                <tr v-if="subs.length === 0">
                    <td colspan="8" style="text-align:center;color:#999;">暂无数据</td>
                </tr>
            </tbody>
        </table>

        <!-- History Panel -->
        <div v-if="showHistoryPanel" style="margin-top:20px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <h3>{{ historyTitle }}</h3>
                <button class="btn btn-default btn-sm" @click="showHistoryPanel = false">关闭</button>
            </div>
            <table class="admin-table">
                <thead><tr><th>ID</th><th>内容摘要</th><th>检测时间</th></tr></thead>
                <tbody>
                    <tr v-for="h in historyRows" :key="h.id">
                        <td>{{ h.id }}</td>
                        <td class="url-cell">{{ (h.content||'').substring(0,100) }}{{ (h.content||'').length > 100 ? '...' : '' }}</td>
                        <td>{{ h.detected_at || '-' }}</td>
                    </tr>
                    <tr v-if="historyRows.length === 0"><td colspan="3" style="text-align:center;color:#999;">暂无历史记录</td></tr>
                </tbody>
            </table>
        </div>

        <!-- Subscribe Modal -->
        <modal-dialog v-if="showModal" @close="showModal = false"
                      :title="editId ? '编辑订阅' : '新增订阅'">
            <div class="modal-form">
                <div class="form-group"><label>名称 *</label><input v-model="form.name" placeholder="订阅名称"></div>
                <div class="form-group"><label>URL *</label><input v-model="form.url" placeholder="https://..."></div>
                <div class="form-group">
                    <label>类型</label>
                    <select v-model="form.sub_type">
                        <option value="website">网站</option><option value="rss">RSS订阅</option>
                        <option value="video">视频</option><option value="forum">论坛</option>
                    </select>
                </div>
                <div class="form-group"><label>检查间隔（秒）</label><input type="number" v-model.number="form.check_interval" min="60"></div>
                <div class="modal-actions">
                    <button class="btn btn-primary" @click="saveSubscription">保存</button>
                    <button class="btn btn-default" @click="showModal = false">取消</button>
                </div>
            </div>
        </modal-dialog>
    </div>
    `
};
