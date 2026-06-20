/* ==========================================================================
   ATSAlign Frontend Controller (Application Orchestrations)
   ========================================================================== */

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000/api'
    : 'https://arkesh06-resume-analyzer.hf.space/api'; // Production Hugging Face Space URL

// State Management
let selectedFile = null;
let currentActiveTab = 'analyze-tab';
let historyLogs = [];

// DOM Element Registry
const elements = {
    // Navigation
    navItems: document.querySelectorAll('.nav-item'),
    tabContents: document.querySelectorAll('.tab-content'),
    pageTitle: document.getElementById('page-title'),
    pageSubtitle: document.getElementById('page-subtitle'),
    backendStatus: document.getElementById('backend-status'),
    statusIndicator: document.querySelector('.status-indicator'),
    
    // File upload & form
    dropzone: document.getElementById('resume-dropzone'),
    resumeInput: document.getElementById('resume-input'),
    filePreview: document.getElementById('file-preview'),
    previewFileName: document.getElementById('preview-file-name'),
    previewFileSize: document.getElementById('preview-file-size'),
    removeFileBtn: document.getElementById('remove-file-btn'),
    jdInput: document.getElementById('jd-input'),
    analyzeForm: document.getElementById('analyze-form'),
    analyzeSubmit: document.getElementById('analyze-submit'),
    analyzeSpinner: document.getElementById('analyze-spinner'),
    
    // Diagnostic Results Panels
    resultsPlaceholder: document.getElementById('results-placeholder'),
    resultsPanel: document.getElementById('results-panel'),
    resCandidateName: document.getElementById('res-candidate-name'),
    resEmail: document.getElementById('res-email'),
    resPhone: document.getElementById('res-phone'),
    resPredictedRole: document.getElementById('res-predicted-role'),
    resOverallScore: document.getElementById('res-overall-score'),
    scoreGauge: document.getElementById('score-gauge'),
    resCoveragePct: document.getElementById('res-coverage-pct'),
    resCoverageFill: document.getElementById('res-coverage-fill'),
    resSemanticPct: document.getElementById('res-semantic-pct'),
    resSemanticFill: document.getElementById('res-semantic-fill'),
    resRoleChart: document.getElementById('res-role-chart'),
    resSkillsCategories: document.getElementById('res-skills-categories'),
    resMatchingCount: document.getElementById('res-matching-count'),
    resMatchingSkills: document.getElementById('res-matching-skills'),
    resMissingCount: document.getElementById('res-missing-count'),
    resMissingSkills: document.getElementById('res-missing-skills'),
    
    // AI Suggestions Panel
    resAtsIssues: document.getElementById('res-ats-issues'),
    resWeakBullets: document.getElementById('res-weak-bullets'),
    resProjectImprovements: document.getElementById('res-project-improvements'),
    resActionPlan: document.getElementById('res-action-plan'),
    
    // Bullet Improver Tab
    improveForm: document.getElementById('improve-form'),
    weakStatementInput: document.getElementById('weak-statement-input'),
    targetRoleInput: document.getElementById('target-role-input'),
    improveSubmit: document.getElementById('improve-submit'),
    improveSpinner: document.getElementById('improve-spinner'),
    improveResultBox: document.getElementById('improve-result-box'),
    improvedStatementText: document.getElementById('improved-statement-text'),
    copyImprovedBtn: document.getElementById('copy-improved-btn'),
    
    // LeetCode Sync Tab
    leetcodeForm: document.getElementById('leetcode-form'),
    leetcodeUsername: document.getElementById('leetcode-username'),
    leetcodeSubmit: document.getElementById('leetcode-submit'),
    leetcodeSpinner: document.getElementById('leetcode-spinner'),
    leetcodeStatsCard: document.getElementById('leetcode-stats-card'),
    lcUsernameDisplay: document.getElementById('lc-username-display'),
    lcRank: document.getElementById('lc-rank'),
    lcReputation: document.getElementById('lc-reputation'),
    lcSolvedAll: document.getElementById('lc-solved-all'),
    lcTotalAll: document.getElementById('lc-total-all'),
    lcSolvedEasy: document.getElementById('lc-solved-easy'),
    lcTotalEasy: document.getElementById('lc-total-easy'),
    lcFillEasy: document.getElementById('lc-fill-easy'),
    lcSolvedMedium: document.getElementById('lc-solved-medium'),
    lcTotalMedium: document.getElementById('lc-total-medium'),
    lcFillMedium: document.getElementById('lc-fill-medium'),
    lcSolvedHard: document.getElementById('lc-solved-hard'),
    lcTotalHard: document.getElementById('lc-total-hard'),
    lcFillHard: document.getElementById('lc-fill-hard'),
    lcSuggestionsList: document.getElementById('lc-suggestions-list'),
    
    // History Logs Tab
    clearAllHistory: document.getElementById('clear-all-history'),
    historyFilter: document.getElementById('history-filter'),
    historyListContainer: document.getElementById('history-list-container'),
    
    // Global notification container
    notificationContainer: document.getElementById('notification-container')
};

