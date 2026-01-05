// UI Components

function createResourceCard(resource) {
    const statusClass = resource.state === 'UP' ? 'status-up' : 'status-down';
    const statusText = resource.state === 'UP' ? 'Доступен' : 'Недоступен';
    
    const updatedDate = new Date(resource.updated_at);
    const formattedDate = formatDate(updatedDate);

    return `
        <div class="resource-card" onclick="showResourceDetail(${resource.resource_id})">
            <div class="resource-header">
                <div class="resource-status ${statusClass}">
                    <span class="status-dot"></span>
                    ${statusText}
                </div>
            </div>
            <h3 class="resource-url">${escapeHtml(resource.url)}</h3>
            <div class="resource-meta">
                <span>ID: ${resource.resource_id}</span>
                <span>Обновлено: ${formattedDate}</span>
            </div>
            <div class="resource-actions" onclick="event.stopPropagation()">
                <button class="btn-icon" onclick="showResourceDetail(${resource.resource_id})" title="Подробнее">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                        <path d="M10 12C11.1046 12 12 11.1046 12 10C12 8.89543 11.1046 8 10 8C8.89543 8 8 8.89543 8 10C8 11.1046 8.89543 12 10 12Z" stroke="currentColor" stroke-width="2"/>
                        <path d="M2 10C2 10 5 4 10 4C15 4 18 10 18 10C18 10 15 16 10 16C5 16 2 10 2 10Z" stroke="currentColor" stroke-width="2"/>
                    </svg>
                </button>
                <button class="btn-icon btn-delete" onclick="showDeleteModal(${resource.resource_id}, '${escapeHtml(resource.url)}')" title="Удалить">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                        <path d="M3 5H17M7 5V3H13V5M8 9V15M12 9V15M5 5L6 17H14L15 5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </button>
            </div>
        </div>
    `;
}

function createResourceDetail(resource, statuses) {
    const statusClass = resource.state === 'UP' ? 'status-up' : 'status-down';
    const statusText = resource.state === 'UP' ? 'Доступен' : 'Недоступен';
    
    // Calculate stats
    const totalChecks = statuses.length;
    const successChecks = statuses.filter(s => s.status_code >= 200 && s.status_code < 400).length;
    const uptime = totalChecks > 0 ? ((successChecks / totalChecks) * 100).toFixed(1) : 0;
    
    // Calculate response time statistics
    const responseTimeStats = calculateResponseTimeStats(statuses);
    
    const lastCheck = statuses.length > 0 
        ? formatTime(new Date(statuses[statuses.length - 1].created_at))
        : 'Нет данных';

    // Get current status code from latest check
    const currentStatusCode = statuses.length > 0 
        ? statuses[statuses.length - 1].status_code 
        : (resource.state === 'UP' ? 200 : 500);

    return `
        <div class="resource-detail-header">
            <div class="detail-title">
                <div>
                    <h2>${escapeHtml(resource.url)}</h2>
                    <p class="detail-url">Последнее обновление: ${formatDate(new Date(resource.updated_at))}</p>
                </div>
                <div class="resource-status ${statusClass}">
                    <span class="status-dot"></span>
                    ${statusText}
                </div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value ${statusClass}">${currentStatusCode}</div>
                    <div class="stat-label">Статус код</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value text-primary-color">${responseTimeStats.avg}ms</div>
                    <div class="stat-label">Среднее время ответа</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value ${statusClass}">${uptime}%</div>
                    <div class="stat-label">Аптайм (24ч)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value text-primary-color">${lastCheck}</div>
                    <div class="stat-label">Последняя проверка</div>
                </div>
            </div>
        </div>

        ${createResponseTimeSection(responseTimeStats, statuses)}

        <div class="history-section">
            <div class="history-header">
                <h3>История доступности (последние 24 часа)</h3>
                <span class="text-muted">${totalChecks} проверок</span>
            </div>
            
            <div class="history-grid">
                ${createHistoryDots(statuses)}
            </div>
            
            <div class="history-legend">
                <div class="legend-item">
                    <div class="legend-dot" style="background: var(--success);"></div>
                    <span>Доступен</span>
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background: var(--danger);"></div>
                    <span>Недоступен</span>
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background: var(--text-muted); opacity: 0.3;"></div>
                    <span>Нет данных</span>
                </div>
            </div>
        </div>
    `;
}

