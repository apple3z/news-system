/**
 * AdminLayout - Admin page with two-level tabs via Vue Router.
 * v2.6.2: 新增账户管理Tab、登出按钮、一级Tab改名
 */
const AdminLayout = {
    data() {
        return {
            currentUser: null
        };
    },
    async mounted() {
        // 检查登录状态
        const res = await API.get('/api/auth/me');
        if (res.code === 200) {
            this.currentUser = res.data;
            window.__currentUser = res.data;
        } else {
            this.$router.push('/sys/login');
        }
    },
    methods: {
        async logout() {
            await API.post('/api/auth/logout', {});
            window.__currentUser = null;
            this.$router.push('/sys/login');
        }
    },
    template: `
    <div class="theme-light">
        <div class="container" v-if="currentUser">
            <!-- 顶部用户栏 -->
            <div class="admin-topbar">
                <span class="admin-user">{{ currentUser.display_name || currentUser.username }}</span>
                <a href="#" @click.prevent="logout" class="admin-logout">登出</a>
            </div>

            <!-- Level 1 tabs -->
            <div class="tabs-level1">
                <router-link to="/sys/news" class="tab-l1-btn" active-class="active" :class="{ active: isCrawlerGroup }">数据采集</router-link>
                <router-link to="/sys/versions" class="tab-l1-btn" active-class="active" :class="{ active: isBaseGroup }">基础管理</router-link>
            </div>

            <!-- Level 2 tabs: Crawler group -->
            <div class="tabs-level2" v-show="isCrawlerGroup">
                <router-link to="/sys/news" class="tab-l2-btn" exact-active-class="active">采集工作台</router-link>
                <router-link to="/sys/skills" class="tab-l2-btn" exact-active-class="active">Skill管理</router-link>
                <router-link to="/sys/subscribe" class="tab-l2-btn" exact-active-class="active">订阅管理</router-link>
            </div>

            <!-- Level 2 tabs: Base group -->
            <div class="tabs-level2" v-show="isBaseGroup">
                <router-link to="/sys/versions" class="tab-l2-btn" exact-active-class="active">版本历史</router-link>
                <router-link to="/sys/docs" class="tab-l2-btn" exact-active-class="active">文档中心</router-link>
                <router-link to="/sys/accounts" class="tab-l2-btn" exact-active-class="active">账户管理</router-link>
            </div>

            <router-view></router-view>
        </div>
    </div>
    `,
    computed: {
        isCrawlerGroup() {
            const p = this.$route.path;
            return p.startsWith('/sys/news') || p.startsWith('/sys/skills') || p.startsWith('/sys/subscribe') || p === '/sys';
        },
        isBaseGroup() {
            const p = this.$route.path;
            return p.startsWith('/sys/versions') || p.startsWith('/sys/docs') || p.startsWith('/sys/accounts');
        }
    }
};
