/**
 * Main Vue 3 application with Vue Router.
 */
const { createApp } = Vue;
const { createRouter, createWebHistory } = VueRouter;

// Define routes
const routes = [
    { path: '/', component: NewsView },
    { path: '/skills', component: SkillsView },
    { path: '/skill/:id', component: SkillDetailView },
    { path: '/subscribe', component: SubscribeView },
    {
        path: '/sys',
        component: AdminLayout,
        children: [
            { path: '', redirect: '/sys/news' },
            { path: 'news', component: NewsAdmin },
            { path: 'skills', component: SkillsAdmin },
            { path: 'subscribe', component: SubscribeAdmin },
            { path: 'versions', component: VersionsAdmin },
            { path: 'docs', component: DocsAdmin }
        ]
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

// Create and mount Vue app
const app = createApp({});

// Register global components
app.component('app-header', AppHeader);
app.component('modal-dialog', Modal);
app.component('pagination', Pagination);
app.component('file-tree', FileTree);
app.component('doc-editor', DocEditor);

app.use(router);
app.mount('#app');
