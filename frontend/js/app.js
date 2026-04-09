/**
 * SPA router and all views - Library Management System
 */
(function () {
  const API = window.LibraryAPI;
  if (!API) return;

  const app = document.getElementById('app');

  function escapeHtml(s) {
    if (s == null) return '';
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  function el(id) { return document.getElementById(id); }

  function getRoute() {
    const h = (location.hash || '#').slice(1);
    return h || '';
  }

  function setActiveNav(route) {
    document.querySelectorAll('.nav-links a').forEach(a => {
      a.classList.toggle('active', (a.getAttribute('data-route') || '') === route);
    });
  }

  // ----- Dashboard -----
  function viewDashboard() {
    app.innerHTML = '<h1 class="page-title">Dashboard</h1><p class="page-subtitle">Library overview</p>' +
      '<div id="stats" class="stats-grid">' +
      '<div class="stat-card primary"><h3 id="stat-books">–</h3><p>Total Books</p></div>' +
      '<div class="stat-card success"><h3 id="stat-members">–</h3><p>Active Members</p></div>' +
      '<div class="stat-card warning"><h3 id="stat-overdue">–</h3><p>Overdue</p></div>' +
      '<div class="stat-card danger"><h3 id="stat-rentals">–</h3><p>Active Rentals</p></div></div>' +
      '<div class="card"><div class="card-header">Outstanding Fines</div><div class="card-body"><p id="stat-fines" style="font-size:1.5rem;font-weight:700;margin:0;">–</p></div></div>' +
      '<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem" class="two-col">' +
      '<div class="card"><div class="card-header">Recent Rentals</div><div class="card-body"><div id="recent-rentals" class="table-wrap"></div></div></div>' +
      '<div class="card"><div class="card-header">Overdue Books</div><div class="card-body"><div id="overdue-books" class="table-wrap"></div></div></div></div>';
    API.stats().then(s => {
      el('stat-books').textContent = (s.total_books || 0) + ' (' + (s.total_copies || 0) + ' copies)';
      el('stat-members').textContent = s.active_members || 0;
      el('stat-overdue').textContent = s.overdue_count || 0;
      el('stat-rentals').textContent = s.active_rentals || 0;
      el('stat-fines').textContent = '$' + Number(s.outstanding_fines != null ? s.outstanding_fines : 0).toFixed(2) + ' outstanding';
    }).catch(() => { if (el('stat-fines')) el('stat-fines').textContent = 'Unable to load stats'; });
    API.recentRentals().then(rows => {
      const w = el('recent-rentals');
      if (!w) return;
      if (!rows || !rows.length) { w.innerHTML = '<p class="empty-state">No recent rentals</p>'; return; }
      w.innerHTML = '<table><thead><tr><th>Book</th><th>Member</th><th>Date</th><th>Status</th></tr></thead><tbody>' +
        rows.map(r => '<tr><td>' + escapeHtml(r.title) + '</td><td>' + escapeHtml(r.member_name) + '</td><td>' + (r.rental_date || '') + '</td><td><span class="badge ' + (r.status === 'active' ? 'success' : 'warning') + '">' + escapeHtml(r.status) + '</span></td></tr>').join('') + '</tbody></table>';
    }).catch(() => { if (el('recent-rentals')) el('recent-rentals').innerHTML = '<p class="empty-state">No recent rentals</p>'; });
    API.overdue().then(rows => {
      const w = el('overdue-books');
      if (!w) return;
      if (!rows || !rows.length) { w.innerHTML = '<p class="empty-state">No overdue books</p>'; return; }
      w.innerHTML = '<table><thead><tr><th>Book</th><th>Member</th><th>Days Overdue</th></tr></thead><tbody>' +
        rows.map(r => '<tr><td>' + escapeHtml(r.title) + '</td><td>' + escapeHtml(r.member_name) + '</td><td><span class="badge danger">' + (r.days_overdue || 0) + ' days</span></td></tr>').join('') + '</tbody></table>';
    }).catch(() => { if (el('overdue-books')) el('overdue-books').innerHTML = '<p class="empty-state">No overdue books</p>'; });
  }

  // ----- Books -----
  function badgeClass(status) {
    if (status === 'Available') return 'success';
    if (status === 'Low Stock') return 'warning';
    return 'danger';
  }

  function viewBooks() {
    app.innerHTML = '<div class="actions"><h1 class="page-title" style="margin:0">Books</h1><button type="button" class="btn btn-primary" id="btn-add">+ Add Book</button></div><p class="page-subtitle">Catalog</p>' +
      '<div class="card"><div class="card-body">' +
      '<div class="filters"><div class="form-group"><label>Search</label><input type="text" id="filter-search" placeholder="Title, author, ISBN"></div>' +
      '<div class="form-group"><label>Category</label><select id="filter-category"><option value="All">All</option></select></div>' +
      '<button type="button" class="btn btn-primary" id="btn-search">Search</button></div>' +
      '<div id="table-wrap" class="table-wrap"></div></div></div>' +
      '<div id="modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.4);z-index:10;align-items:center;justify-content:center;"><div style="background:white;padding:1.5rem;border-radius:8px;max-width:480px;width:90%;max-height:90vh;overflow:auto;">' +
      '<h2 style="margin-top:0" id="modal-title">Add Book</h2><form id="form-book">' +
      '<input type="hidden" id="book-id"><div class="form-group"><label>ISBN *</label><input type="text" id="book-isbn" required></div>' +
      '<div class="form-group"><label>Title *</label><input type="text" id="book-title" required></div><div class="form-group"><label>Author *</label><input type="text" id="book-author" required></div>' +
      '<div class="form-group"><label>Publisher</label><input type="text" id="book-publisher"></div><div class="form-group"><label>Publication Year</label><input type="number" id="book-year" min="1400" max="2030"></div>' +
      '<div class="form-group"><label>Category</label><input type="text" id="book-category"></div><div class="form-group"><label>Total Copies *</label><input type="number" id="book-total" min="0" value="1" required></div>' +
      '<div class="form-group"><label>Available Copies *</label><input type="number" id="book-available" min="0" value="1" required></div>' +
      '<div style="display:flex;gap:0.5rem;margin-top:1rem"><button type="submit" class="btn btn-primary">Save</button><button type="button" class="btn btn-secondary" id="btn-cancel">Cancel</button></div></form></div></div>';
    const modal = el('modal');
    const form = el('form-book');

    function loadCategories() {
      API.categories().then(cats => {
        const sel = el('filter-category');
        if (!sel) return;
        const current = sel.value;
        sel.innerHTML = '<option value="All">All</option>' + (cats || []).map(c => '<option value="' + escapeHtml(c) + '"' + (c === current ? ' selected' : '') + '>' + escapeHtml(c) + '</option>').join('');
      });
    }

    function loadBooks() {
      const search = (el('filter-search') || {}).value || '';
      const category = (el('filter-category') || {}).value || 'All';
      const params = {};
      if (search) params.search = search;
      if (category !== 'All') params.category = category;
      API.books(params).then(rows => {
        const wrap = el('table-wrap');
        if (!wrap) return;
        if (!rows || !rows.length) { wrap.innerHTML = '<p class="empty-state">No books found</p>'; return; }
        wrap.innerHTML = '<table><thead><tr><th>ISBN</th><th>Title</th><th>Author</th><th>Category</th><th>Copies</th><th>Available</th><th>Status</th><th>Actions</th></tr></thead><tbody>' +
          rows.map(b => '<tr><td><small>' + escapeHtml(b.isbn) + '</small></td><td><strong>' + escapeHtml(b.title) + '</strong></td><td>' + escapeHtml(b.author) + '</td><td>' + (b.category ? '<span class="badge secondary">' + escapeHtml(b.category) + '</span>' : '–') + '</td><td>' + b.total_copies + '</td><td>' + b.available_copies + '</td><td><span class="badge ' + badgeClass(b.status) + '">' + escapeHtml(b.status) + '</span></td><td><div style="display:flex;gap:0.4rem;flex-wrap:nowrap"><button type="button" class="btn btn-secondary" data-edit="' + b.book_id + '">Edit</button><button type="button" class="btn btn-danger" data-delete="' + b.book_id + '">Delete</button></div></td></tr>').join('') + '</tbody></table>';
        wrap.querySelectorAll('[data-edit]').forEach(btn => btn.addEventListener('click', () => openEdit(parseInt(btn.dataset.edit, 10))));
        wrap.querySelectorAll('[data-delete]').forEach(btn => btn.addEventListener('click', () => { if (confirm('Delete this book?')) API.deleteBook(parseInt(btn.dataset.delete, 10)).then(() => loadBooks()).catch(() => alert('Delete failed')); }));
      }).catch(() => { const w = el('table-wrap'); if (w) w.innerHTML = '<p class="alert alert-error">Failed to load books</p>'; });
    }

    function openAdd() {
      el('modal-title').textContent = 'Add Book';
      el('book-id').value = '';
      form.reset();
      el('book-total').value = '1';
      el('book-available').value = '1';
      modal.style.display = 'flex';
    }

    function openEdit(id) {
      API.books().then(rows => {
        const b = (rows || []).find(r => r.book_id === id);
        if (!b) return;
        el('modal-title').textContent = 'Edit Book';
        el('book-id').value = b.book_id;
        el('book-isbn').value = b.isbn;
        el('book-isbn').readOnly = true;
        el('book-title').value = b.title;
        el('book-author').value = b.author;
        el('book-publisher').value = b.publisher || '';
        el('book-year').value = b.publication_year || '';
        el('book-category').value = b.category || '';
        el('book-total').value = b.total_copies;
        el('book-available').value = b.available_copies;
        modal.style.display = 'flex';
      });
    }

    form.addEventListener('submit', e => {
      e.preventDefault();
      const id = el('book-id').value;
      const payload = { isbn: el('book-isbn').value, title: el('book-title').value, author: el('book-author').value, publisher: el('book-publisher').value || null, publication_year: el('book-year').value ? parseInt(el('book-year').value, 10) : null, category: el('book-category').value || null, total_copies: parseInt(el('book-total').value, 10), available_copies: parseInt(el('book-available').value, 10) };
      (id ? API.updateBook(parseInt(id, 10), payload) : API.addBook(payload)).then(() => { modal.style.display = 'none'; loadBooks(); }).catch(() => alert('Save failed'));
    });
    el('btn-cancel').addEventListener('click', () => { modal.style.display = 'none'; if (el('book-isbn')) el('book-isbn').readOnly = false; });
    el('btn-add').addEventListener('click', openAdd);
    el('btn-search').addEventListener('click', loadBooks);
    loadCategories();
    loadBooks();
  }

  // ----- Members -----
  function viewMembers() {
    app.innerHTML = '<div class="actions"><h1 class="page-title" style="margin:0">Members</h1><button type="button" class="btn btn-primary" id="btn-add">+ Add Member</button></div><p class="page-subtitle">Directory</p>' +
      '<div class="card"><div class="card-body">' +
      '<div class="filters"><div class="form-group"><label>Search</label><input type="text" id="filter-search" placeholder="Name or email"></div>' +
      '<div class="form-group"><label>Type</label><select id="filter-type"><option value="All">All</option><option value="Student">Student</option><option value="Faculty">Faculty</option><option value="Staff">Staff</option></select></div>' +
      '<div class="form-group"><label>Status</label><select id="filter-status"><option value="All">All</option><option value="active">Active</option><option value="suspended">Suspended</option><option value="expired">Expired</option></select></div>' +
      '<button type="button" class="btn btn-primary" id="btn-search">Search</button></div><div id="table-wrap" class="table-wrap"></div></div></div>' +
      '<div id="modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.4);z-index:10;align-items:center;justify-content:center;"><div style="background:white;padding:1.5rem;border-radius:8px;max-width:480px;width:90%;max-height:90vh;overflow:auto;">' +
      '<h2 style="margin-top:0" id="modal-title">Add Member</h2><form id="form-member">' +
      '<input type="hidden" id="member-id"><div class="form-group"><label>First Name *</label><input type="text" id="member-first" required></div><div class="form-group"><label>Last Name *</label><input type="text" id="member-last" required></div>' +
      '<div class="form-group"><label>Email *</label><input type="email" id="member-email" required></div><div class="form-group"><label>Phone</label><input type="text" id="member-phone"></div>' +
      '<div class="form-group"><label>Membership Type *</label><select id="member-type"><option value="Student">Student</option><option value="Faculty">Faculty</option><option value="Staff">Staff</option></select></div>' +
      '<div class="form-group"><label>Max Books Allowed *</label><input type="number" id="member-maxbooks" min="1" value="5" required></div>' +
      '<div style="display:flex;gap:0.5rem;margin-top:1rem"><button type="submit" class="btn btn-primary">Save</button><button type="button" class="btn btn-secondary" id="btn-cancel">Cancel</button></div></form></div></div>';
    const modal = el('modal');
    const form = el('form-member');

    function loadMembers() {
      const search = (el('filter-search') || {}).value || '';
      const type = (el('filter-type') || {}).value || 'All';
      const status = (el('filter-status') || {}).value || 'All';
      const params = {};
      if (search) params.search = search;
      if (type !== 'All') params.type = type;
      if (status !== 'All') params.status = status;
      API.members(params).then(rows => {
        const wrap = el('table-wrap');
        if (!wrap) return;
        if (!rows || !rows.length) { wrap.innerHTML = '<p class="empty-state">No members found</p>'; return; }
        wrap.innerHTML = '<table><thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Type</th><th>Status</th><th>Max Books</th><th>Actions</th></tr></thead><tbody>' +
          rows.map(m => '<tr><td>' + m.member_id + '</td><td><strong>' + escapeHtml(m.name) + '</strong></td><td>' + escapeHtml(m.email) + '</td><td><span class="badge secondary">' + escapeHtml(m.membership_type) + '</span></td><td><span class="badge ' + (m.status === 'active' ? 'success' : 'warning') + '">' + escapeHtml(m.status) + '</span></td><td>' + m.max_books_allowed + '</td><td><button type="button" class="btn btn-secondary" data-edit="' + m.member_id + '">Edit</button></td></tr>').join('') + '</tbody></table>';
        wrap.querySelectorAll('[data-edit]').forEach(btn => btn.addEventListener('click', () => openEdit(parseInt(btn.dataset.edit, 10))));
      }).catch(() => { const w = el('table-wrap'); if (w) w.innerHTML = '<p class="alert alert-error">Failed to load members</p>'; });
    }

    function openAdd() {
      el('modal-title').textContent = 'Add Member';
      el('member-id').value = '';
      form.reset();
      el('member-type').value = 'Student';
      el('member-maxbooks').value = '5';
      modal.style.display = 'flex';
    }

    function openEdit(id) {
      API.members().then(rows => {
        const m = (rows || []).find(r => r.member_id === id);
        if (!m) return;
        el('modal-title').textContent = 'Edit Member';
        el('member-id').value = m.member_id;
        el('member-first').value = m.first_name;
        el('member-last').value = m.last_name;
        el('member-email').value = m.email;
        el('member-phone').value = m.phone || '';
        el('member-type').value = m.membership_type;
        el('member-maxbooks').value = m.max_books_allowed;
        modal.style.display = 'flex';
      });
    }

    form.addEventListener('submit', e => {
      e.preventDefault();
      const id = el('member-id').value;
      const payload = { first_name: el('member-first').value, last_name: el('member-last').value, email: el('member-email').value, phone: el('member-phone').value || null, membership_type: el('member-type').value, max_books_allowed: parseInt(el('member-maxbooks').value, 10) };
      (id ? API.updateMember(parseInt(id, 10), payload) : API.addMember(payload)).then(() => { modal.style.display = 'none'; loadMembers(); }).catch(() => alert('Save failed'));
    });
    el('btn-cancel').addEventListener('click', () => { modal.style.display = 'none'; });
    el('btn-add').addEventListener('click', openAdd);
    el('btn-search').addEventListener('click', loadMembers);
    loadMembers();
  }

  // ----- Rentals -----
  function viewRentals() {
    app.innerHTML = '<div class="actions"><h1 class="page-title" style="margin:0">Active Rentals</h1><a href="#checkout" class="btn btn-primary">Checkout Book</a></div><p class="page-subtitle">Currently checked out</p><div class="card"><div class="card-body"><div id="table-wrap" class="table-wrap"></div></div></div>';
    API.rentals().then(rows => {
      const wrap = el('table-wrap');
      if (!wrap) return;
      if (!rows || !rows.length) { wrap.innerHTML = '<p class="empty-state">No active rentals. <a href="#checkout">Check out a book</a>.</p>'; return; }
      wrap.innerHTML = '<table><thead><tr><th>Rental ID</th><th>Book</th><th>Member</th><th>Rental Date</th><th>Due Date</th><th>Status</th><th>Days Overdue</th></tr></thead><tbody>' +
        rows.map(r => '<tr><td>' + r.rental_id + '</td><td><strong>' + escapeHtml(r.title) + '</strong><br><small>' + escapeHtml(r.author) + '</small></td><td>' + escapeHtml(r.member_name) + '<br><small>' + escapeHtml(r.email) + '</small></td><td>' + (r.rental_date || '') + '</td><td>' + (r.due_date || '') + '</td><td><span class="badge ' + (r.status === 'overdue' ? 'danger' : 'success') + '">' + escapeHtml(r.status) + '</span></td><td>' + (r.days_overdue > 0 ? '<span class="badge warning">' + r.days_overdue + ' days</span>' : '–') + '</td></tr>').join('') + '</tbody></table>';
    }).catch(() => { const w = el('table-wrap'); if (w) w.innerHTML = '<p class="alert alert-error">Failed to load rentals</p>'; });
  }

  // ----- Returns -----
  function viewReturns() {
    app.innerHTML = '<div class="actions"><h1 class="page-title" style="margin:0">Return History</h1><a href="#process-return" class="btn btn-primary">Process Return</a></div><p class="page-subtitle">Recent returns</p><div class="card"><div class="card-body"><div id="table-wrap" class="table-wrap"></div></div></div>';
    API.returns().then(rows => {
      const wrap = el('table-wrap');
      if (!wrap) return;
      if (!rows || !rows.length) { wrap.innerHTML = '<p class="empty-state">No returns yet. <a href="#process-return">Process a return</a>.</p>'; return; }
      wrap.innerHTML = '<table><thead><tr><th>Return ID</th><th>Book</th><th>Member</th><th>Rental Date</th><th>Due Date</th><th>Return Date</th><th>Condition</th><th>Days Overdue</th></tr></thead><tbody>' +
        rows.map(r => '<tr><td>' + r.return_id + '</td><td><strong>' + escapeHtml(r.title) + '</strong></td><td>' + escapeHtml(r.member_name) + '</td><td>' + (r.rental_date || '') + '</td><td>' + (r.due_date || '') + '</td><td>' + (r.return_date || '') + '</td><td><span class="badge secondary">' + escapeHtml(r.condition_on_return || '') + '</span></td><td>' + (r.days_overdue > 0 ? '<span class="badge warning">' + r.days_overdue + '</span>' : '–') + '</td></tr>').join('') + '</tbody></table>';
    }).catch(() => { const w = el('table-wrap'); if (w) w.innerHTML = '<p class="alert alert-error">Failed to load returns</p>'; });
  }

  // ----- Checkout -----
  function viewCheckout() {
    const today = new Date().toISOString().slice(0, 10);
    const due = new Date();
    due.setDate(due.getDate() + 14);
    app.innerHTML = '<a href="#rentals" class="back-link">← Back to Rentals</a><h1 class="page-title">Checkout Book</h1><p class="page-subtitle">Create a new rental</p>' +
      '<div class="card" style="max-width:480px"><div class="card-body"><form id="form-checkout">' +
      '<div class="form-group"><label>Member *</label><select id="member-id" required></select></div>' +
      '<div class="form-group"><label>Book *</label><select id="book-id" required></select></div>' +
      '<div class="form-group"><label>Rental Date *</label><input type="date" id="rental-date" required></div>' +
      '<div class="form-group"><label>Due Date *</label><input type="date" id="due-date" required></div>' +
      '<button type="submit" class="btn btn-primary">Check Out</button></form></div></div>';
    el('rental-date').value = today;
    el('due-date').value = due.toISOString().slice(0, 10);
    API.members().then(rows => {
      const sel = el('member-id');
      sel.innerHTML = '<option value="">Select member</option>' + (rows || []).map(m => '<option value="' + m.member_id + '">' + (m.name || m.first_name + ' ' + m.last_name) + ' (' + m.email + ')</option>').join('');
    });
    API.books().then(rows => {
      const available = (rows || []).filter(b => b.available_copies > 0);
      el('book-id').innerHTML = '<option value="">Select book</option>' + available.map(b => '<option value="' + b.book_id + '">' + b.title + ' – ' + b.author + ' (avail: ' + b.available_copies + ')</option>').join('');
    });
    el('form-checkout').addEventListener('submit', e => {
      e.preventDefault();
      const payload = { member_id: parseInt(el('member-id').value, 10), book_id: parseInt(el('book-id').value, 10), rental_date: el('rental-date').value, due_date: el('due-date').value };
      API.checkout(payload).then(() => { alert('Checkout successful'); location.hash = 'rentals'; }).catch(() => alert('Checkout failed'));
    });
  }

  // ----- Process Return -----
  function viewProcessReturn() {
    app.innerHTML = '<a href="#returns" class="back-link">← Back to Returns</a><h1 class="page-title">Process Return</h1><p class="page-subtitle">Record a book return</p>' +
      '<div class="card" style="max-width:480px"><div class="card-body"><form id="form-return">' +
      '<div class="form-group"><label>Rental *</label><select id="rental-id" required></select></div>' +
      '<div class="form-group"><label>Return Date *</label><input type="date" id="return-date" required></div>' +
      '<div class="form-group"><label>Condition *</label><select id="condition"><option value="Good">Good</option><option value="Damaged">Damaged</option><option value="Lost">Lost</option></select></div>' +
      '<button type="submit" class="btn btn-primary">Submit Return</button></form></div></div>';
    el('return-date').value = new Date().toISOString().slice(0, 10);
    API.activeRentalsForReturn().then(rows => {
      el('rental-id').innerHTML = '<option value="">Select rental</option>' + (rows || []).map(r => '<option value="' + r.rental_id + '">' + r.rental_id + ' – ' + r.title + ' (by ' + r.member_name + ', due ' + r.due_date + ')</option>').join('');
    });
    el('form-return').addEventListener('submit', e => {
      e.preventDefault();
      const payload = { rental_id: parseInt(el('rental-id').value, 10), return_date: el('return-date').value, condition_status: el('condition').value };
      API.processReturn(payload).then(() => { alert('Return recorded successfully.'); location.hash = 'returns'; }).catch(() => alert('Return failed'));
    });
  }

  // ----- Fines -----
  function viewFines() {
    app.innerHTML = '<h1 class="page-title">Fines</h1><p class="page-subtitle">Fine records</p>' +
      '<div class="card"><div class="card-body">' +
      '<div class="filters"><div class="form-group"><label>Status</label><select id="filter-status"><option value="All">All</option><option value="unpaid">Unpaid</option><option value="partial">Partial</option><option value="paid">Paid</option></select></div>' +
      '<button type="button" class="btn btn-primary" id="btn-search">Apply</button></div><div id="table-wrap" class="table-wrap"></div></div></div>';
    function load() {
      const status = (el('filter-status') || {}).value || 'All';
      const params = status !== 'All' ? { status } : {};
      API.fines(params).then(rows => {
        const wrap = el('table-wrap');
        if (!wrap) return;
        if (!rows || !rows.length) { wrap.innerHTML = '<p class="empty-state">No fines found</p>'; return; }
        wrap.innerHTML = '<table><thead><tr><th>Fine ID</th><th>Member</th><th>Book</th><th>Reason</th><th>Amount</th><th>Paid</th><th>Outstanding</th><th>Status</th><th>Date</th></tr></thead><tbody>' +
          rows.map(f => '<tr><td>' + f.fine_id + '</td><td>' + escapeHtml(f.member_name) + '</td><td>' + escapeHtml(f.book_title) + '</td><td>' + escapeHtml(f.fine_reason) + '</td><td>$' + Number(f.fine_amount).toFixed(2) + '</td><td>$' + Number(f.paid_amount || 0).toFixed(2) + '</td><td><strong>$' + Number(f.outstanding || 0).toFixed(2) + '</strong></td><td><span class="badge ' + (f.paid_status === 'paid' ? 'success' : 'warning') + '">' + escapeHtml(f.paid_status) + '</span></td><td>' + (f.fine_date || '') + '</td></tr>').join('') + '</tbody></table>';
      }).catch(() => { const w = el('table-wrap'); if (w) w.innerHTML = '<p class="alert alert-error">Failed to load fines</p>'; });
    }
    el('btn-search').addEventListener('click', load);
    load();
  }

  // ----- Reports hub -----
  function viewReports() {
    const reportMeta = [
      { id: 1, icon: '⚠️', title: 'Overdue Books', desc: 'Past-due active and overdue rentals' },
      { id: 2, icon: '📚', title: 'Book Availability', desc: 'Catalog stock and loan availability' },
      { id: 3, icon: '🆕', title: 'Never Borrowed Books', desc: 'Books with no rental history' },
      { id: 4, icon: '💵', title: 'Fines by Member', desc: 'Total fines, paid amount, outstanding balance' },
      { id: 5, icon: '📈', title: 'Most Popular Books', desc: 'Top borrowed titles by rental count' },
      { id: 6, icon: '🧾', title: 'Rental + Return History', desc: 'Rental timeline with return timing status' },
      { id: 7, icon: '🗓️', title: 'Recent Rentals (7 Days)', desc: 'All checkouts created in the last week' },
      { id: 8, icon: '🛠️', title: 'Damaged or Lost Returns', desc: 'Condition issues and related fines' },
      { id: 9, icon: '📅', title: 'Monthly Rental Activity', desc: 'Monthly totals, members, and unique books' },
      { id: 10, icon: '💰', title: 'Unpaid/Partial Fines', desc: 'Open fine balances by member and book' }
    ];
    const cards = reportMeta.map(r =>
      '<a href="#report-' + r.id + '" class="report-card"><div class="icon">' + r.icon + '</div><h3>' + escapeHtml(r.title) + '</h3><p>' + escapeHtml(r.desc) + '</p><span class="btn btn-secondary">View Report</span></a>'
    ).join('');
    app.innerHTML = '<h1 class="page-title">Reports</h1><p class="page-subtitle">Database reports and analytics</p><div class="report-grid">' + cards + '</div>';
  }

  function viewReportById(id) {
    app.innerHTML = '<a href="#reports" class="back-link">← Back to Reports</a><h1 class="page-title">Report ' + id + '</h1><p class="page-subtitle">Query ' + id + ' results</p><div class="card"><div class="card-body"><div id="table-wrap" class="table-wrap"></div></div></div>';
    API.report(id).then(rows => {
      const wrap = el('table-wrap');
      if (!wrap) return;
      if (!rows || !rows.length) {
        wrap.innerHTML = '<p class="empty-state">No rows returned.</p>';
        return;
      }
      const cols = Object.keys(rows[0]);
      wrap.innerHTML = '<table><thead><tr>' + cols.map(c => '<th>' + escapeHtml(c.replaceAll('_', ' ')) + '</th>').join('') + '</tr></thead><tbody>' +
        rows.map(r => '<tr>' + cols.map(c => '<td>' + escapeHtml(String(r[c] == null ? '' : r[c])) + '</td>').join('') + '</tr>').join('') +
        '</tbody></table>';
    }).catch(() => {
      const w = el('table-wrap');
      if (w) w.innerHTML = '<p class="alert alert-error">Failed to load report.</p>';
    });
  }

  // ----- Report: Overdue -----
  function viewReportOverdue() {
    app.innerHTML = '<a href="#reports" class="back-link">← Back to Reports</a><h1 class="page-title">Overdue Books</h1><p class="page-subtitle">Books past due date</p><div class="card"><div class="card-body"><div id="table-wrap" class="table-wrap"></div></div></div>';
    API.reportOverdue().then(rows => {
      const wrap = el('table-wrap');
      if (!wrap) return;
      if (!rows || !rows.length) { wrap.innerHTML = '<p class="empty-state">No overdue books.</p>'; return; }
      wrap.innerHTML = '<table><thead><tr><th>Rental</th><th>Book</th><th>Member</th><th>Due</th><th>Days Overdue</th><th>Est. Fine</th></tr></thead><tbody>' +
        rows.map(r => '<tr><td>' + r.rental_id + '</td><td><strong>' + escapeHtml(r.book_title) + '</strong><br><small>' + escapeHtml(r.author) + '</small></td><td>' + escapeHtml(r.member_name) + '</td><td>' + (r.due_date || '') + '</td><td><span class="badge danger">' + (r.days_overdue || 0) + '</span></td><td>$' + Number(r.estimated_fine || 0).toFixed(2) + '</td></tr>').join('') + '</tbody></table>';
    }).catch(() => { const w = el('table-wrap'); if (w) w.innerHTML = '<p class="alert alert-error">Failed to load or view not found.</p>'; });
  }

  // ----- Report: Unpaid Fines -----
  function viewReportUnpaidFines() {
    app.innerHTML = '<a href="#reports" class="back-link">← Back to Reports</a><h1 class="page-title">Unpaid Fines</h1><p class="page-subtitle">Outstanding balances</p><div class="card"><div class="card-body"><div id="table-wrap" class="table-wrap"></div></div></div>';
    API.reportUnpaidFines().then(rows => {
      const wrap = el('table-wrap');
      if (!wrap) return;
      if (!rows || !rows.length) { wrap.innerHTML = '<p class="empty-state">No unpaid fines.</p>'; return; }
      wrap.innerHTML = '<table><thead><tr><th>Fine ID</th><th>Member</th><th>Book</th><th>Amount</th><th>Paid</th><th>Outstanding</th><th>Status</th></tr></thead><tbody>' +
        rows.map(r => '<tr><td>' + r.fine_id + '</td><td>' + escapeHtml(r.member_name) + '</td><td>' + escapeHtml(r.book_title) + '</td><td>$' + Number(r.fine_amount || 0).toFixed(2) + '</td><td>$' + Number(r.paid_amount || 0).toFixed(2) + '</td><td><strong>$' + Number(r.outstanding_balance != null ? r.outstanding_balance : (r.fine_amount - (r.paid_amount || 0))).toFixed(2) + '</strong></td><td><span class="badge warning">' + escapeHtml(r.paid_status) + '</span></td></tr>').join('') + '</tbody></table>';
    }).catch(() => { const w = el('table-wrap'); if (w) w.innerHTML = '<p class="alert alert-error">Failed to load or view not found.</p>'; });
  }

  // ----- Report: Popular -----
  function viewReportPopular() {
    app.innerHTML = '<a href="#reports" class="back-link">← Back to Reports</a><h1 class="page-title">Popular Books</h1><p class="page-subtitle">Most borrowed titles</p><div class="card"><div class="card-body"><div id="table-wrap" class="table-wrap"></div></div></div>';
    API.reportPopular().then(rows => {
      const wrap = el('table-wrap');
      if (!wrap) return;
      if (!rows || !rows.length) { wrap.innerHTML = '<p class="empty-state">No data.</p>'; return; }
      wrap.innerHTML = '<table><thead><tr><th>#</th><th>Title</th><th>Author</th><th>Category</th><th>Times Borrowed</th><th>Copies</th><th>Available</th></tr></thead><tbody>' +
        rows.map((r, i) => '<tr><td>' + (i + 1) + '</td><td><strong>' + escapeHtml(r.title) + '</strong></td><td>' + escapeHtml(r.author) + '</td><td>' + (r.category ? '<span class="badge secondary">' + escapeHtml(r.category) + '</span>' : '–') + '</td><td><span class="badge primary">' + (r.times_borrowed || 0) + '</span></td><td>' + (r.total_copies || '') + '</td><td>' + (r.available_copies != null ? r.available_copies : '') + '</td></tr>').join('') + '</tbody></table>';
    }).catch(() => { const w = el('table-wrap'); if (w) w.innerHTML = '<p class="alert alert-error">Failed to load or view not found.</p>'; });
  }

  // ----- Report: Availability -----
  function viewReportAvailability() {
    app.innerHTML = '<a href="#reports" class="back-link">← Back to Reports</a><h1 class="page-title">Book Availability</h1><p class="page-subtitle">Stock and availability</p><div class="card"><div class="card-body"><div id="table-wrap" class="table-wrap"></div></div></div>';
    API.reportAvailability().then(rows => {
      const wrap = el('table-wrap');
      if (!wrap) return;
      if (!rows || !rows.length) { wrap.innerHTML = '<p class="empty-state">No data.</p>'; return; }
      wrap.innerHTML = '<table><thead><tr><th>ISBN</th><th>Title</th><th>Author</th><th>Total</th><th>Available</th><th>On Loan</th><th>Status</th></tr></thead><tbody>' +
        rows.map(r => '<tr><td><small>' + escapeHtml(r.isbn) + '</small></td><td><strong>' + escapeHtml(r.title) + '</strong></td><td>' + escapeHtml(r.author) + '</td><td>' + (r.total_copies || '') + '</td><td>' + (r.available_copies != null ? r.available_copies : '') + '</td><td>' + (r.copies_on_loan != null ? r.copies_on_loan : '') + '</td><td><span class="badge ' + (r.availability_status === 'Available' ? 'success' : r.availability_status === 'Unavailable' ? 'danger' : 'warning') + '">' + escapeHtml(r.availability_status) + '</span></td></tr>').join('') + '</tbody></table>';
    }).catch(() => { const w = el('table-wrap'); if (w) w.innerHTML = '<p class="alert alert-error">Failed to load or view not found.</p>'; });
  }

  const routes = {
    '': viewDashboard,
    'dashboard': viewDashboard,
    'books': viewBooks,
    'members': viewMembers,
    'rentals': viewRentals,
    'returns': viewReturns,
    'checkout': viewCheckout,
    'process-return': viewProcessReturn,
    'fines': viewFines,
    'reports': viewReports,
    'report-overdue': viewReportOverdue,
    'report-unpaid-fines': viewReportUnpaidFines,
    'report-popular': viewReportPopular,
    'report-availability': viewReportAvailability
  };

  function render() {
    const route = getRoute();
    const reportMatch = /^report-(\d+)$/.exec(route);
    if (reportMatch) {
      viewReportById(parseInt(reportMatch[1], 10));
      setActiveNav('reports');
      return;
    }
    const view = routes[route] || viewDashboard;
    view();
    setActiveNav(route === 'dashboard' ? 'dashboard' : route === 'checkout' ? 'rentals' : route === 'process-return' ? 'returns' : route.startsWith('report-') ? 'reports' : route);
  }

  window.addEventListener('hashchange', render);
  render();
})();
