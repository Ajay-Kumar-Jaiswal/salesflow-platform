// ========================================================
// SalesFlow CRM - Client Application Logic
// ========================================================

const API_BASE = window.API_BASE_URL || 'http://localhost:8000/api';

// State
const state = {
  token: localStorage.getItem('salesflow_token') || null,
  user: JSON.parse(localStorage.getItem('salesflow_user') || 'null'),
  currentView: 'dashboard',
  customers: [],
  customerPagination: { page: 1, pageSize: 20, total: 0, pages: 1 },
  selectedCustomer: null,
  opportunities: [],
  followUps: [],
  activeFuFilter: 'all',
  users: [],
};

// ========================================================
// API CLIENT & AUTHENTICATION
// ========================================================

async function api(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  if (state.token) {
    headers['Authorization'] = `Bearer ${state.token}`;
  }

  try {
    const response = await fetch(url, { ...options, headers });
    
    if (response.status === 401) {
      // If token expired, clear state
      if (state.token) {
        logout(false);
        showToast('Your session has expired. Please sign in again.', 'error');
      }
    }

    if (response.status === 204) {
      return null;
    }

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errorMsg = data && (data.detail || (data.errors && data.errors[0])) || 'Request failed';
      throw new Error(errorMsg);
    }

    return data;
  } catch (err) {
    console.error(`API Error [${endpoint}]:`, err);
    throw err;
  }
}

function setAuth(token, user) {
  state.token = token;
  state.user = user;
  if (token) localStorage.setItem('salesflow_token', token);
  else localStorage.removeItem('salesflow_token');
  if (user) localStorage.setItem('salesflow_user', JSON.stringify(user));
  else localStorage.removeItem('salesflow_user');
  updateAuthUI();
}

function updateAuthUI() {
  const guestBox = document.getElementById('authGuest');
  const userBox = document.getElementById('authUser');
  const usersNavBtn = document.getElementById('usersNavBtn');

  if (state.user && state.token) {
    guestBox.style.display = 'none';
    userBox.style.display = 'flex';
    document.getElementById('navUserName').textContent = state.user.name;
    document.getElementById('navUserRole').textContent = state.user.role;
    document.getElementById('navUserAvatar').textContent = state.user.name.charAt(0).toUpperCase();

    if (state.user.role === 'ADMIN') {
      usersNavBtn.style.display = 'inline-flex';
    } else {
      usersNavBtn.style.display = 'none';
    }
  } else {
    guestBox.style.display = 'flex';
    userBox.style.display = 'none';
    usersNavBtn.style.display = 'none';
  }
}

function logout(notify = true) {
  setAuth(null, null);
  if (notify) showToast('Signed out successfully.', 'info');
  switchView('dashboard');
  loadDashboard();
}

// ========================================================
// NAVIGATION & VIEW SWITCHING
// ========================================================

function switchView(viewName) {
  state.currentView = viewName;
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.view === viewName);
  });
  document.querySelectorAll('.view').forEach(view => {
    view.classList.toggle('active', view.id === `view-${viewName}`);
  });

  if (viewName === 'dashboard') loadDashboard();
  else if (viewName === 'customers') loadCustomers();
  else if (viewName === 'pipeline') loadPipeline();
  else if (viewName === 'follow-ups') loadFollowUps();
  else if (viewName === 'activities') loadGlobalActivities();
  else if (viewName === 'users') loadUsers();
}

// ========================================================
// TOAST NOTIFICATIONS & HELPERS
// ========================================================

function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 200);
  }, 4000);
}

function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  const div = document.createElement('div');
  div.textContent = String(str);
  return div.innerHTML;
}

function formatCurrency(num) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0
  }).format(num || 0);
}

