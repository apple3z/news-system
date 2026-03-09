// Newsystem v2.5 "稳定之基" - 前端 JavaScript
// 用于系统管理页面（旧版 SYS_TPL 模板）

// 全局变量
let currentDoc = null;       // 当前编辑的文档路径
let currentVersionInfo = null; // 当前文档版本信息
let isSysLocked = false;     // 文档锁定状态

/**
 * 切换版本树展开/折叠
 */
function toggleTree(el) {
    const folder = el;
    const children = el.nextElementSibling;
    if (!children || !children.classList.contains('tree-children')) return;

    if (children.classList.contains('show')) {
        children.classList.remove('show');
        folder.classList.remove('open');
    } else {
        children.classList.add('show');
        folder.classList.add('open');
    }
}

/**
 * 加载版本历史中的文档文件
 * 由 SYS_TPL 模板中 onclick="loadVersionFile('v2.5.0', '01-规划.md', this)" 调用
 */
function loadVersionFile(versionId, filename, el) {
    // 高亮当前选中
    document.querySelectorAll('.tree-node').forEach(node => node.classList.remove('active'));
    if (el) el.classList.add('active');

    // 统一使用版本历史目录
    const filepath = `版本历史/${versionId}/${filename}`;
    loadDoc(filepath);
}

/**
 * 加载文档内容
 * 由 SYS_TPL 模板中 onclick="loadDoc('README.md', this)" 调用
 * 也由 loadVersionFile 内部调用
 */
async function loadDoc(filepath, el) {
    // 高亮（如果从文档中心点击）
    if (el) {
        document.querySelectorAll('.tree-node').forEach(node => node.classList.remove('active'));
        el.classList.add('active');
    }

    currentDoc = filepath;

    // 如果路径不以允许的目录开头，自动补 文档中心/ 前缀
    let apiPath = filepath;
    const allowedPrefixes = ['版本历史/', '文档中心/', 'docs/', '研发规范/'];
    if (!allowedPrefixes.some(p => filepath.startsWith(p))) {
        apiPath = '文档中心/' + filepath;
    }

    try {
        const encodedPath = encodeURIComponent(apiPath);
        const response = await fetch(`/api/v2/wiki/read/${encodedPath}`);
        const result = await response.json();

        if (result.code === 200) {
            // 切换面板：隐藏版本信息，显示编辑器
            const versionPanel = document.getElementById('versionPanel');
            const wikiPanel = document.getElementById('wikiPanel');
            if (versionPanel) versionPanel.style.display = 'none';
            if (wikiPanel) wikiPanel.style.display = 'flex';

            // 填充编辑器
            const editor = document.getElementById('docEditor');
            if (editor) editor.value = result.content;

            // 更新状态栏
            const docStatus = document.getElementById('docStatus');
            if (docStatus) docStatus.textContent = '已加载: ' + filepath;

            // 更新编辑器头部
            const docName = document.querySelector('.editor-doc-name');
            if (docName) docName.textContent = filepath;

            // 显示版本号
            const versionDisplay = document.getElementById('doc-version');
            if (versionDisplay && result.version) {
                versionDisplay.textContent = '版本：' + result.version;
            }

            // 显示修改时间
            const mtimeDisplay = document.getElementById('doc-mtime');
            if (mtimeDisplay && result.mtime) {
                mtimeDisplay.textContent = '修改：' + result.mtime;
            }

            // 显示作者（v2.5 Phase 6 新增）
            const authorDisplay = document.getElementById('doc-author');
            if (authorDisplay && result.author) {
                authorDisplay.textContent = '作者：' + result.author;
            }

            // 缓存版本信息
            currentVersionInfo = {
                version: result.version,
                mtime: result.mtime,
                author: result.author,
                locked: result.locked
            };

            // 显示删除按钮（v2.5 Phase 6 新增）
            const deleteBtn = document.getElementById('delete-btn');
            if (deleteBtn) {
                deleteBtn.style.display = 'inline-block';
            }
        } else {
            showToast('加载失败: ' + result.msg, 'error');
        }
    } catch (error) {
        showToast('网络错误: ' + error.message, 'error');
        console.error('[sys] 加载文档失败:', error);
    }
}

/**
 * 保存文档
 */
