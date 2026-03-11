/**
 * DocsAdmin - Document center management tab with file tree + editor.
 */
const DocsAdmin = {
    data() {
        return {};
    },
    methods: {
        onFileSelect(path) {
            this.$refs.editor.loadContent(path);
        },
        onDocDeleted() {
            this.$refs.tree.loadTree('文档中心');
        }
    },
    template: `
    <div class="tree-container">
        <div class="tree-sidebar">
            <file-tree ref="tree" base-path="文档中心" @file-select="onFileSelect"></file-tree>
        </div>
        <div class="tree-content">
            <doc-editor ref="editor" base-path="文档中心" @doc-deleted="onDocDeleted"></doc-editor>
        </div>
    </div>
    `
};
