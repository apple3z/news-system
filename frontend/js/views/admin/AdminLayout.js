/**
 * AdminLayout - Admin page with two-level tabs via Vue Router.
 */
const AdminLayout = {
    template: `
    <div class="theme-light">
        <div class="container">
            <h1>管理后台</h1>

            <!-- Level 1 tabs -->
            <div class="tabs-level1">
                <router-link to="/sys/news" class="tab-l1-btn" active-class="active" :class="{ active: isCrawlerGroup }">新闻爬虫与资讯</router-link>
                <router-link to="/sys/versions" class="tab-l1-btn" active-class="active" :class="{ active: isBaseGroup }">基础管理</router-link>
            </div>

            <!-- Level 2 tabs: Crawler group -->
            <div class="tabs-level2" v-show="isCrawlerGroup">
                <router-link to="/sys/news" class="tab-l2-btn" exact-active-class="active">新闻管理</router-link>
                <router-link to="/sys/skills" class="tab-l2-btn" exact-active-class="active">Skill管理</router-link>
                <router-link to="/sys/subscribe" class="tab-l2-btn" exact-active-class="active">订阅管理</router-link>
            </div>

            <!-- Level 2 tabs: Base group -->
            <div class="tabs-level2" v-show="isBaseGroup">
                <router-link to="/sys/versions" class="tab-l2-btn" exact-active-class="active">版本历史</router-link>
                <router-link to="/sys/docs" class="tab-l2-btn" exact-active-class="active">文档中心</router-link>
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
            return p.startsWith('/sys/versions') || p.startsWith('/sys/docs');
        }
    }
};