/* ==========================================================================
   Helper Functions & Notifications
   ========================================================================== */

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = 'fa-circle-info';
    if (type === 'success') icon = 'fa-circle-check';
    if (type === 'warning') icon = 'fa-triangle-exclamation';
    if (type === 'error') icon = 'fa-circle-exclamation';
    
    toast.innerHTML = `
        <i class="fa-solid ${icon} toast-icon"></i>
        <div class="toast-content">${message}</div>
    `;
    
    elements.notificationContainer.appendChild(toast);
    
    // Animate out and remove
    setTimeout(() => {
        toast.style.transform = 'translateX(120%)';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/* ==========================================================================
   API Communications & Health Check
   ========================================================================== */

async function checkBackendHealth() {
    elements.statusIndicator.className = 'status-indicator loading';
    elements.backendStatus.textContent = 'Connecting...';
    
    try {
        const response = await fetch(`${API_BASE}/history/`, { method: 'GET' });
        if (response.ok) {
            elements.statusIndicator.className = 'status-indicator online';
            elements.backendStatus.textContent = 'Online';
            loadHistoryLogs(); // Fetch history if online
        } else {
            throw new Error();
        }
    } catch (e) {
        elements.statusIndicator.className = 'status-indicator offline';
        elements.backendStatus.textContent = 'Offline';
        showToast('Could not connect to Django backend. Ensure it is running on port 8000.', 'error');
    }
}

/* ==========================================================================
   Navigation Router
   ========================================================================== */

function switchTab(tabId) {
    elements.navItems.forEach(item => {
        if (item.getAttribute('data-tab') === tabId) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    elements.tabContents.forEach(content => {
        if (content.id === tabId) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });

    currentActiveTab = tabId;

    // Update Header texts dynamically
    switch (tabId) {
        case 'analyze-tab':
            elements.pageTitle.textContent = 'Resume Analyzer';
            elements.pageSubtitle.textContent = 'Evaluate your resume alignment against job descriptions using AI & NLP';
            break;
        case 'improve-tab':
            elements.pageTitle.textContent = 'Bullet Improver';
            elements.pageSubtitle.textContent = 'Optimize project statements for high impact metrics using STAR methodology';
            break;
        case 'leetcode-tab':
            elements.pageTitle.textContent = 'LeetCode Profile Sync';
            elements.pageSubtitle.textContent = 'Retrieve your algorithmic coding stats and suggestions';
            break;
        case 'history-tab':
            elements.pageTitle.textContent = 'Scan History Logs';
            elements.pageSubtitle.textContent = 'Inspect and review candidate resumes processed previously';
            loadHistoryLogs();
            break;
    }
}

// Bind Navigation Clicks
elements.navItems.forEach(item => {
    item.addEventListener('click', () => {
        switchTab(item.getAttribute('data-tab'));
    });
});

/* ==========================================================================
   File Drag & Drop Event Binds
   ========================================================================== */

const dropzone = elements.dropzone;

// Click dropzone to open hidden file input
dropzone.addEventListener('click', (e) => {
    // Avoid recursion if clicking remove button or browsing links
    if (e.target.closest('.remove-file-btn') || e.target.closest('.dropzone-file-preview')) return;
    elements.resumeInput.click();
});

// Sync file input selection
elements.resumeInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelection(e.target.files[0]);
    }
});

// Dragover styles
['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
    }, false);
});

// Drop handler
dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
        handleFileSelection(files[0]);
    }
});