function calculateResponseTimeStats(statuses) {
    if (statuses.length === 0) {
        return {
            avg: 0,
            min: 0,
            max: 0,
            median: 0,
            p95: 0,
        };
    }

    // response_time в API приходит в секундах (например, 0.123)
    // Конвертируем в миллисекунды
    const responseTimes = statuses.map(s => s.response_time * 1000);
    
    const sorted = [...responseTimes].sort((a, b) => a - b);
    
    const sum = responseTimes.reduce((acc, val) => acc + val, 0);
    const avg = Math.round(sum / responseTimes.length);
    const min = Math.round(Math.min(...responseTimes));
    const max = Math.round(Math.max(...responseTimes));
    
    // Calculate median
    const mid = Math.floor(sorted.length / 2);
    const median = sorted.length % 2 === 0
        ? Math.round((sorted[mid - 1] + sorted[mid]) / 2)
        : Math.round(sorted[mid]);
    
    // Calculate 95th percentile
    const p95Index = Math.floor(sorted.length * 0.95);
    const p95 = Math.round(sorted[p95Index] || sorted[sorted.length - 1]);

    return { avg, min, max, median, p95 };
}

function createResponseTimeSection(stats, statuses) {
    if (statuses.length === 0) {
        return `
            <div class="response-time-section">
                <h3>Статистика времени ответа</h3>
                <p class="text-muted">Недостаточно данных для отображения статистики</p>
            </div>
        `;
    }

    return `
        <div class="response-time-section">
            <div class="section-header">
                <h3>Статистика времени ответа</h3>
                <span class="text-muted">За последние 24 часа</span>
            </div>
            
            <div class="response-time-grid">
                <div class="response-time-card">
                    <div class="rt-icon" style="background: rgba(139, 92, 246, 0.1); color: var(--primary);">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                            <path d="M12 2L15 8L22 9L17 14L18 21L12 18L6 21L7 14L2 9L9 8L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                        </svg>
                    </div>
                    <div class="rt-content">
                        <div class="rt-label">Среднее</div>
                        <div class="rt-value">${stats.avg}<span class="rt-unit">ms</span></div>
                    </div>
                </div>

                <div class="response-time-card">
                    <div class="rt-icon" style="background: rgba(16, 185, 129, 0.1); color: var(--success);">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                            <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                        </svg>
                    </div>
                    <div class="rt-content">
                        <div class="rt-label">Минимальное</div>
                        <div class="rt-value">${stats.min}<span class="rt-unit">ms</span></div>
                    </div>
                </div>

                <div class="response-time-card">
                    <div class="rt-icon" style="background: rgba(239, 68, 68, 0.1); color: var(--danger);">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                            <path d="M12 8V12L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                            <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
                        </svg>
                    </div>
                    <div class="rt-content">
                        <div class="rt-label">Максимальное</div>
                        <div class="rt-value">${stats.max}<span class="rt-unit">ms</span></div>
                    </div>
                </div>

                <div class="response-time-card">
                    <div class="rt-icon" style="background: rgba(99, 102, 241, 0.1); color: var(--secondary);">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                            <path d="M9 11L12 14L22 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M21 12V19C21 20.1 20.1 21 19 21H5C3.9 21 3 20.1 3 19V5C3 3.9 3.9 3 5 3H16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    </div>
                    <div class="rt-content">
                        <div class="rt-label">Медиана</div>
                        <div class="rt-value">${stats.median}<span class="rt-unit">ms</span></div>
                    </div>
                </div>

                <div class="response-time-card">
                    <div class="rt-icon" style="background: rgba(245, 158, 11, 0.1); color: var(--warning);">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                            <path d="M3 3V21H21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                            <path d="M7 14L12 9L16 13L21 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </div>
                    <div class="rt-content">
                        <div class="rt-label">95-й процентиль</div>
                        <div class="rt-value">${stats.p95}<span class="rt-unit">ms</span></div>
                    </div>
                </div>
            </div>

            ${createResponseTimeChart(statuses, stats)}
        </div>
    `;
}

