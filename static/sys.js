console.log('External JS loaded');

function toggleTree(el) {
    console.log('toggleTree called');
    el.classList.toggle('open');
    el.nextElementSibling.classList.toggle('show');
    return false;
}

// 新函数：加载版本目录下的实际文件
function loadVersionFile(versionId, filename, el) {
    console.log('loadVersionFile called:', versionId, filename);
    document.getElementById('versionPanel').style.display = 'none';
    document.getElementById('wikiPanel').style.display = 'flex';
    document.querySelectorAll('.tree-node').forEach(n => n.classList.remove('active'));
    el.classList.add('active');
    
    // 完整路径：versionId/filename (如 v2.4/需求文档.md)
    const fullPath = versionId + '/' + filename;
    currentDoc = fullPath;
    
    Promise.all([
        fetch('/api/wiki/raw/' + fullPath).then(r => r.json()),
        fetch('/api/wiki/meta/' + fullPath).then(r => r.json())
    ]).then(([data, meta]) => {
        if (data.code === 200) {
            document.getElementById('docEditor').value = data.content;
            document.getElementById('docStatus').innerText = '已加载: ' + fullPath;
            if (meta.code === 200) {
                const versionBar = document.querySelector('#wikiPanel > div:first-child');
                if (versionBar) {
                    let versionSpan = versionBar.querySelector('.version-badge');
                    if (!versionSpan) {
                        versionSpan = document.createElement('span');
                        versionSpan.className = 'version-badge';
                        versionSpan.style.cssText = 'font-size: 24px; font-weight: bold; background: linear-gradient(90deg, #00d2ff, #3a7bd5); -webkit-background-clip: text; -webkit-text-fill-color: transparent;';
                        versionBar.insertBefore(versionSpan, versionBar.firstChild);
                    }
                    versionSpan.innerText = '📋 版本: ' + meta.version;
                    const timeSpan = versionBar.querySelector('.time-badge');
                    if (timeSpan) {
                        timeSpan.innerText = '🕐 更新时间: ' + meta.mtime;
                    }
                }
                isSysLocked = meta.locked;
                updateLockButton();
            }
        } else {
            alert('文档加载失败: ' + (data.msg || '未知错误'));
        }
    }).catch(err => {
        console.error('Error loading doc:', err);
        alert('加载文档失败');
    });
}

function loadVersionDoc(versionId, docType, el) {
    console.log('loadVersionDoc called:', versionId, docType);
    document.getElementById('versionPanel').style.display = 'none';
    document.getElementById('wikiPanel').style.display = 'flex';
    document.querySelectorAll('.tree-node').forEach(n => n.classList.remove('active'));
    el.classList.add('active');
    
    const docMap = {
        'update_intro': '更新介绍.md',
        'features': '功能介绍.md',
        'bug_fix': 'BUG修复.md',
        'source_code': '源代码.md',
        'dev_plan': '研发计划.md',
        'prd': 'PRD.md',
        'arch': 'ARCH.md',
        'coding_design': '代码设计.md',
        'db_design': '数据库设计.md',
        'test_plan': '测试计划.md',
        'test_cases': '测试用例.md',
        'test_report': '测试报告.md',
        'ops_report': '运维报告.md'
    };
    
    const filename = docMap[docType] || docType + '.md';
    currentDoc = versionId + '/' + filename;
    
    Promise.all([
        fetch('/api/wiki/raw/' + filename).then(r => r.json()),
        fetch('/api/wiki/meta/' + filename).then(r => r.json())
    ]).then(([data, meta]) => {
        if (data.code === 200) {
            document.getElementById('docEditor').value = data.content;
            document.getElementById('docStatus').innerText = '已加载: ' + versionId + '/' + filename;
            if (meta.code === 200) {
                const versionBar = document.querySelector('#wikiPanel > div:first-child');
                if (versionBar) {
                    let versionSpan = versionBar.querySelector('.version-badge');
                    if (!versionSpan) {
                        versionSpan = document.createElement('span');
                        versionSpan.className = 'version-badge';
                        versionSpan.style.cssText = 'font-size: 24px; font-weight: bold; background: linear-gradient(90deg, #00d2ff, #3a7bd5); -webkit-background-clip: text; -webkit-text-fill-color: transparent;';
                        versionBar.insertBefore(versionSpan, versionBar.querySelector('button'));
                    }
                    versionSpan.innerHTML = '📋 版本: v' + meta.version;
                    let timeSpan = versionBar.querySelector('.time-badge');
                    if (!timeSpan) {
                        timeSpan = document.createElement('span');
                        timeSpan.className = 'time-badge';
                        timeSpan.style.cssText = 'font-size: 18px; color: #aaa;';
                        versionBar.insertBefore(timeSpan, versionBar.querySelector('button'));
                    }
                    timeSpan.innerHTML = '🕐 更新时间: ' + meta.mtime;
                }
                document.getElementById('docStatus').innerText = '已加载: ' + currentDoc + ' | 版本: ' + meta.version + ' | ' + meta.mtime;
            }
            history.pushState(null, '', '/sys/version/' + versionId + '/' + docType);
        } else {
            document.getElementById('docEditor').value = '版本: ' + versionId + ', 文档类型: ' + docType + '(此文档不存在于版本目录中)';
        }
    }).catch(err => {
        console.error(err);
        alert('加载失败');
    });
}

