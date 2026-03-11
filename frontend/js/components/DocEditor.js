/**
 * DocEditor component - document viewer/editor with version management.
 */
const DocEditor = {
    props: {
        basePath: { type: String, required: true },
        editorId: { type: String, default: 'editor' }
    },
    data() {
        return {
            currentPath: null,
            title: '选择文档查看',
            content: '请点击左侧文档查看内容',
            version: '-',
            mtime: '-',
            author: '-',
            history: [],
            showHistory: false,
            isReadonly: true
        };
    },
    methods: {
        async loadContent(docPath) {
            this.currentPath = docPath;
            const data = await API.get('/api/v2/doc/read?path=' + encodeURIComponent(docPath));
            if (data.code === 200) {
                const docName = docPath.substring(docPath.lastIndexOf('/') + 1);
                this.title = docName.replace('.md', '');
                this.content = data.content || '无内容';
                this.version = data.version || '-';
                this.mtime = data.mtime || '-';
                this.author = data.author || '-';
                this.history = data.history || [];
                this.isReadonly = false;
            }
        },
        async save() {
            if (!this.currentPath) { alert('请先选择文档'); return; }
            const data = await API.post('/api/v2/doc/save', {
                path: this.currentPath,
                content: this.content,
                author: '管理员'
            });
            if (data.code === 200) {
                alert('保存成功！版本号：' + data.version);
                this.version = data.version;
                this.history = data.history || [];
                this.showHistory = true;
                this.loadContent(this.currentPath);
            } else {
                alert('保存失败：' + data.message);
            }
        },
        async deleteDoc() {
            if (!this.currentPath) { alert('请先选择文档'); return; }
            if (!confirm('确定要删除这个文档吗？此操作不可恢复！')) return;
            const data = await API.post('/api/v2/doc/delete', { path: this.currentPath });
            if (data.code === 200) {
                alert('删除成功！');
                this.currentPath = null;
                this.title = '选择文档查看';
                this.content = '请点击左侧文档查看内容';
                this.isReadonly = true;
                this.$emit('doc-deleted');
            } else {
                alert('删除失败：' + data.message);
            }
        },
        formatText(before, after) {
            if (this.isReadonly) { alert('请先点击编辑按钮'); return; }
            const ta = this.$refs.editorArea;
            const start = ta.selectionStart;
            const end = ta.selectionEnd;
            const selected = this.content.substring(start, end);
            this.content = this.content.substring(0, start) + before + selected + after + this.content.substring(end);
        }
    },
    emits: ['doc-deleted'],
    template: `
    <div class="editor-container">
        <div class="editor-header">
            <h3>{{ title }}</h3>
            <div>
                <button class="btn btn-danger" @click="deleteDoc">删除</button>
                <button class="btn btn-success" @click="save">保存</button>
            </div>
        </div>
        <div class="editor-toolbar">
            <button @click="formatText('**', '**')" title="粗体"><b>B</b></button>
            <button @click="formatText('*', '*')" title="斜体"><i>I</i></button>
            <button @click="formatText('## ', '')" title="标题">H</button>
            <div class="toolbar-separator"></div>
            <button @click="formatText('- ', '')" title="列表">&#8226;</button>
            <button @click="formatText('\`', '\`')" title="代码">&lt;/&gt;</button>
            <button @click="formatText('\\n\`\`\`\\n', '\\n\`\`\`\\n')" title="代码块">[&#8862;]</button>
        </div>
        <div class="editor-content">
            <textarea ref="editorArea" class="editor" v-model="content" :readonly="isReadonly"></textarea>
        </div>
        <div class="version-meta">
            <span>版本：<strong>{{ version }}</strong></span>
            <span>修改时间：<strong>{{ mtime }}</strong></span>
            <span>作者：<strong>{{ author }}</strong></span>
        </div>
        <div v-if="showHistory && history.length > 0" class="history-panel">
            <div style="font-weight:bold;margin-bottom:5px;">版本历史</div>
            <div v-for="h in history" :key="h.version" class="history-item">
                <span class="history-version">{{ h.version }}</span>
                <span class="history-time">{{ h.time }}</span> - {{ h.action || '更新' }}
            </div>
        </div>
    </div>
    `
};