function createResponseTimeChart(statuses, stats) {
    // Take last 20 data points for the chart
    const chartData = statuses.slice(-20);
    
    // Convert response times to ms
    const responseTimes = statuses.map(s => s.response_time * 1000);

    const maxResponseTime = Math.max(...responseTimes);
    const chartHeight = 120;

    const bars = chartData.map((status, index) => {
        const responseTime = responseTimes[index];
        const height = (responseTime / maxResponseTime) * 100;
        const x = (index / chartData.length) * 100;
        const width = 100 / chartData.length - 1;
        
        let color = 'var(--success)';
        if (responseTime > stats.p95) color = 'var(--danger)';
        else if (responseTime > stats.avg) color = 'var(--warning)';
        
        const time = formatTime(new Date(status.created_at));
        const statusCode = status.status_code;
        
        return `
            <div class="chart-bar" 
                 style="left: ${x}%; width: ${width}%; height: ${height}%; background: ${color};"
                 title="${time}: ${Math.round(responseTime)}ms (${statusCode})">
            </div>
        `;
    }).join('');

    return `
        <div class="response-time-chart">
            <div class="chart-header">
                <div class="chart-title">График времени ответа</div>
                <div class="chart-legend">
                    <div class="chart-legend-item">
                        <div class="legend-color" style="background: var(--success);"></div>
                        <span>Быстро (&lt;${stats.avg}ms)</span>
                    </div>
                    <div class="chart-legend-item">
                        <div class="legend-color" style="background: var(--warning);"></div>
                        <span>Средне (${stats.avg}-${stats.p95}ms)</span>
                    </div>
                    <div class="chart-legend-item">
                        <div class="legend-color" style="background: var(--danger);"></div>
                        <span>Медленно (&gt;${stats.p95}ms)</span>
                    </div>
                </div>
            </div>
            <div class="chart-container">
                <div class="chart-y-axis">
                    <span class="y-label">${Math.round(maxResponseTime)}ms</span>
                    <span class="y-label">${Math.round(maxResponseTime / 2)}ms</span>
                    <span class="y-label">0ms</span>
                </div>
                <div class="chart-bars">
                    ${bars}
                </div>
            </div>
            <div class="chart-info">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.5"/>
                    <path d="M8 11V8M8 5H8.01" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
                <span>Наведите на столбец для подробной информации</span>
            </div>
        </div>
    `;
}

function createHistoryDots(statuses) {
    // ИСПРАВЛЕНИЕ: Используем все статусы напрямую, дополняя до 48 точек
    const targetDots = 48;
    const dots = [];
    
    // Сортируем статусы по времени (от старых к новым)
    const sortedStatuses = [...statuses].sort((a, b) => 
        new Date(a.created_at) - new Date(b.created_at)
    );
    
    // Если статусов меньше 48, добавляем пустые точки в начало
    const emptyDotsCount = Math.max(0, targetDots - sortedStatuses.length);
    
    // Добавляем пустые точки
    for (let i = 0; i < emptyDotsCount; i++) {
        dots.push(`<div class="history-dot status-unknown" title="Нет данных"></div>`);
    }
    
    // Добавляем реальные данные (берём последние 48 или все, если меньше)
    const displayStatuses = sortedStatuses.slice(-targetDots);
    
    displayStatuses.forEach(status => {
        const isSuccess = status.status_code >= 200 && status.status_code < 400;
        const dotClass = isSuccess ? 'status-up' : 'status-down';
        
        const time = formatTime(new Date(status.created_at));
        const responseTime = Math.round(status.response_time * 1000);
        
        const title = `${time} - ${status.status_code} (${responseTime}ms)`;
        
        dots.push(`<div class="history-dot ${dotClass}" title="${title}"></div>`);
    });
    
    return dots.join('');
}

// Utility functions
function formatDate(date) {
    const now = new Date();
    const diff = now - date;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days} д. назад`;
    if (hours > 0) return `${hours} ч. назад`;
    if (minutes > 0) return `${minutes} мин. назад`;
    return 'только что';
}

function formatTime(date) {
    return date.toLocaleTimeString('ru-RU', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = toast.querySelector('.toast-message');
    
    toastMessage.textContent = message;
    toast.classList.toggle('error', type === 'error');
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