async function saveDoc() {
    if (!currentDoc) {
        showToast('请先选择文档', 'warning');
        return;
    }

    const editor = document.getElementById('docEditor');
    if (!editor) return;

    const content = editor.value;

    // 保存时也需要补路径前缀
    let savePath = currentDoc;
    const allowedPrefixes = ['版本历史/', '文档中心/', 'docs/', '研发规范/'];
    if (!allowedPrefixes.some(p => currentDoc.startsWith(p))) {
        savePath = '文档中心/' + currentDoc;
    }

    showToast('保存中...', 'info');

    try {
        const response = await fetch('/api/v2/doc/save', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                path: savePath,
                content: content,
                author: '张振中'
            })
        });

        const result = await response.json();

        if (result.code === 200) {
            showToast('保存成功 (版本: v' + result.version + ')', 'success');
            if (currentVersionInfo) {
                currentVersionInfo.version = result.version;
            }
        } else {
            showToast('保存失败: ' + result.msg, 'error');
        }
    } catch (error) {
        showToast('网络错误: ' + error.message, 'error');
        console.error('[sys] 保存失败:', error);
    }
}

/**
 * 删除文档（v2.5 Phase 6 新增）
 */
async function deleteDoc() {
    if (!currentDoc) {
        showToast('请先选择文档', 'warning');
        return;
    }

    // 确认对话框
    if (!confirm('确定要删除此文档吗？\n\n' + currentDoc + '\n\n此操作不可恢复！')) {
        return;
    }

    showToast('删除中...', 'info');

    // 删除时也需要补路径前缀
    let deletePath = currentDoc;
    const allowedPrefixes = ['版本历史/', '文档中心/', 'docs/', '研发规范/'];
    if (!allowedPrefixes.some(p => currentDoc.startsWith(p))) {
        deletePath = '文档中心/' + currentDoc;
    }

    try {
        const response = await fetch('/api/v2/doc/delete', {
            method: 'DELETE',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({path: deletePath})
        });

        const result = await response.json();

        if (result.code === 200) {
            showToast('删除成功', 'success');
            // 回到版本面板
            cancelEdit();
            // 清空编辑器
            const editor = document.getElementById('docEditor');
            if (editor) editor.value = '';
            // 刷新版本树（如果有的话）
            if (typeof loadVersionTree === 'function') {
                loadVersionTree();
            }
        } else {
            showToast('删除失败: ' + result.msg, 'error');
        }
    } catch (error) {
        showToast('网络错误: ' + error.message, 'error');
        console.error('[sys] 删除失败:', error);
    }
}

/**
 * 取消编辑 - 回到版本面板
 */
function cancelEdit() {
    const versionPanel = document.getElementById('versionPanel');
    const wikiPanel = document.getElementById('wikiPanel');
    if (versionPanel) versionPanel.style.display = 'block';
    if (wikiPanel) wikiPanel.style.display = 'none';
    currentDoc = null;
}

/**
 * 切换文档锁定状态
 */
function toggleSysLock() {
    isSysLocked = !isSysLocked;
    const btn = document.getElementById('sysLockBtn');
    if (btn) {
        if (isSysLocked) {
            btn.innerHTML = '🔓 解锁';
            btn.style.background = '#4CAF50';
        } else {
            btn.innerHTML = '🔒 锁定';
            btn.style.background = '#ff6b6b';
        }
    }
}

/**
 * 编辑器工具栏 - 插入格式
 */
function formatText(before, after) {
    const editor = document.getElementById('docEditor');
    if (!editor) return;

    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const selected = editor.value.substring(start, end);
    const replacement = before + selected + after;
    editor.value = editor.value.substring(0, start) + replacement + editor.value.substring(end);
    editor.focus();
    editor.selectionStart = start + before.length;
    editor.selectionEnd = start + before.length + selected.length;
}

/**
 * Toast 提示
 */
function showToast(msg, type) {
    type = type || 'info';
    const colors = {
        success: '#27ae60',
        error: '#e74c3c',
        warning: '#f39c12',
        info: '#3498db'
    };
    const toast = document.createElement('div');
    toast.style.cssText = 'position:fixed;bottom:30px;right:30px;padding:12px 24px;border-radius:8px;color:#fff;font-size:14px;z-index:10000;animation:fadeInOut 3s forwards;background:' + (colors[type] || colors.info);
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(function() {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 3000);
}
