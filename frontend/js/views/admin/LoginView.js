/**
 * LoginView - 后台登录页面
 */
const LoginView = {
    data() {
        return {
            username: '',
            password: '',
            loading: false,
            error: ''
        };
    },
    methods: {
        async doLogin() {
            if (!this.username || !this.password) {
                this.error = '请输入用户名和密码';
                return;
            }
            this.loading = true;
            this.error = '';
            try {
                const res = await API.post('/api/auth/login', {
                    username: this.username,
                    password: this.password
                });
                if (res.code === 200) {
                    window.__currentUser = res.data;
                    this.$router.push('/sys/news');
                } else {
                    this.error = res.message || '登录失败';
                }
            } finally {
                this.loading = false;
            }
        }
    },
    template: `
    <div class="theme-light">
        <div class="login-page">
            <div class="login-card">
                <h2>后台管理</h2>
                <p class="login-subtitle">请登录以继续</p>
                <div class="login-form">
                    <div class="form-group">
                        <label>用户名</label>
                        <input v-model="username" type="text" placeholder="请输入用户名"
                               @keyup.enter="doLogin" autofocus>
                    </div>
                    <div class="form-group">
                        <label>密码</label>
                        <input v-model="password" type="password" placeholder="请输入密码"
                               @keyup.enter="doLogin">
                    </div>
                    <div v-if="error" class="login-error">{{ error }}</div>
                    <button class="btn btn-primary login-btn" @click="doLogin" :disabled="loading">
                        {{ loading ? '登录中...' : '登 录' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
    `
};
