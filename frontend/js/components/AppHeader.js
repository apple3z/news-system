/**
 * AppHeader component - shared navigation header.
 */
const AppHeader = {
    template: `
    <header class="app-header">
        <div class="header-container">
            <div class="logo" @click="$router.push('/')">
                <span class="logo-icon">⚡</span>
                <span class="logo-text">科技资讯</span>
            </div>
            <nav class="nav">
                <router-link to="/" class="nav-link" exact>科技热点</router-link>
                <router-link to="/skills" class="nav-link">Skills工具</router-link>
                <router-link to="/subscribe" class="nav-link">订阅管理</router-link>
                <router-link to="/sys" class="nav-link">后台管理</router-link>
            </nav>
        </div>
    </header>
    `
};
