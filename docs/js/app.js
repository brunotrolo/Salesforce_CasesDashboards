/**
 * Salesforce Dashboard - App.js
 * Carrega dados do JSONs gerados por GitHub Actions
 * Renderiza gráficos, tabelas e métricas em tempo real
 */

// Configuração
const config = {
    dataDir: './data/',
    refreshInterval: 5 * 60 * 1000, // 5 minutos
    charts: {}
};

/**
 * Carregar dados do Salesforce
 */
async function loadSalesforceData() {
    try {
        updateSyncStatus('syncing');

        const [casesResp, reportsResp, accountsResp, metaResp] = await Promise.all([
            fetch(config.dataDir + 'cases.json?t=' + Date.now()),
            fetch(config.dataDir + 'reports.json?t=' + Date.now()),
            fetch(config.dataDir + 'accounts.json?t=' + Date.now()),
            fetch(config.dataDir + 'metadata.json?t=' + Date.now())
        ]);

        if (!casesResp.ok || !reportsResp.ok || !accountsResp.ok) {
            throw new Error('Erro ao carregar dados');
        }

        const cases = await casesResp.json();
        const reports = await reportsResp.json();
        const accounts = await accountsResp.json();
        const metadata = await metaResp.json();

        // Atualizar UI
        updateMetadata(metadata);
        updateCounts(cases, reports, accounts);
        renderCasesTable(cases.records);
        renderReportsTable(reports.records);
        renderAccountsTable(accounts.records);
        renderCharts(cases.records, accounts.records);

        updateSyncStatus(metadata.isLive ? 'success' : 'fallback');

    } catch (error) {
        console.error('❌ Erro ao carregar dados:', error);
        updateSyncStatus('error');
    }
}

/**
 * Atualizar metadata (timestamp, etc)
 */
function updateMetadata(metadata) {
    const lastSyncEl = document.getElementById('lastSync');
    const dataSourceEl = document.getElementById('dataSource');

    const lastSync = new Date(metadata.lastSync);
    lastSyncEl.textContent = lastSync.toLocaleString('pt-BR');

    dataSourceEl.textContent = metadata.isLive
        ? '✅ Salesforce (LIVE via MCP)'
        : '📦 Dados de Fallback';

    dataSourceEl.className = metadata.isLive ? 'text-mono' : 'text-mono error';
}

/**
 * Atualizar contadores
 */
function updateCounts(cases, reports, accounts) {
    document.getElementById('caseCount').textContent = cases.total;
    document.getElementById('reportCount').textContent = reports.total;
    document.getElementById('accountCount').textContent = accounts.total;
    document.getElementById('casesCount').textContent = `${cases.total} registros`;
    document.getElementById('reportsCount').textContent = `${reports.total} registros`;
    document.getElementById('accountsCount').textContent = `${accounts.total} registros`;
}

/**
 * Renderizar tabela de Cases
 */
function renderCasesTable(cases) {
    const tbody = document.querySelector('#casesTable tbody');

    if (!cases || cases.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Nenhum case disponível</td></tr>';
        return;
    }

    tbody.innerHTML = cases.slice(0, 20).map(c => `
        <tr>
            <td><strong>${escapeHtml(c.number)}</strong></td>
            <td>${escapeHtml(c.subject)}</td>
            <td>
                <span class="badge ${getNormalizedStatus(c.status)}">
                    ${escapeHtml(c.status)}
                </span>
            </td>
            <td>
                <span class="badge ${getNormalizedPriority(c.priority)}">
                    ${escapeHtml(c.priority)}
                </span>
            </td>
            <td>${escapeHtml(c.owner)}</td>
            <td>${formatDate(c.created)}</td>
        </tr>
    `).join('');
}

/**
 * Renderizar tabela de Reports
 */
function renderReportsTable(reports) {
    const tbody = document.querySelector('#reportsTable tbody');

    if (!reports || reports.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Nenhum relatório disponível</td></tr>';
        return;
    }

    tbody.innerHTML = reports.slice(0, 15).map(r => `
        <tr>
            <td><strong>${escapeHtml(r.name)}</strong></td>
            <td>${escapeHtml(r.description || '-')}</td>
            <td>${escapeHtml(r.createdBy)}</td>
            <td>${formatDate(r.created)}</td>
        </tr>
    `).join('');
}

/**
 * Renderizar tabela de Accounts
 */
function renderAccountsTable(accounts) {
    const tbody = document.querySelector('#accountsTable tbody');

    if (!accounts || accounts.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Nenhuma conta disponível</td></tr>';
        return;
    }

    tbody.innerHTML = accounts.slice(0, 15).map(a => `
        <tr>
            <td><strong>${escapeHtml(a.name)}</strong></td>
            <td>${escapeHtml(a.industry || '-')}</td>
            <td>${formatCurrency(a.revenue)}</td>
            <td>${formatDate(a.created)}</td>
        </tr>
    `).join('');
}

/**
 * Renderizar gráficos com Chart.js
 */
function renderCharts(cases, accounts) {
    // 1. Status Distribution
    renderCaseStatusChart(cases);

    // 2. Priority Distribution
    renderPriorityChart(cases);

    // 3. Case Trend (por dia)
    renderTrendChart(cases);

    // 4. Top Accounts
    renderAccountsChart(accounts);
}

/**
 * Gráfico: Cases por Status
 */