function handleFileSelection(file) {
    if (file.type !== 'application/pdf') {
        showToast('Unsupported format! Please upload a PDF resume file.', 'error');
        return;
    }
    
    selectedFile = file;
    elements.previewFileName.textContent = file.name;
    elements.previewFileSize.textContent = formatBytes(file.size);
    
    // Toggle dropzone view state
    dropzone.querySelector('.dropzone-prompt').classList.add('hidden');
    elements.filePreview.classList.remove('hidden');
}

// Remove selected file handler
elements.removeFileBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    resetFileUpload();
});

function resetFileUpload() {
    selectedFile = null;
    elements.resumeInput.value = '';
    dropzone.querySelector('.dropzone-prompt').classList.remove('hidden');
    elements.filePreview.classList.add('hidden');
}

/* ==========================================================================
   Result Dashboard DOM Renderer
   ========================================================================== */

function renderAnalysisResults(data) {
    elements.resultsPlaceholder.classList.add('hidden');
    elements.resultsPanel.classList.remove('hidden');

    // 1. Meta Details
    elements.resCandidateName.textContent = data.candidate_name || 'Candidate Name';
    elements.resEmail.textContent = data.candidate_email || 'Not Found';
    elements.resPhone.textContent = data.candidate_phone || 'Not Found';
    
    // Predicted role
    elements.resPredictedRole.textContent = data.predicted_role;
    
    // Overall score & Radial Progress
    const overallScore = Math.round(data.overall_score || 0);
    elements.resOverallScore.textContent = overallScore;
    elements.scoreGauge.style.setProperty('--percent', overallScore);
    
    // Subscores progress fills
    elements.resCoveragePct.textContent = `${Math.round(data.skill_coverage || 0)}%`;
    elements.resCoverageFill.style.width = `${Math.round(data.skill_coverage || 0)}%`;
    
    elements.resSemanticPct.textContent = `${Math.round(data.semantic_score || 0)}%`;
    elements.resSemanticFill.style.width = `${Math.round(data.semantic_score || 0)}%`;

    // 2. Track Probabilities Chart
    elements.resRoleChart.innerHTML = '';
    if (data.role_probabilities) {
        // Sort roles so primary prediction appears top
        const roles = Object.entries(data.role_probabilities).sort((a, b) => b[1] - a[1]);
        roles.forEach(([roleName, probability], idx) => {
            const isPrimary = idx === 0;
            const barHTML = `
                <div class="role-bar-item ${isPrimary ? 'primary' : ''}">
                    <div class="role-bar-meta">
                        <span class="role-name">${roleName}</span>
                        <span class="role-pct">${probability}%</span>
                    </div>
                    <div class="role-bar-fill">
                        <div class="role-bar-progress" style="width: ${probability}%;"></div>
                    </div>
                </div>
            `;
            elements.resRoleChart.insertAdjacentHTML('beforeend', barHTML);
        });
    }

    // 3. Skill taxonomy categories
    elements.resSkillsCategories.innerHTML = '';
    if (data.skills_by_category && Object.keys(data.skills_by_category).length > 0) {
        Object.entries(data.skills_by_category).forEach(([category, skills]) => {
            const rowHTML = `
                <div class="skill-category-row">
                    <div class="cat-info">
                        <i class="fa-regular fa-folder-open cat-icon-folder"></i>
                        <span class="cat-title">${category}</span>
                    </div>
                    <span class="cat-badge">${skills.length} skills</span>
                </div>
            `;
            elements.resSkillsCategories.insertAdjacentHTML('beforeend', rowHTML);
        });
    } else {
        elements.resSkillsCategories.innerHTML = '<div class="no-skills-msg">No structured skill taxonomy extracted.</div>';
    }

    // 4. Skills badge wraps
    // Matching
    elements.resMatchingSkills.innerHTML = '';
    if (data.matching_skills && data.matching_skills.length > 0) {
        elements.resMatchingCount.textContent = data.matching_skills.length;
        data.matching_skills.forEach(skill => {
            const tag = document.createElement('span');
            tag.className = 'skill-tag match';
            tag.textContent = skill;
            elements.resMatchingSkills.appendChild(tag);
        });
    } else {
        elements.resMatchingCount.textContent = '0';
        elements.resMatchingSkills.innerHTML = '<span class="no-skills-msg">No matching skills found.</span>';
    }
    
    // Missing
    elements.resMissingSkills.innerHTML = '';
    if (data.missing_skills && data.missing_skills.length > 0) {
        elements.resMissingCount.textContent = data.missing_skills.length;
        data.missing_skills.forEach(skill => {
            const tag = document.createElement('span');
            tag.className = 'skill-tag miss';
            tag.textContent = skill;
            elements.resMissingSkills.appendChild(tag);
        });
    } else {
        elements.resMissingCount.textContent = '0';
        elements.resMissingSkills.innerHTML = '<span class="no-skills-msg">Excellent! No missing required skills.</span>';
    }

    // 5. AI Suggestions Accordions
    const feedback = data.ai_feedback || {};

    // ATS Issues
    elements.resAtsIssues.innerHTML = '';
    const atsIssues = feedback.ats_issues || [];
    if (atsIssues.length > 0) {
        atsIssues.forEach(issue => {
            const li = document.createElement('li');
            li.textContent = issue;
            elements.resAtsIssues.appendChild(li);
        });
    } else {
        elements.resAtsIssues.innerHTML = '<li><i class="fa-solid fa-circle-check" style="color:#10b981; margin-right:8px;"></i> No severe formatting flaws detected. Resume structure looks clean.</li>';
    }

    // Weak bullet comparison carousel
    elements.resWeakBullets.innerHTML = '';
    const weakBullets = feedback.weak_bullets || [];
    if (weakBullets.length > 0) {
        weakBullets.forEach(bullet => {
            const card = `
                <div class="bullet-compare-card">
                    <div class="compare-block">
                        <span class="compare-label original">Original Statement</span>
                        <p class="compare-text original">"${bullet.original}"</p>
                    </div>
                    <div class="compare-block">
                        <span class="compare-label reason">Diagnostics</span>
                        <p class="compare-text reason">${bullet.reason}</p>
                    </div>
                    <div class="compare-block">
                        <span class="compare-label improved">STAR Recommendation</span>
                        <p class="compare-text improved">"${bullet.improved}"</p>
                    </div>
                </div>
            `;
            elements.resWeakBullets.insertAdjacentHTML('beforeend', card);
        });
    } else {
        elements.resWeakBullets.innerHTML = '<div class="no-skills-msg">All resume achievements look impact-focused and numbers-driven.</div>';
    }

    // Recommended project improvements
    elements.resProjectImprovements.innerHTML = '';
    const projUpgrades = feedback.project_improvements || [];
    if (projUpgrades.length > 0) {
        projUpgrades.forEach(proj => {
            const card = `
                <div class="proj-suggest-card">
                    <div class="proj-context">${proj.current_project_context || 'System Project Context'}</div>
                    <p class="proj-suggestion-txt">${proj.suggestion}</p>
                </div>
            `;
            elements.resProjectImprovements.insertAdjacentHTML('beforeend', card);
        });
    } else {
        elements.resProjectImprovements.innerHTML = '<div class="no-skills-msg">No custom project recommendations generated.</div>';
    }

    // Action plan steps
    elements.resActionPlan.innerHTML = '';
    const actionPlan = feedback.action_plan || [];
    if (actionPlan.length > 0) {
        actionPlan.forEach(step => {
            const li = document.createElement('li');
            li.textContent = step;
            elements.resActionPlan.appendChild(li);
        });
    } else {
        elements.resActionPlan.innerHTML = '<li>Complete alignment validation by customizing keywords to suit the JD requirements.</li>';
    }
}

