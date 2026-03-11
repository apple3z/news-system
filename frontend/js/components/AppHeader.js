/**
 * AppHeader component - shared navigation header.
 */
const AppHeader = {
    template: `
    <header style="display:flex;justify-content:space-between;align-items:center;padding:20px 0;border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:20px;">
        <h1 style="font-size:2em;background:linear-gradient(90deg,#00d2ff,#3a7bd5);-webkit-background-clip:text;-webkit-text-fill-color:transparent;cursor:pointer;" @click="$router.push('/')">AI News System</h1>
        <nav class="nav">
            <router-link to="/" class="nav-link">科技热点</router-link>
            <router-link to="/skills" class="nav-link">Skills工具</router-link>
            <router-link to="/subscribe" class="nav-link">订阅管理</router-link>
            <router-link to="/sys" class="nav-link">系统管理</router-link>
        </nav>
    </header>
    `
};
