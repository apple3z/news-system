/**
 * VersionsAdmin - Version history management tab with file tree + editor.
 */
const VersionsAdmin = {
    data() {
        return {};
    },
    methods: {
        onFileSelect(path) {
            this.$refs.editor.loadContent(path);
        },
        onDocDeleted() {
            this.$refs.tree.loadTree('版本历史');
        }
    },
    template: `
    <div class="tree-container">
        <div class="tree-sidebar">
            <file-tree ref="tree" base-path="版本历史" @file-select="onFileSelect"></file-tree>
        </div>
        <div class="tree-content">
            <doc-editor ref="editor" base-path="版本历史" @doc-deleted="onDocDeleted"></doc-editor>
        </div>
    </div>
    `
};
