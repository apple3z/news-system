/**
 * AccountsAdmin - 账户管理页面
 */
const AccountsAdmin = {
    data() {
        return {
            users: [],
            loading: false,
            showModal: false,
            editMode: false,
            form: { username: '', password: '', display_name: '', role: 'admin' },
            editId: null,
            showPasswordModal: false,
            passwordForm: { user_id: null, username: '', password: '' }
        };
    },
    methods: {
        async loadUsers() {
            this.loading = true;
            try {
                const res = await API.get('/api/admin/users');
                if (res.code === 200) this.users = res.data || [];
            } finally {
                this.loading = false;
            }
        },
        openCreate() {
            this.editMode = false;
            this.editId = null;
            this.form = { username: '', password: '', display_name: '', role: 'admin' };
            this.showModal = true;
        },
        openEdit(user) {
            this.editMode = true;
            this.editId = user.id;
            this.form = { username: user.username, display_name: user.display_name || '', role: user.role };
            this.showModal = true;
        },
        async saveUser() {
            if (this.editMode) {
                const res = await API.put('/api/admin/users/' + this.editId, {
                    display_name: this.form.display_name,
                    role: this.form.role
                });
                if (res.code === 200) { this.showModal = false; this.loadUsers(); }
                else alert(res.message);
            } else {
                if (!this.form.username || !this.form.password) { alert('用户名和密码必填'); return; }
                const res = await API.post('/api/admin/users', this.form);
                if (res.code === 200) { this.showModal = false; this.loadUsers(); }
                else alert(res.message);
            }
        },
        openResetPassword(user) {
            this.passwordForm = { user_id: user.id, username: user.username, password: '' };
            this.showPasswordModal = true;
        },
        async resetPassword() {
            if (!this.passwordForm.password || this.passwordForm.password.length < 6) {
                alert('密码长度至少6位'); return;
            }
            const res = await API.put('/api/admin/users/' + this.passwordForm.user_id + '/password', {
                password: this.passwordForm.password
            });
            if (res.code === 200) { this.showPasswordModal = false; alert('密码已重置'); }
            else alert(res.message);
        },
        async toggleStatus(user) {
            const newStatus = user.status === 'active' ? 'inactive' : 'active';
            const res = await API.put('/api/admin/users/' + user.id, { status: newStatus });
            if (res.code === 200) this.loadUsers();
            else alert(res.message);
        },
        async deleteUser(user) {
            if (!confirm('确定要删除用户 ' + user.username + ' 吗？')) return;
            const res = await API.del('/api/admin/users/' + user.id);
            if (res.code === 200) this.loadUsers();
            else alert(res.message);
        },
        roleLabel(role) {
            return role === 'super_admin' ? '超级管理员' : '管理员';
        }
    },
    mounted() {
        this.loadUsers();
    },
    template: `
    <div class="admin-section">
        <div class="section-header">
            <h3>账户管理</h3>
            <button class="btn btn-primary btn-sm" @click="openCreate">+ 新增账户</button>
        </div>

        <table class="admin-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>用户名</th>
                    <th>显示名</th>
                    <th>角色</th>
                    <th>状态</th>
                    <th>上次登录</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="u in users" :key="u.id">
                    <td>{{ u.id }}</td>
                    <td>{{ u.username }}</td>
                    <td>{{ u.display_name || '-' }}</td>
                    <td>{{ roleLabel(u.role) }}</td>
                    <td>
                        <span :class="u.status === 'active' ? 'badge-success' : 'badge-gray'">
                            {{ u.status === 'active' ? '启用' : '禁用' }}
                        </span>
                    </td>
                    <td>{{ u.last_login || '从未登录' }}</td>
                    <td class="actions">
                        <a href="#" @click.prevent="openEdit(u)">编辑</a>
                        <a href="#" @click.prevent="openResetPassword(u)">重置密码</a>
                        <a href="#" @click.prevent="toggleStatus(u)">{{ u.status === 'active' ? '禁用' : '启用' }}</a>
                        <a href="#" @click.prevent="deleteUser(u)" class="text-danger">删除</a>
                    </td>
                </tr>
            </tbody>
        </table>

        <!-- 新增/编辑弹窗 -->
        <modal-dialog v-if="showModal" @close="showModal = false"
                      :title="editMode ? '编辑账户' : '新增账户'">
            <div class="modal-form">
                <div class="form-group" v-if="!editMode">
                    <label>用户名</label>
                    <input v-model="form.username" placeholder="请输入用户名">
                </div>
                <div class="form-group" v-if="!editMode">
                    <label>密码</label>
                    <input v-model="form.password" type="password" placeholder="至少6位">
                </div>
                <div class="form-group">
                    <label>显示名</label>
                    <input v-model="form.display_name" placeholder="可选">
                </div>
                <div class="form-group">
                    <label>角色</label>
                    <select v-model="form.role">
                        <option value="admin">管理员</option>
                        <option value="super_admin">超级管理员</option>
                    </select>
                </div>
                <div class="modal-actions">
                    <button class="btn btn-primary" @click="saveUser">保存</button>
                    <button class="btn btn-default" @click="showModal = false">取消</button>
                </div>
            </div>
        </modal-dialog>

        <!-- 重置密码弹窗 -->
        <modal-dialog v-if="showPasswordModal" @close="showPasswordModal = false"
                      title="重置密码">
            <div class="modal-form">
                <p>为用户 <strong>{{ passwordForm.username }}</strong> 重置密码</p>
                <div class="form-group">
                    <label>新密码</label>
                    <input v-model="passwordForm.password" type="password" placeholder="至少6位">
                </div>
                <div class="modal-actions">
                    <button class="btn btn-primary" @click="resetPassword">确认重置</button>
                    <button class="btn btn-default" @click="showPasswordModal = false">取消</button>
                </div>
            </div>
        </modal-dialog>
    </div>
    `
};
