/**
 * SkillsAdmin - Skill管理（统一列表风格 v2.6.2）
 */
const SkillsAdmin = {
    data() {
        return {
            skills: [],
            categories: [],
            totalSkills: 0,
            searchKeyword: '',
            categoryFilter: '',
            showModal: false,
            editId: null,
            form: { name:'', owner:'', category:'', description:'', url:'', github_url:'', skill_level:'专业型', features:'', chinese_intro:'' }
        };
    },
    methods: {
        async loadCategories() {
            const data = await API.get('/api/admin/skills/categories');
            if (data.code === 200) this.categories = data.data || [];
        },
        async loadSkills() {
            const params = new URLSearchParams({ keyword: this.searchKeyword, category: this.categoryFilter });
            const data = await API.get('/api/admin/skills?' + params);
            if (data.code === 200) {
                this.skills = data.data || [];
                this.totalSkills = data.total || 0;
            }
        },
        showAddModal() {
            this.editId = null;
            this.form = { name:'', owner:'', category:'', description:'', url:'', github_url:'', skill_level:'专业型', features:'', chinese_intro:'' };
            this.showModal = true;
        },
        async showEditModal(id) {
            const data = await API.get('/api/admin/skills/' + id);
            if (data.code === 200) {
                const s = data.data;
                this.editId = s.id;
                this.form = {
                    name: s.name||'', owner: s.owner||'', category: s.category||'',
                    description: s.description||'', url: s.url||'', github_url: s.github_url||'',
                    skill_level: s.skill_level||'专业型', features: s.features||'', chinese_intro: s.chinese_intro||''
                };
                this.showModal = true;
            }
        },
        async saveSkill() {
            if (!this.form.name) { alert('名称不能为空'); return; }
            const payload = { ...this.form, title: this.form.name };
            let data;
            if (this.editId) {
                data = await API.put('/api/admin/skills/' + this.editId, payload);
            } else {
                data = await API.post('/api/admin/skills', payload);
            }
            if (data.code === 200) {
                this.showModal = false;
                this.loadSkills();
                this.loadCategories();
            } else {
                alert('操作失败：' + data.message);
            }
        },
        async deleteSkill(id, name) {
            if (!confirm('确定要删除 Skill "' + name + '" 吗？')) return;
            const data = await API.del('/api/admin/skills/' + id);
            if (data.code === 200) { this.loadSkills(); this.loadCategories(); }
        }
    },
    mounted() {
        this.loadCategories();
        this.loadSkills();
    },
    template: `
    <div>
        <div class="stat-cards">
            <div class="stat-card"><div class="stat-number">{{ totalSkills }}</div><div class="stat-label">总Skill数</div></div>
            <div class="stat-card"><div class="stat-number">{{ categories.length }}</div><div class="stat-label">分类数</div></div>
        </div>

        <div class="toolbar">
            <input type="text" v-model="searchKeyword" placeholder="搜索 Skill..." @keyup.enter="loadSkills"
                   style="padding:6px 12px;border:1px solid #ddd;border-radius:4px;font-size:13px;">
            <select v-model="categoryFilter" @change="loadSkills" class="filter-select">
                <option value="">全部分类</option>
                <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
            <button class="btn btn-primary btn-sm" @click="loadSkills">搜索</button>
            <button class="btn btn-success btn-sm" @click="showAddModal">+ 新增Skill</button>
        </div>

        <table class="admin-table">
            <thead>
                <tr><th>ID</th><th>名称</th><th>分类</th><th>级别</th><th>简介</th><th>创建时间</th><th>操作</th></tr>
            </thead>
            <tbody>
                <tr v-for="s in skills" :key="s.id">
                    <td>{{ s.id }}</td>
                    <td><strong>{{ s.name }}</strong></td>
                    <td><span class="badge-info">{{ s.category || '-' }}</span></td>
                    <td>{{ s.skill_level || '-' }}</td>
                    <td class="url-cell">{{ s.chinese_intro || s.description || '-' }}</td>
                    <td>{{ s.created_at || '-' }}</td>
                    <td class="actions">
                        <a href="#" @click.prevent="showEditModal(s.id)">编辑</a>
                        <a href="#" @click.prevent="deleteSkill(s.id, s.name)" class="text-danger">删除</a>
                    </td>
                </tr>
                <tr v-if="skills.length === 0">
                    <td colspan="7" style="text-align:center;color:#999;">暂无数据</td>
                </tr>
            </tbody>
        </table>

        <!-- Skill Modal -->
        <modal-dialog v-if="showModal" @close="showModal = false"
                      :title="editId ? '编辑 Skill' : '新增 Skill'">
            <div class="modal-form">
                <div class="form-group"><label>名称 *</label><input v-model="form.name" placeholder="Skill 名称"></div>
                <div class="form-group"><label>作者</label><input v-model="form.owner" placeholder="作者/组织"></div>
                <div class="form-group"><label>分类</label><input v-model="form.category" placeholder="如：代码助手、文档处理"></div>
                <div class="form-group"><label>描述</label><textarea v-model="form.description" placeholder="功能描述" rows="3"></textarea></div>
                <div class="form-group"><label>URL</label><input v-model="form.url" placeholder="https://..."></div>
                <div class="form-group"><label>GitHub URL</label><input v-model="form.github_url" placeholder="https://github.com/..."></div>
                <div class="form-group">
                    <label>级别</label>
                    <select v-model="form.skill_level">
                        <option value="专业型">专业型</option><option value="多功能">多功能</option><option value="全能型">全能型</option>
                    </select>
                </div>
                <div class="form-group"><label>功能特性</label><input v-model="form.features" placeholder="逗号分隔"></div>
                <div class="form-group"><label>中文简介</label><textarea v-model="form.chinese_intro" placeholder="中文简介" rows="3"></textarea></div>
                <div class="modal-actions">
                    <button class="btn btn-primary" @click="saveSkill">保存</button>
                    <button class="btn btn-default" @click="showModal = false">取消</button>
                </div>
            </div>
        </modal-dialog>
    </div>
    `
};