function formatDate(isoStr) {
  if (!isoStr) return '-';
  const d = new Date(isoStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatDateTime(isoStr) {
  if (!isoStr) return '-';
  const d = new Date(isoStr);
  return d.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function openModal(modalId) {
  const el = document.getElementById(modalId);
  if (el) el.classList.add('open');
}

function closeModal(modalId) {
  const el = document.getElementById(modalId);
  if (el) el.classList.remove('open');
}

// ========================================================
// DASHBOARD LOGIC (PHASE 11)
// ========================================================

async function loadDashboard() {
  try {
    const summary = await api('/dashboard/summary');
    if (!summary) return;

    // KPI Cards
    document.getElementById('kpiTotalCustomers').textContent = summary.total_customers.toLocaleString();
    document.getElementById('kpiOpenOpps').textContent = summary.open_opportunities.toLocaleString();
    document.getElementById('kpiPipelineValue').textContent = formatCurrency(summary.pipeline_value);
    document.getElementById('kpiWonRevenue').textContent = formatCurrency(summary.won_revenue);
    document.getElementById('kpiWonCount').textContent = summary.won_opportunities;
    document.getElementById('kpiWinRate').textContent = `${summary.conversion_rate}%`;

    // Pipeline Stage Distribution Chart
    renderPipelineChart(summary.pipeline_distribution);

    // Customer Status Pills
    renderCustomerStatusPills(summary.customer_status_distribution);

    // Upcoming Follow-ups Feed
    const fuList = document.getElementById('dashUpcomingFollowUps');
    fuList.innerHTML = '';
    if (summary.upcoming_follow_ups.length === 0) {
      fuList.innerHTML = '<p class="feed-item-sub">No pending follow-ups scheduled.</p>';
    } else {
      summary.upcoming_follow_ups.forEach(fu => {
        const item = document.createElement('div');
        item.className = 'feed-item';
        item.innerHTML = `
          <div class="feed-item-header">
            <span>${escapeHtml(fu.title)}</span>
            <span class="type-pill type-${fu.follow_up_type}">${fu.follow_up_type}</span>
          </div>
          <div class="feed-item-sub">${escapeHtml(fu.customer_name || 'Customer')} • Due: ${formatDateTime(fu.scheduled_at)}</div>
        `;
        fuList.appendChild(item);
      });
    }

    // Recent Activities Feed
    const actList = document.getElementById('dashRecentActivities');
    actList.innerHTML = '';
    if (summary.recent_activities.length === 0) {
      actList.innerHTML = '<p class="feed-item-sub">No recent activities logged.</p>';
    } else {
      summary.recent_activities.forEach(act => {
        const item = document.createElement('div');
        item.className = 'feed-item';
        item.innerHTML = `
          <div class="feed-item-header">
            <span>${escapeHtml(act.title)}</span>
            <span class="type-pill type-${act.activity_type}">${act.activity_type}</span>
          </div>
          <div class="feed-item-sub">${escapeHtml(act.customer_name || 'Customer')} • ${formatDateTime(act.created_at)}</div>
        `;
        actList.appendChild(item);
      });
    }

    // Recent Customers Feed
    const custList = document.getElementById('dashRecentCustomers');
    custList.innerHTML = '';
    if (summary.recent_customers.length === 0) {
      custList.innerHTML = '<p class="feed-item-sub">No customers in database.</p>';
    } else {
      summary.recent_customers.forEach(c => {
        const item = document.createElement('div');
        item.className = 'feed-item';
        item.style.cursor = 'pointer';
        item.onclick = () => viewCustomerDetail(c.id);
        item.innerHTML = `
          <div class="feed-item-header">
            <span>${escapeHtml(c.name)}</span>
            <span class="status-badge status-${c.status}">${c.status}</span>
          </div>
          <div class="feed-item-sub">${escapeHtml(c.company || c.email)}</div>
        `;
        custList.appendChild(item);
      });
    }

  } catch (err) {
    showToast('Failed to load dashboard metrics. Backend running?', 'error');
  }
}

function renderPipelineChart(dist) {
  const container = document.getElementById('pipelineChartContainer');
  container.innerHTML = '';

  const maxVal = Math.max(...dist.map(d => d.value), 1000);

  dist.forEach(stage => {
    const pct = Math.max((stage.value / maxVal) * 100, stage.count > 0 ? 8 : 2);
    const bar = document.createElement('div');
    bar.className = 'funnel-bar-wrap';
    bar.innerHTML = `
      <div class="funnel-label-row">
        <span>${stage.stage} (${stage.count})</span>
        <span>${formatCurrency(stage.value)}</span>
      </div>
      <div class="funnel-track">
        <div class="funnel-fill" style="width: ${pct}%; background: var(--${stage.stage.toLowerCase()}, var(--primary));"></div>
      </div>
    `;
    container.appendChild(bar);
  });
}

function renderCustomerStatusPills(dist) {
  const container = document.getElementById('customerStatusChartContainer');
  container.innerHTML = '';

  const grid = document.createElement('div');
  grid.className = 'status-pills-grid';

  Object.entries(dist).forEach(([status, count]) => {
    const pill = document.createElement('div');
    pill.className = 'status-pill-card';
    pill.innerHTML = `
      <div class="status-pill-title">
        <span class="status-badge status-${status}">${status}</span>
      </div>
      <div class="status-pill-count">${count}</div>
    `;
    grid.appendChild(pill);
  });

  container.appendChild(grid);
}

// ========================================================
// CUSTOMERS DIRECTORY (PHASE 5, 12, 13)
// ========================================================

let custSearchTimeout;

async function loadCustomers() {
  const search = document.getElementById('custSearchInput').value.trim();
  const status = document.getElementById('custStatusFilter').value;
  const sortVal = document.getElementById('custSortBy').value;
  const [sortBy, sortOrder] = sortVal.split(':');
  const pageSize = parseInt(document.getElementById('custPageSize').value, 10);
  const page = state.customerPagination.page;

  let url = `/customers?page=${page}&page_size=${pageSize}&sort_by=${sortBy}&sort_order=${sortOrder}`;
  if (search) url += `&search=${encodeURIComponent(search)}`;
  if (status) url += `&status=${encodeURIComponent(status)}`;

  try {
    const data = await api(url);
    const items = data.items || data;
    state.customers = items;
    state.customerPagination = {
      page: data.page || 1,
      pageSize: data.page_size || pageSize,
      total: data.total || items.length,
      pages: data.pages || 1,
    };

    renderCustomersTable(items);
    updateCustomerPaginationUI();
  } catch (err) {
    showToast('Failed to load customers.', 'error');
  }
}

function renderCustomersTable(customers) {
  const tbody = document.getElementById('customersTableBody');
  const empty = document.getElementById('customersEmpty');
  tbody.innerHTML = '';

  if (!customers || customers.length === 0) {
    empty.style.display = 'block';
    return;
  }
  empty.style.display = 'none';

  customers.forEach(c => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>
        <div class="customer-cell-main" onclick="viewCustomerDetail(${c.id})">${escapeHtml(c.name)}</div>
        <div style="font-size:12px;color:var(--text-muted);">${escapeHtml(c.industry || 'No industry')}</div>
      </td>
      <td>${escapeHtml(c.company || '-')}</td>
      <td>
        <div>${escapeHtml(c.email)}</div>
        <div style="font-size:12px;color:var(--text-muted);">${escapeHtml(c.phone || '-')}</div>
      </td>
      <td><span class="status-badge status-${c.status}">${c.status}</span></td>
      <td>${escapeHtml(c.assigned_user_name || 'Unassigned')}</td>
      <td>${formatDate(c.created_at)}</td>
      <td class="text-right">
        <button class="btn btn-outline btn-xs" onclick="viewCustomerDetail(${c.id})">View</button>
        <button class="btn btn-outline btn-xs" onclick="openEditCustomerModal(${c.id})">Edit</button>
        <button class="btn btn-danger btn-xs" onclick="deleteCustomerConfirm(${c.id})">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function updateCustomerPaginationUI() {
  const p = state.customerPagination;
  const start = p.total === 0 ? 0 : (p.page - 1) * p.pageSize + 1;
  const end = Math.min(p.page * p.pageSize, p.total);
  document.getElementById('custPaginationInfo').textContent = `Showing ${start} to ${end} of ${p.total} entries`;
  document.getElementById('custCurrentPageNum').textContent = p.page;
  document.getElementById('custPrevPageBtn').disabled = p.page <= 1;
  document.getElementById('custNextPageBtn').disabled = p.page >= p.pages;
}

// ========================================================
// CUSTOMER DETAIL RECORD (PHASE 6)
// ========================================================

async function viewCustomerDetail(customerId) {
  try {
    const customer = await api(`/customers/${customerId}`);
    state.selectedCustomer = customer;

    document.getElementById('detailCustomerName').textContent = customer.name;
    const statusBadge = document.getElementById('detailCustomerStatus');
    statusBadge.textContent = customer.status;
    statusBadge.className = `status-badge status-${customer.status}`;

    document.getElementById('detailCustomerCompany').textContent = customer.company || '-';
    document.getElementById('detailCustomerEmail').textContent = customer.email;
    document.getElementById('detailCustomerPhone').textContent = customer.phone || '-';
    document.getElementById('detailCustomerIndustry').textContent = customer.industry || '-';
    document.getElementById('detailCustomerSource').textContent = customer.source || '-';
    document.getElementById('detailCustomerRep').textContent = customer.assigned_user_name || 'Unassigned';
    document.getElementById('detailCustomerCreated').textContent = formatDateTime(customer.created_at);
    document.getElementById('detailCustomerUpdated').textContent = formatDateTime(customer.updated_at);
    document.getElementById('detailCustomerNotes').textContent = customer.notes || 'No notes added for this account.';

    // Setup action buttons in detail modal
    document.getElementById('detailEditBtn').onclick = () => {
      closeModal('customerDetailModal');
      openEditCustomerModal(customer.id);
    };
    document.getElementById('detailDeleteBtn').onclick = () => {
      deleteCustomerConfirm(customer.id, () => closeModal('customerDetailModal'));
    };
    document.getElementById('detailAddActivityBtn').onclick = () => {
      openActivityModal(customer.id);
    };
    document.getElementById('detailAddOppBtn').onclick = () => {
      openOpportunityModal(null, customer.id);
    };
    document.getElementById('detailScheduleFuBtn').onclick = () => {
      openFollowUpModal(null, customer.id);
    };

    // Load sub-items: Activities, Opportunities, Follow-ups
    loadCustomerActivities(customer.id);
    loadCustomerOpportunities(customer.id);
    loadCustomerFollowUps(customer.id);

    openModal('customerDetailModal');
  } catch (err) {
    showToast('Failed to load customer details.', 'error');
  }
}

async function loadCustomerActivities(customerId) {
  const timeline = document.getElementById('detailActivitiesTimeline');
  timeline.innerHTML = '<p class="feed-item-sub">Loading activity history...</p>';

  try {
    const activities = await api(`/customers/${customerId}/activities`);
    timeline.innerHTML = '';
    if (!activities || activities.length === 0) {
      timeline.innerHTML = '<p class="feed-item-sub">No recorded interactions yet. Click "+ Add Activity" to log one.</p>';
      return;
    }

    activities.forEach(act => {
      const item = document.createElement('div');
      item.className = 'timeline-item';
      item.innerHTML = `
        <div class="timeline-item-header">
          <span class="type-pill type-${act.activity_type}">${act.activity_type}</span>
          <span class="timeline-title">${escapeHtml(act.title)}</span>
          <span class="timeline-date">${formatDateTime(act.created_at)}</span>
        </div>
        ${act.description ? `<div class="timeline-body">${escapeHtml(act.description)}</div>` : ''}
      `;
      timeline.appendChild(item);
    });
  } catch (err) {
    timeline.innerHTML = '<p class="feed-item-sub">Error loading activities.</p>';
  }
}

async function loadCustomerOpportunities(customerId) {
  const container = document.getElementById('detailOppsList');
  container.innerHTML = '<p class="feed-item-sub">Loading opportunities...</p>';

  try {
    const opps = await api(`/opportunities?customer_id=${customerId}`);
    container.innerHTML = '';
    if (!opps || opps.length === 0) {
      container.innerHTML = '<p class="feed-item-sub">No sales deals active for this customer.</p>';
      return;
    }

    opps.forEach(o => {
      const card = document.createElement('div');
      card.className = 'feed-item';
      card.innerHTML = `
        <div class="feed-item-header">
          <span>${escapeHtml(o.title)}</span>
          <span class="status-badge status-${o.stage}">${o.stage}</span>
        </div>
        <div class="feed-item-sub">Amount: <strong>${formatCurrency(o.amount)}</strong> • Probability: ${o.probability}%</div>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    container.innerHTML = '<p class="feed-item-sub">Error loading opportunities.</p>';
  }
}

async function loadCustomerFollowUps(customerId) {
  const container = document.getElementById('detailFusList');
  container.innerHTML = '<p class="feed-item-sub">Loading follow-ups...</p>';

  try {
    const fus = await api(`/follow-ups?customer_id=${customerId}`);
    container.innerHTML = '';
    if (!fus || fus.length === 0) {
      container.innerHTML = '<p class="feed-item-sub">No upcoming tasks scheduled.</p>';
      return;
    }

    fus.forEach(f => {
      const card = document.createElement('div');
      card.className = `feed-item ${f.completed ? 'completed' : ''}`;
      card.innerHTML = `
        <div class="feed-item-header">
          <span>${escapeHtml(f.title)} ${f.completed ? '✓ (Completed)' : ''}</span>
          <span class="type-pill type-${f.follow_up_type}">${f.follow_up_type}</span>
        </div>
        <div class="feed-item-sub">Scheduled: ${formatDateTime(f.scheduled_at)}</div>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    container.innerHTML = '<p class="feed-item-sub">Error loading follow-ups.</p>';
  }
}

// Detail modal internal tab switcher
document.querySelectorAll('.detail-tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.detail-tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.detail-tab-content').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(btn.dataset.detailTab).classList.add('active');
  });
});

// ========================================================
// CUSTOMER CREATE & EDIT MODAL
// ========================================================

async function openAddCustomerModal() {
  document.getElementById('customerForm').reset();
  document.getElementById('custFormId').value = '';
  document.getElementById('customerFormTitle').textContent = 'Add New Customer';
  document.getElementById('custFormSubmitBtn').textContent = 'Create Customer';
  await populateRepDropdown('custFormAssigned');
  openModal('customerFormModal');
}

async function openEditCustomerModal(id) {
  try {
    const c = await api(`/customers/${id}`);
    document.getElementById('custFormId').value = c.id;
    document.getElementById('custFormName').value = c.name;
    document.getElementById('custFormEmail').value = c.email;
    document.getElementById('custFormPhone').value = c.phone || '';
    document.getElementById('custFormCompany').value = c.company || '';
    document.getElementById('custFormIndustry').value = c.industry || '';
    document.getElementById('custFormStatus').value = c.status;
    document.getElementById('custFormSource').value = c.source || '';
    document.getElementById('custFormNotes').value = c.notes || '';

    await populateRepDropdown('custFormAssigned', c.assigned_to);

    document.getElementById('customerFormTitle').textContent = 'Edit Customer';
    document.getElementById('custFormSubmitBtn').textContent = 'Save Changes';
    openModal('customerFormModal');
  } catch (err) {
    showToast('Failed to load customer for editing.', 'error');
  }
}

document.getElementById('customerForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const id = document.getElementById('custFormId').value;
  const payload = {
    name: document.getElementById('custFormName').value.trim(),
    email: document.getElementById('custFormEmail').value.trim(),
    phone: document.getElementById('custFormPhone').value.trim() || null,
    company: document.getElementById('custFormCompany').value.trim() || null,
    industry: document.getElementById('custFormIndustry').value.trim() || null,
    status: document.getElementById('custFormStatus').value,
    source: document.getElementById('custFormSource').value.trim() || null,
    assigned_to: document.getElementById('custFormAssigned').value ? parseInt(document.getElementById('custFormAssigned').value, 10) : null,
    notes: document.getElementById('custFormNotes').value.trim() || null,
  };

  try {
    if (id) {
      await api(`/customers/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
      showToast('Customer updated successfully.', 'success');
    } else {
      await api('/customers', { method: 'POST', body: JSON.stringify(payload) });
      showToast('Customer created successfully.', 'success');
    }
    closeModal('customerFormModal');
    loadCustomers();
    loadDashboard();
  } catch (err) {
    showToast(err.message, 'error');
  }
});

async function deleteCustomerConfirm(id, onSuccess) {
  if (!confirm('Are you sure you want to delete this customer? This will also remove associated opportunities, activities, and follow-ups.')) return;

  try {
    await api(`/customers/${id}`, { method: 'DELETE' });
    showToast('Customer deleted successfully.', 'success');
    if (onSuccess) onSuccess();
    loadCustomers();
    loadDashboard();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// ========================================================
// SALES PIPELINE / KANBAN BOARD (PHASE 8 & 9)
// ========================================================

const PIPELINE_STAGES = ['LEAD', 'CONTACTED', 'QUALIFIED', 'PROPOSAL', 'NEGOTIATION', 'WON', 'LOST'];

async function loadPipeline() {
  const board = document.getElementById('kanbanBoard');
  board.innerHTML = '';

  try {
    const opps = await api('/opportunities');
    state.opportunities = opps || [];

    PIPELINE_STAGES.forEach(stage => {
      const stageOpps = state.opportunities.filter(o => o.stage === stage);
      const colTotal = stageOpps.reduce((sum, o) => sum + (o.amount || 0), 0);

      const col = document.createElement('div');
      col.className = 'kanban-column';
      col.dataset.stage = stage;

      col.innerHTML = `
        <div class="kanban-column-header">
          <div class="kanban-col-title">
            <span>${stage}</span>
            <span class="kanban-badge-count">${stageOpps.length}</span>
          </div>
          <span class="kanban-col-total">${formatCurrency(colTotal)}</span>
        </div>
        <div class="kanban-cards-wrap" id="col-${stage}" ondragover="handleDragOver(event)" ondrop="handleDrop(event, '${stage}')">
          <!-- Injected cards -->
        </div>
      `;

      const cardsWrap = col.querySelector('.kanban-cards-wrap');
      stageOpps.forEach(opp => {
        const card = document.createElement('div');
        card.className = 'kanban-card';
        card.draggable = true;
        card.dataset.id = opp.id;
        card.ondragstart = (e) => handleDragStart(e, opp.id);

        card.innerHTML = `
          <div class="kanban-card-title">${escapeHtml(opp.title)}</div>
          <div class="kanban-card-customer">${escapeHtml(opp.customer_name || 'Customer')}</div>
          <div style="font-size:12px;color:var(--text-muted);margin-bottom:6px;">${escapeHtml(opp.description || '')}</div>
          <div class="kanban-card-footer">
            <span class="kanban-amount">${formatCurrency(opp.amount)}</span>
            <select class="kanban-move-select" onchange="moveOpportunityStage(${opp.id}, this.value)">
              ${PIPELINE_STAGES.map(s => `<option value="${s}" ${s === stage ? 'selected' : ''}>${s}</option>`).join('')}
            </select>
          </div>
        `;
        cardsWrap.appendChild(card);
      });

      board.appendChild(col);
    });

  } catch (err) {
    showToast('Failed to load sales pipeline.', 'error');
  }
}

let draggedOppId = null;

function handleDragStart(e, oppId) {
  draggedOppId = oppId;
  e.dataTransfer.setData('text/plain', String(oppId));
}

function handleDragOver(e) {
  e.preventDefault();
}

async function handleDrop(e, targetStage) {
  e.preventDefault();
  const oppId = draggedOppId || parseInt(e.dataTransfer.getData('text/plain'), 10);
  if (oppId) {
    await moveOpportunityStage(oppId, targetStage);
  }
}

async function moveOpportunityStage(oppId, newStage) {
  try {
    await api(`/opportunities/${oppId}`, {
      method: 'PUT',
      body: JSON.stringify({ stage: newStage })
    });
    showToast(`Deal moved to ${newStage}`, 'success');
    loadPipeline();
    loadDashboard();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Opportunity Modal
async function openOpportunityModal(oppId = null, defaultCustomerId = null) {
  document.getElementById('oppForm').reset();
  document.getElementById('oppFormId').value = oppId || '';
  await populateCustomerDropdown('oppFormCustomer', defaultCustomerId);
  await populateRepDropdown('oppFormAssigned');

  if (oppId) {
    const opp = await api(`/opportunities/${oppId}`);
    document.getElementById('oppFormTitle').textContent = 'Edit Opportunity';
    document.getElementById('oppFormTitleInput').value = opp.title;
    document.getElementById('oppFormCustomer').value = opp.customer_id;
    document.getElementById('oppFormAmount').value = opp.amount;
    document.getElementById('oppFormStage').value = opp.stage;
    document.getElementById('oppFormProbability').value = opp.probability;
    document.getElementById('oppFormDescription').value = opp.description || '';
  } else {
    document.getElementById('oppFormTitle').textContent = 'New Opportunity Deal';
  }

  openModal('oppFormModal');
}

document.getElementById('oppForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const id = document.getElementById('oppFormId').value;
  const payload = {
    title: document.getElementById('oppFormTitleInput').value.trim(),
    customer_id: parseInt(document.getElementById('oppFormCustomer').value, 10),
    amount: parseFloat(document.getElementById('oppFormAmount').value),
    stage: document.getElementById('oppFormStage').value,
    probability: parseFloat(document.getElementById('oppFormProbability').value || 50),
    expected_close_date: document.getElementById('oppFormCloseDate').value ? new Date(document.getElementById('oppFormCloseDate').value).toISOString() : null,
    assigned_to: document.getElementById('oppFormAssigned').value ? parseInt(document.getElementById('oppFormAssigned').value, 10) : null,
    description: document.getElementById('oppFormDescription').value.trim() || null,
  };

  try {
    if (id) {
      await api(`/opportunities/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
      showToast('Opportunity updated.', 'success');
    } else {
      await api('/opportunities', { method: 'POST', body: JSON.stringify(payload) });
      showToast('Opportunity created.', 'success');
    }
    closeModal('oppFormModal');
    loadPipeline();
    loadDashboard();
  } catch (err) {
    showToast(err.message, 'error');
  }
});

// ========================================================
// FOLLOW-UPS SYSTEM (PHASE 10)
// ========================================================

async function loadFollowUps() {
  const container = document.getElementById('followUpsList');
  const empty = document.getElementById('followUpsEmpty');
  container.innerHTML = '';

  try {
    const fus = await api(`/follow-ups?filter_status=${state.activeFuFilter}`);
    state.followUps = fus || [];

    if (state.followUps.length === 0) {
      empty.style.display = 'block';
      return;
    }
    empty.style.display = 'none';

    state.followUps.forEach(fu => {
      const card = document.createElement('div');
      card.className = `fu-card ${fu.completed ? 'completed' : ''}`;
      card.innerHTML = `
        <div class="fu-header">
          <span class="type-pill type-${fu.follow_up_type}">${fu.follow_up_type}</span>
          <span class="fu-date">${formatDateTime(fu.scheduled_at)}</span>
        </div>
        <div class="fu-checkbox-title">
          <input type="checkbox" ${fu.completed ? 'checked' : ''} onchange="toggleFollowUpComplete(${fu.id}, this.checked)">
          <span class="fu-title" style="${fu.completed ? 'text-decoration:line-through;color:var(--text-muted);' : ''}">${escapeHtml(fu.title)}</span>
        </div>
        <div style="font-size:12px;color:var(--primary);font-weight:500;">
          ${escapeHtml(fu.customer_name || 'Customer')}
        </div>
        ${fu.description ? `<div class="fu-desc">${escapeHtml(fu.description)}</div>` : ''}
        <div style="display:flex;justify-content:flex-end;margin-top:4px;">
          <button class="btn btn-danger btn-xs" onclick="deleteFollowUp(${fu.id})">Delete</button>
        </div>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    showToast('Failed to load follow-ups.', 'error');
  }
}

async function toggleFollowUpComplete(id, completed) {
  try {
    await api(`/follow-ups/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ completed })
    });
    showToast(completed ? 'Follow-up marked completed!' : 'Follow-up reopened.', 'info');
    loadFollowUps();
    loadDashboard();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function deleteFollowUp(id) {
  if (!confirm('Delete this scheduled follow-up?')) return;
  try {
    await api(`/follow-ups/${id}`, { method: 'DELETE' });
    showToast('Follow-up deleted.', 'success');
    loadFollowUps();
    loadDashboard();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function openFollowUpModal(fuId = null, defaultCustomerId = null) {
  document.getElementById('followUpForm').reset();
  document.getElementById('fuFormId').value = fuId || '';
  await populateCustomerDropdown('fuFormCustomer', defaultCustomerId);

  // Default to tomorrow 10:00 AM
  const d = new Date();
  d.setDate(d.getDate() + 1);
  d.setHours(10, 0, 0, 0);
  document.getElementById('fuFormScheduled').value = d.toISOString().slice(0, 16);

  openModal('followUpFormModal');
}

document.getElementById('followUpForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const id = document.getElementById('fuFormId').value;
  const payload = {
    title: document.getElementById('fuFormTitleInput').value.trim(),
    customer_id: parseInt(document.getElementById('fuFormCustomer').value, 10),
    follow_up_type: document.getElementById('fuFormType').value,
    scheduled_at: new Date(document.getElementById('fuFormScheduled').value).toISOString(),
    description: document.getElementById('fuFormDesc').value.trim() || null,
    completed: false
  };

  try {
    if (id) {
      await api(`/follow-ups/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
      showToast('Follow-up updated.', 'success');
    } else {
      await api('/follow-ups', { method: 'POST', body: JSON.stringify(payload) });
      showToast('Follow-up scheduled.', 'success');
    }
    closeModal('followUpFormModal');
    loadFollowUps();
    loadDashboard();
  } catch (err) {
    showToast(err.message, 'error');
  }
});

// Follow-up sub-tabs
document.querySelectorAll('.sub-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.sub-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    state.activeFuFilter = tab.dataset.fuFilter;
    loadFollowUps();
  });
});

// ========================================================
// ACTIVITIES SYSTEM (PHASE 7)
// ========================================================

async function loadGlobalActivities() {
  const container = document.getElementById('globalActivitiesTimeline');
  const empty = document.getElementById('activitiesEmpty');
  container.innerHTML = '';

  try {
    // Get recent activities from dashboard summary or customers
    const summary = await api('/dashboard/summary');
    const acts = summary.recent_activities || [];

    if (acts.length === 0) {
      empty.style.display = 'block';
      return;
    }
    empty.style.display = 'none';

    acts.forEach(act => {
      const item = document.createElement('div');
      item.className = 'timeline-item';
      item.innerHTML = `
        <div class="timeline-item-header">
          <span class="type-pill type-${act.activity_type}">${act.activity_type}</span>
          <span class="timeline-title">${escapeHtml(act.title)}</span>
          <span class="timeline-date">${formatDateTime(act.created_at)}</span>
        </div>
        <div style="font-size:12px;color:var(--primary);margin-bottom:4px;">
          ${escapeHtml(act.customer_name || 'Customer')}
        </div>
        ${act.description ? `<div class="timeline-body">${escapeHtml(act.description)}</div>` : ''}
      `;
      container.appendChild(item);
    });
  } catch (err) {
    showToast('Failed to load activities.', 'error');
  }
}

async function openActivityModal(defaultCustomerId = null) {
  document.getElementById('activityForm').reset();
  await populateCustomerDropdown('actFormCustomer', defaultCustomerId);
  openModal('activityFormModal');
}

document.getElementById('activityForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const customerId = parseInt(document.getElementById('actFormCustomer').value, 10);
  const payload = {
    customer_id: customerId,
    activity_type: document.getElementById('actFormType').value,
    title: document.getElementById('actFormTitleInput').value.trim(),
    description: document.getElementById('actFormDesc').value.trim() || null,
  };

  try {
    await api(`/customers/${customerId}/activities`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    showToast('Activity logged successfully.', 'success');
    closeModal('activityFormModal');
    if (state.selectedCustomer && state.selectedCustomer.id === customerId) {
      loadCustomerActivities(customerId);
    }
    loadDashboard();
  } catch (err) {
    showToast(err.message, 'error');
  }
});

// ========================================================
// USERS ADMIN MANAGEMENT (PHASE 4 & 12)
// ========================================================

async function loadUsers() {
  const tbody = document.getElementById('usersTableBody');
  tbody.innerHTML = '';

  try {
    const users = await api('/users');
    state.users = users || [];

    state.users.forEach(u => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>${escapeHtml(u.name)}</strong></td>
        <td>${escapeHtml(u.email)}</td>
        <td><span class="status-badge ${u.role === 'ADMIN' ? 'status-PROPOSAL' : 'status-QUALIFIED'}">${u.role}</span></td>
        <td>${formatDate(u.created_at)}</td>
        <td class="text-right">
          ${u.id !== state.user.id ? `<button class="btn btn-danger btn-xs" onclick="deleteUser(${u.id})">Remove</button>` : '<span style="font-size:12px;color:var(--text-muted);">(You)</span>'}
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    showToast('Only admins can view users list.', 'error');
  }
}

async function deleteUser(id) {
  if (!confirm('Remove this team member from SalesFlow CRM?')) return;
  try {
    await api(`/users/${id}`, { method: 'DELETE' });
    showToast('User removed.', 'success');
    loadUsers();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

document.getElementById('addUserForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    name: document.getElementById('adminAddName').value.trim(),
    email: document.getElementById('adminAddEmail').value.trim(),
    password: document.getElementById('adminAddPassword').value,
    role: document.getElementById('adminAddRole').value,
  };

  try {
    await api('/auth/register', { method: 'POST', body: JSON.stringify(payload) });
    showToast('Team member added successfully.', 'success');
    closeModal('userModal');
    document.getElementById('addUserForm').reset();
    loadUsers();
  } catch (err) {
    showToast(err.message, 'error');
  }
});

// ========================================================
// DROPDOWN HELPERS
// ========================================================

async function populateCustomerDropdown(selectId, selectedId = null) {
  const select = document.getElementById(selectId);
  select.innerHTML = '<option value="">Select customer...</option>';
  try {
    const data = await api('/customers?page_size=100&paginate=false');
    const list = Array.isArray(data) ? data : (data.items || []);
    list.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = `${c.name} (${c.company || c.email})`;
      if (selectedId && c.id === selectedId) opt.selected = true;
      select.appendChild(opt);
    });
  } catch (err) {
    console.warn('Could not populate customers dropdown:', err);
  }
}

async function populateRepDropdown(selectId, selectedId = null) {
  const select = document.getElementById(selectId);
  select.innerHTML = '<option value="">Unassigned</option>';
  try {
    const users = await api('/users');
    (users || []).forEach(u => {
      const opt = document.createElement('option');
      opt.value = u.id;
      opt.textContent = `${u.name} (${u.role})`;
      if (selectedId && u.id === selectedId) opt.selected = true;
      select.appendChild(opt);
    });
  } catch (err) {
    // If unauthenticated or forbidden, fallback
    if (state.user) {
      const opt = document.createElement('option');
      opt.value = state.user.id;
      opt.textContent = `${state.user.name} (${state.user.role})`;
      if (selectedId === state.user.id) opt.selected = true;
      select.appendChild(opt);
    }
  }
}

// ========================================================
// AUTH MODAL & DEMO CREDENTIALS
// ========================================================

document.getElementById('tabLoginBtn').addEventListener('click', () => {
  document.getElementById('tabLoginBtn').classList.add('active');
  document.getElementById('tabRegisterBtn').classList.remove('active');
  document.getElementById('loginForm').style.display = 'block';
  document.getElementById('registerForm').style.display = 'none';
  document.getElementById('authModalTitle').textContent = 'Sign In to SalesFlow';
});

document.getElementById('tabRegisterBtn').addEventListener('click', () => {
  document.getElementById('tabRegisterBtn').classList.add('active');
  document.getElementById('tabLoginBtn').classList.remove('active');
  document.getElementById('loginForm').style.display = 'none';
  document.getElementById('registerForm').style.display = 'block';
  document.getElementById('authModalTitle').textContent = 'Create SalesFlow Account';
});

document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.getElementById('loginEmail').value.trim();
  const password = document.getElementById('loginPassword').value;

  try {
    const res = await api('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    setAuth(res.access_token, res.user);
    showToast(`Welcome back, ${res.user.name}!`, 'success');
    closeModal('authModal');
    loadDashboard();
  } catch (err) {
    showToast(err.message, 'error');
  }
});

document.getElementById('registerForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    name: document.getElementById('regName').value.trim(),
    email: document.getElementById('regEmail').value.trim(),
    password: document.getElementById('regPassword').value,
    role: document.getElementById('regRole').value,
  };

  try {
    await api('/auth/register', { method: 'POST', body: JSON.stringify(payload) });
    // Log in immediately
    const loginRes = await api('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email: payload.email, password: payload.password })
    });
    setAuth(loginRes.access_token, loginRes.user);
    showToast(`Account created! Welcome, ${loginRes.user.name}.`, 'success');
    closeModal('authModal');
    loadDashboard();
  } catch (err) {
    showToast(err.message, 'error');
  }
});

// Quick Demo Login buttons:
async function quickDemoAuth(name, email, password, role) {
  try {
    // Try login
    let loginRes;
    try {
      loginRes = await api('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      });
    } catch {
      // Register demo user if not existing
      await api('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ name, email, password, role })
      });
      loginRes = await api('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      });
    }

    setAuth(loginRes.access_token, loginRes.user);
    showToast(`Signed in as ${loginRes.user.name} (${role})`, 'success');
    closeModal('authModal');
    loadDashboard();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

document.getElementById('quickDemoAdmin').addEventListener('click', () => {
  quickDemoAuth('Admin Director', 'admin@salesflow.com', 'AdminPass123!', 'ADMIN');
});

document.getElementById('quickDemoRep').addEventListener('click', () => {
  quickDemoAuth('Jordan Rep', 'jordan@salesflow.com', 'RepPass123!', 'SALES_REP');
});

// ========================================================
// GLOBAL EVENT LISTENERS & INITIALIZATION
// ========================================================

document.querySelectorAll('.nav-item').forEach(btn => {
  btn.addEventListener('click', () => switchView(btn.dataset.view));
});

document.getElementById('openLoginModalBtn').onclick = () => openModal('authModal');
document.getElementById('logoutBtn').onclick = () => logout();
document.getElementById('refreshDashboardBtn').onclick = () => loadDashboard();

// Customer toolbar listeners
document.getElementById('openAddCustomerBtn').onclick = openAddCustomerModal;
document.getElementById('custSearchInput').addEventListener('input', () => {
  clearTimeout(custSearchTimeout);
  custSearchTimeout = setTimeout(() => {
    state.customerPagination.page = 1;
    loadCustomers();
  }, 300);
});
document.getElementById('custStatusFilter').addEventListener('change', () => {
  state.customerPagination.page = 1;
  loadCustomers();
});
document.getElementById('custSortBy').addEventListener('change', () => {
  state.customerPagination.page = 1;
  loadCustomers();
});
document.getElementById('custPageSize').addEventListener('change', () => {
  state.customerPagination.page = 1;
  loadCustomers();
});
document.getElementById('custResetFilterBtn').addEventListener('click', () => {
  document.getElementById('custSearchInput').value = '';
  document.getElementById('custStatusFilter').value = '';
  document.getElementById('custSortBy').value = 'created_at:desc';
  state.customerPagination.page = 1;
  loadCustomers();
});
document.getElementById('custPrevPageBtn').addEventListener('click', () => {
  if (state.customerPagination.page > 1) {
    state.customerPagination.page--;
    loadCustomers();
  }
});
document.getElementById('custNextPageBtn').addEventListener('click', () => {
  if (state.customerPagination.page < state.customerPagination.pages) {
    state.customerPagination.page++;
    loadCustomers();
  }
});

// Modal triggers
document.getElementById('openAddOpportunityBtn').onclick = () => openOpportunityModal();
document.getElementById('openAddFollowUpBtn').onclick = () => openFollowUpModal();
document.getElementById('openAddUserBtn').onclick = () => openModal('userModal');

// Close modal when clicking outside content
document.querySelectorAll('.modal-backdrop').forEach(modal => {
  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.classList.remove('open');
  });
});

// Initial boot
(async function init() {
  updateAuthUI();
  // Check if saved token is valid
  if (state.token) {
    try {
      const me = await api('/auth/me');
      setAuth(state.token, me);
    } catch {
      setAuth(null, null);
    }
  }
  loadDashboard();
})();