function renderCaseStatusChart(cases) {
    const ctx = document.getElementById('caseStatusChart');
    if (!ctx) return;

    // Contar por status
    const statusCount = {};
    cases.forEach(c => {
        const status = c.status || 'Unknown';
        statusCount[status] = (statusCount[status] || 0) + 1;
    });

    if (config.charts.statusChart) {
        config.charts.statusChart.destroy();
    }

    config.charts.statusChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(statusCount),
            datasets: [{
                data: Object.values(statusCount),
                backgroundColor: [
                    '#3b82f6', // New - Blue
                    '#10b981', // In Progress - Green
                    '#f59e0b', // On Hold - Amber
                    '#ef4444'  // Closed - Red
                ],
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: { size: 12 },
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (ctx) {
                            const label = ctx.label || '';
                            const value = ctx.parsed || 0;
                            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            const percent = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percent}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Gráfico: Prioridade dos Cases
 */
function renderPriorityChart(cases) {
    const ctx = document.getElementById('casePriorityChart');
    if (!ctx) return;

    // Contar por prioridade
    const priorityCount = {};
    cases.forEach(c => {
        const priority = c.priority || 'Unknown';
        priorityCount[priority] = (priorityCount[priority] || 0) + 1;
    });

    if (config.charts.priorityChart) {
        config.charts.priorityChart.destroy();
    }

    config.charts.priorityChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(priorityCount).sort(),
            datasets: [{
                label: 'Quantidade',
                data: Object.values(priorityCount),
                backgroundColor: '#6366f1',
                borderRadius: 4,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: true,
                    labels: { padding: 15 }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
}

/**
 * Gráfico: Tendência de Cases (últimos 15 dias)
 */
function renderTrendChart(cases) {
    const ctx = document.getElementById('caseTrendChart');
    if (!ctx) return;

    // Agrupar por data
    const dailyCounts = {};
    const today = new Date();

    // Inicializar últimos 15 dias
    for (let i = 14; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        const dateKey = date.toLocaleDateString('pt-BR');
        dailyCounts[dateKey] = 0;
    }

    // Contar casos por data
    cases.forEach(c => {
        const date = new Date(c.created);
        const dateKey = date.toLocaleDateString('pt-BR');
        if (dateKey in dailyCounts) {
            dailyCounts[dateKey]++;
        }
    });

    if (config.charts.trendChart) {
        config.charts.trendChart.destroy();
    }

    config.charts.trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Object.keys(dailyCounts),
            datasets: [{
                label: 'Cases Criados',
                data: Object.values(dailyCounts),
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: '#667eea'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    labels: { padding: 15 }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
}

/**
 * Gráfico: Top Accounts (por receita)
 */
function renderAccountsChart(accounts) {
    const ctx = document.getElementById('topAccountsChart');
    if (!ctx) return;

    // Top 10 accounts por receita
    const topAccounts = accounts
        .filter(a => a.revenue > 0)
        .sort((a, b) => b.revenue - a.revenue)
        .slice(0, 10);

    if (config.charts.accountsChart) {
        config.charts.accountsChart.destroy();
    }

    config.charts.accountsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topAccounts.map(a => truncateString(a.name, 20)),
            datasets: [{
                label: 'Receita (US$)',
                data: topAccounts.map(a => a.revenue / 1000000), // Em milhões
                backgroundColor: '#764ba2',
                borderRadius: 4,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    labels: { padding: 15 }
                },
                tooltip: {
                    callbacks: {
                        label: function (ctx) {
                            return `US$ ${(ctx.parsed.y).toFixed(2)}M`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    ticks: {
                        callback: function (value) {
                            return 'US$ ' + value.toFixed(0) + 'M';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Atualizar status de sincronização
 */
function updateSyncStatus(status) {
    const el = document.getElementById('syncStatus');

    switch (status) {
        case 'syncing':
            el.textContent = '🔄 Sincronizando...';
            el.className = 'sync-badge';
            break;
        case 'success':
            el.textContent = '✅ Sincronizado com sucesso';
            el.className = 'sync-badge success';
            break;
        case 'fallback':
            el.textContent = '📦 Usando dados de fallback';
            el.className = 'sync-badge warning';
            break;
        case 'error':
            el.textContent = '❌ Erro ao sincronizar';
            el.className = 'sync-badge error';
            break;
    }
}

/**
 * Utilidades
 */

function getNormalizedStatus(status) {
    const map = {
        'new': 'new',
        'open': 'open',
        'in progress': 'in-progress',
        'in_progress': 'in-progress',
        'on hold': 'on-hold',
        'on_hold': 'on-hold',
        'closed': 'closed',
        'resolved': 'resolved'
    };
    return map[status?.toLowerCase()] || 'new';
}

function getNormalizedPriority(priority) {
    const map = {
        'high': 'high',
        'medium': 'medium',
        'low': 'low'
    };
    return map[priority?.toLowerCase()] || 'medium';
}

function formatDate(dateStr) {
    try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('pt-BR', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch {
        return dateStr;
    }
}

function formatCurrency(value) {
    if (!value || value === 0) return '-';
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        notation: 'compact',
        compactDisplay: 'short'
    }).format(value);
}

function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function truncateString(str, length) {
    if (!str) return '';
    return str.length > length ? str.substring(0, length) + '...' : str;
}

/**
 * Inicialização
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Salesforce Dashboard inicializando...');
    loadSalesforceData();

    // Recarregar a cada X minutos
    setInterval(loadSalesforceData, config.refreshInterval);
    console.log(`♻️ Auto-refresh ativado a cada ${config.refreshInterval / 60000} minutos`);
});

// Recarregar ao voltar à aba
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        console.log('📱 Dashboard retornou à visibilidade');
        loadSalesforceData();
    }
});
