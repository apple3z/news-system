/**
 * FileTree component - expandable file tree for doc browsing.
 */
const FileTree = {
    props: {
        basePath: { type: String, required: true },
        containerId: { type: String, default: '' }
    },
    emits: ['file-select'],
    data() {
        return {
            items: [],
            currentPath: this.basePath
        };
    },
    methods: {
        async loadTree(path) {
            path = path || this.basePath;
            this.currentPath = path;
            const data = await API.get('/api/v2/doc/list?path=' + encodeURIComponent(path));
            if (data.code === 200) {
                this.items = (data.data || []).map(item => ({
                    ...item,
                    open: false,
                    loaded: false,
                    children: [],
                    parentPath: path
                }));
            }
        },
        async toggleFolder(item) {
            if (item.open) {
                item.open = false;
                this.currentPath = item.parentPath;
            } else {
                item.open = true;
                const folderPath = item.parentPath + '/' + item.name;
                this.currentPath = folderPath;
                if (!item.loaded) {
                    const data = await API.get('/api/v2/doc/list?path=' + encodeURIComponent(folderPath));
                    if (data.code === 200) {
                        item.children = (data.data || []).map(child => ({
                            ...child,
                            open: false,
                            loaded: false,
                            children: [],
                            parentPath: folderPath
                        }));
                    }
                    item.loaded = true;
                }
            }
        },
        selectFile(item) {
            const filePath = item.parentPath + '/' + item.name;
            this.currentPath = item.parentPath;
            this.$emit('file-select', filePath);
        },
        async createNew() {
            const currentDir = this.currentPath || this.basePath;
            const docName = prompt('在 [' + currentDir + '] 下新建文档（不需要.md 后缀）:', '新文档');
            if (!docName) return;

            const fullPath = currentDir + '/' + docName + '.md';
            const data = await API.post('/api/v2/doc/create', {
                path: fullPath,
                content: '# ' + docName + '\n\n',
                author: '管理员'
            });
            if (data.code === 200) {
                alert('创建成功！版本号：' + data.version);
                this.loadTree(currentDir);
            } else {
                alert('创建失败：' + data.message);
            }
        }
    },
    mounted() {
        this.loadTree(this.basePath);
    },
    template: `
    <div>
        <div class="tree-section-title">
            {{ basePath }}
            <button class="btn btn-success" style="float:right;padding:2px 8px;font-size:12px;" @click="createNew">+ 新建</button>
        </div>
        <div v-if="items.length === 0" style="color:#888;font-size:0.9em;">暂无文档</div>
        <template v-for="item in items" :key="item.name">
            <div v-if="item.type === 'dir'">
                <div class="tree-folder" :class="{ open: item.open }" @click="toggleFolder(item)">
                    <span class="folder-icon">▶</span> 📁 {{ item.name }}
                </div>
                <div class="tree-children" :class="{ show: item.open }">
                    <template v-for="child in item.children" :key="child.name">
                        <div v-if="child.type === 'dir'">
                            <div class="tree-folder" :class="{ open: child.open }" @click="toggleFolder(child)">
                                <span class="folder-icon">▶</span> 📁 {{ child.name }}
                            </div>
                            <div class="tree-children" :class="{ show: child.open }">
                                <div v-for="gc in child.children" :key="gc.name" class="tree-node" @click="selectFile(gc)">
                                    📄 {{ gc.name.replace('.md', '') }}
                                </div>
                            </div>
                        </div>
                        <div v-else class="tree-node" @click="selectFile(child)">
                            📄 {{ child.name.replace('.md', '') }}
                        </div>
                    </template>
                    <div v-if="item.loaded && item.children.length === 0" style="color:#888;font-size:0.9em;padding:4px 8px;">空目录</div>
                </div>
            </div>
            <div v-else class="tree-node" @click="selectFile(item)">
                📄 {{ item.name.replace('.md', '') }}
            </div>
        </template>
    </div>
    `
};