function loadDoc(filename, el) {
    console.log('loadDoc called:', filename);
    document.getElementById('versionPanel').style.display = 'none';
    document.getElementById('wikiPanel').style.display = 'flex';
    document.querySelectorAll('.tree-node').forEach(n => n.classList.remove('active'));
    el.classList.add('active');
    currentDoc = filename;
    
    Promise.all([
        fetch('/api/wiki/raw/' + filename).then(r => r.json()),
        fetch('/api/wiki/meta/' + filename).then(r => r.json())
    ]).then(([data, meta]) => {
        if (data.code === 200) {
            document.getElementById('docEditor').value = data.content;
            document.getElementById('docStatus').innerText = '已加载: ' + filename;
            if (meta.code === 200) {
                const versionBar = document.querySelector('#wikiPanel > div:first-child');
                if (versionBar) {
                    let versionSpan = versionBar.querySelector('.version-badge');
                    if (!versionSpan) {
                        versionSpan = document.createElement('span');
                        versionSpan.className = 'version-badge';
                        versionSpan.style.cssText = 'font-size: 24px; font-weight: bold; background: linear-gradient(90deg, #00d2ff, #3a7bd5); -webkit-background-clip: text; -webkit-text-fill-color: transparent;';
                        versionBar.insertBefore(versionSpan, versionBar.querySelector('button'));
                    }
                    versionSpan.innerHTML = '📋 版本: v' + meta.version;
                    let timeSpan = versionBar.querySelector('.time-badge');
                    if (!timeSpan) {
                        timeSpan = document.createElement('span');
                        timeSpan.className = 'time-badge';
                        timeSpan.style.cssText = 'font-size: 18px; color: #aaa;';
                        versionBar.insertBefore(timeSpan, versionBar.querySelector('button'));
                    }
                    timeSpan.innerHTML = '🕐 更新时间: ' + meta.mtime;
                }
                document.getElementById('docStatus').innerText = '已加载: ' + filename + ' | 版本: ' + meta.version + ' | ' + meta.mtime;
            }
            history.pushState(null, '', '/sys/wiki/' + filename);
        }
    });
}

function formatText(before, after) {
    const textarea = document.getElementById('docEditor');
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;
    const selected = text.substring(start, end);
    textarea.value = text.substring(0, start) + before + selected + after + text.substring(end);
    textarea.focus();
}

function saveDoc() {
    console.log('saveDoc called');
    const content = document.getElementById('docEditor').value;
    fetch('/api/wiki/' + currentDoc, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({content: content, locked: isSysLocked || false})
    }).then(r => r.json()).then(d => {
        if(d.code === 200) {
            alert('保存成功 ✓');
            fetch('/api/wiki/meta/' + currentDoc)
                .then(r => r.json())
                .then(meta => {
                    if (meta.code === 200) {
                        const versionBar = document.querySelector('#wikiPanel > div:first-child');
                        if (versionBar) {
                            let versionSpan = versionBar.querySelector('.version-badge');
                            if (versionSpan) versionSpan.innerHTML = '📋 版本: v' + meta.version;
                            let timeSpan = versionBar.querySelector('.time-badge');
                            if (timeSpan) timeSpan.innerHTML = '🕐 更新时间: ' + meta.mtime;
                        }
                        document.getElementById('docStatus').innerText = '已保存: ' + currentDoc + ' | 版本: ' + meta.version + ' | ' + meta.mtime;
                    }
                });
        } else {
            alert('保存失败: ' + d.msg);
        }
    });
}

function cancelEdit() {
    location.reload();
}

function toggleSysLock() {
    console.log('toggleSysLock called');
    isSysLocked = !isSysLocked;
    const btn = document.getElementById('sysLockBtn');
    if (isSysLocked) {
        btn.innerHTML = '🔓 解锁';
        btn.style.background = '#4CAF50';
    } else {
        btn.innerHTML = '🔒 锁定';
        btn.style.background = '#ff6b6b';
    }
    let lockedBadge = document.querySelector('.sys-locked-badge');
    if (lockedBadge) lockedBadge.remove();
    if (isSysLocked) {
        const versionBar = document.querySelector('#wikiPanel > div:first-child');
        const badge = document.createElement('span');
        badge.className = 'sys-locked-badge';
        badge.style.cssText = 'font-size: 18px; background: #ff6b6b; color: #fff; padding: 6px 15px; border-radius: 15px; font-weight: bold;';
        badge.innerHTML = '🔒 已锁定';
        versionBar.insertBefore(badge, btn);
    }
    alert(isSysLocked ? '文档已锁定：内容只能添加不能删减' : '文档已解锁：可以自由编辑');
}

console.log('All functions defined');

// 切换文件夹展开/折叠
function toggleFolder(element) {
    element.classList.toggle('open');
    const children = element.nextElementSibling;
    if (children && children.classList.contains('tree-children')) {
        children.classList.toggle('show');
    }
}