// Bind Accordion Toggles
document.querySelectorAll('.copilot-sec-trigger').forEach(trigger => {
    trigger.addEventListener('click', () => {
        const parent = trigger.parentElement;
        parent.classList.toggle('open');
    });
});

/* ==========================================================================
   Form Submission Event Handlers
   ========================================================================== */

// 1. Run Diagnostic Form Submit
elements.analyzeForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!selectedFile) {
        showToast('Please upload a PDF resume file first.', 'warning');
        return;
    }
    
    const jdText = elements.jdInput.value.trim();
    if (!jdText) {
        showToast('Please paste a Job Description to evaluate alignment.', 'warning');
        return;
    }

    // Loading State
    elements.analyzeSubmit.disabled = true;
    elements.analyzeSpinner.classList.remove('hidden');
    
    const formData = new FormData();
    formData.append('resume', selectedFile);
    formData.append('job_description', jdText);

    try {
        const response = await fetch(`${API_BASE}/analyze/`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            showToast('Resume alignment diagnostic completed!', 'success');
            renderAnalysisResults(result);
            loadHistoryLogs(); // Update history list
        } else {
            const err = await response.json();
            throw new Error(err.error || 'Server error occurred during processing.');
        }
    } catch (err) {
        showToast(err.message || 'Failed to submit analysis. Ensure backend is online.', 'error');
    } finally {
        elements.analyzeSubmit.disabled = false;
        elements.analyzeSpinner.classList.add('hidden');
    }
});

// 2. STAR Bullet Improver Form Submit
elements.improveForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const statement = elements.weakStatementInput.value.trim();
    const role = elements.targetRoleInput.value;
    
    if (!statement) {
        showToast('Please enter a weak project statement.', 'warning');
        return;
    }

    elements.improveSubmit.disabled = true;
    elements.improveSpinner.classList.remove('hidden');
    elements.improveResultBox.classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE}/improve-project/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                weak_statement: statement,
                target_role: role
            })
        });

        if (response.ok) {
            const data = await response.json();
            elements.improvedStatementText.textContent = data.improved_statement;
            elements.improveResultBox.classList.remove('hidden');
            showToast('Statement optimized successfully!', 'success');
        } else {
            throw new Error('Could not optimize statement.');
        }
    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        elements.improveSubmit.disabled = false;
        elements.improveSpinner.classList.add('hidden');
    }
});

// Copy to Clipboard logic for Bullet Improver
elements.copyImprovedBtn.addEventListener('click', () => {
    const text = elements.improvedStatementText.textContent.trim();
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy text.', 'error');
    });
});

// 3. LeetCode Profile Search Form Submit
elements.leetcodeForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = elements.leetcodeUsername.value.trim();
    if (!username) return;

    elements.leetcodeSubmit.disabled = true;
    elements.leetcodeSpinner.classList.remove('hidden');
    elements.leetcodeStatsCard.classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE}/leetcode/?username=${encodeURIComponent(username)}`, {
            method: 'GET'
        });

        if (response.ok) {
            const data = await response.json();
            
            // Populate card values
            elements.lcUsernameDisplay.textContent = data.username;
            elements.lcRank.textContent = (data.ranking || 0).toLocaleString();
            elements.lcReputation.textContent = data.reputation || 0;
            elements.lcSolvedAll.textContent = data.solved_all;
            elements.lcTotalAll.textContent = data.total_all;
            
            // Easy progress bar
            elements.lcSolvedEasy.textContent = data.solved_easy;
            elements.lcTotalEasy.textContent = data.total_easy;
            const easyPct = (data.solved_easy / (data.total_easy || 1)) * 100;
            elements.lcFillEasy.style.width = `${easyPct}%`;

            // Medium progress bar
            elements.lcSolvedMedium.textContent = data.solved_medium;
            elements.lcTotalMedium.textContent = data.total_medium;
            const medPct = (data.solved_medium / (data.total_medium || 1)) * 100;
            elements.lcFillMedium.style.width = `${medPct}%`;

            // Hard progress bar
            elements.lcSolvedHard.textContent = data.solved_hard;
            elements.lcTotalHard.textContent = data.total_hard;
            const hardPct = (data.solved_hard / (data.total_hard || 1)) * 100;
            elements.lcFillHard.style.width = `${hardPct}%`;

            // Suggestions List
            elements.lcSuggestionsList.innerHTML = '';
            if (data.suggestions && data.suggestions.length > 0) {
                data.suggestions.forEach(suggestion => {
                    const li = document.createElement('li');
                    li.textContent = suggestion;
                    elements.lcSuggestionsList.appendChild(li);
                });
            } else {
                elements.lcSuggestionsList.innerHTML = '<li>No specific algorithmic recommendations. Continue practicing!</li>';
            }

            elements.leetcodeStatsCard.classList.remove('hidden');
            showToast('LeetCode profile details synced!', 'success');
        } else {
            throw new Error('LeetCode profile not found or API down.');
        }
    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        elements.leetcodeSubmit.disabled = false;
        elements.leetcodeSpinner.classList.add('hidden');
    }
});

/* ==========================================================================
   History Logs Managers
   ========================================================================== */

async function loadHistoryLogs() {
    try {
        const response = await fetch(`${API_BASE}/history/`);
        if (response.ok) {
            historyLogs = await response.json();
            renderHistoryLogs(historyLogs);
        }
    } catch (e) {
        console.error('Failed to load history.', e);
    }
}

function renderHistoryLogs(logs) {
    elements.historyListContainer.innerHTML = '';
    
    if (logs.length === 0) {
        elements.historyListContainer.innerHTML = `
            <div class="history-empty-state">
                <i class="fa-solid fa-folder-open"></i>
                <p>No scanned records found in history database.</p>
            </div>
        `;
        return;
    }

    logs.forEach(log => {
        const score = Math.round(log.overall_score || 0);
        let scoreClass = 'low';
        if (score >= 80) scoreClass = 'high';
        else if (score >= 50) scoreClass = 'medium';

        // Format Date
        const dateStr = log.created_at ? new Date(log.created_at).toLocaleDateString(undefined, {
            month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
        }) : 'Recent Scan';

        const itemHTML = `
            <div class="history-item" data-id="${log.id}">
                <div class="hist-main-info">
                    <div class="hist-score-badge ${scoreClass}">${score}%</div>
                    <div class="hist-meta">
                        <span class="hist-name">${log.candidate_name}</span>
                        <div class="hist-sub">
                            <span><i class="fa-solid fa-user-gear"></i> ${log.predicted_role}</span>
                            <span><i class="fa-solid fa-calendar"></i> ${dateStr}</span>
                        </div>
                    </div>
                </div>
                <div class="hist-action">
                    <button class="delete-hist-btn" data-id="${log.id}" title="Remove record">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </div>
            </div>
        `;
        
        elements.historyListContainer.insertAdjacentHTML('beforeend', itemHTML);
    });

    // Bind click events to load individual record
    document.querySelectorAll('.history-item').forEach(item => {
        item.addEventListener('click', (e) => {
            // Prevent trigger if clicking delete button
            if (e.target.closest('.delete-hist-btn')) return;
            
            const logId = parseInt(item.getAttribute('data-id'));
            const record = historyLogs.find(l => l.id === logId);
            if (record) {
                renderAnalysisResults(record);
                switchTab('analyze-tab');
                showToast(`Loaded analysis for ${record.candidate_name}`, 'success');
            }
        });
    });

    // Bind delete single clicks
    document.querySelectorAll('.delete-hist-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const logId = btn.getAttribute('data-id');
            if (confirm('Delete this scan record permanently?')) {
                await deleteHistoryRecord(logId);
            }
        });
    });
}

// Filter History Logs Input
elements.historyFilter.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    if (!query) {
        renderHistoryLogs(historyLogs);
        return;
    }
    const filtered = historyLogs.filter(log => {
        return (log.candidate_name || '').toLowerCase().includes(query) ||
               (log.predicted_role || '').toLowerCase().includes(query) ||
               (log.overall_score || '').toString().includes(query);
    });
    renderHistoryLogs(filtered);
});

async function deleteHistoryRecord(id) {
    try {
        const response = await fetch(`${API_BASE}/history/${id}/`, {
            method: 'DELETE'
        });
        if (response.ok) {
            showToast('Scan log deleted successfully.', 'success');
            loadHistoryLogs();
        } else {
            throw new Error();
        }
    } catch (e) {
        showToast('Failed to delete history record.', 'error');
    }
}

// Clear all logs event
elements.clearAllHistory.addEventListener('click', async () => {
    if (confirm('Are you sure you want to clear the entire scan history database? This cannot be undone.')) {
        try {
            const response = await fetch(`${API_BASE}/history/`, {
                method: 'DELETE'
            });
            if (response.ok) {
                showToast('All historical scan logs cleared.', 'success');
                loadHistoryLogs();
            } else {
                throw new Error();
            }
        } catch (e) {
            showToast('Failed to clear history logs.', 'error');
        }
    }
});

/* ==========================================================================
   Init Block
   ========================================================================== */

function init() {
    checkBackendHealth();
    // Poll backend status every 15s
    setInterval(checkBackendHealth, 15000);
}

// Run Initialization
init();
