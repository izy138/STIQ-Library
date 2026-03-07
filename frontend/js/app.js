
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
    return (location.hash || '#books').slice(1) || 'books';
  }

  function setActiveNav(route) {
    document.querySelectorAll('.nav-links a').forEach(a => {
      a.classList.toggle('active', (a.getAttribute('data-route') || '') === route);
    });
  }

  function badgeClass(status) {
    if (status === 'Available') return 'success';
    if (status === 'Low Stock') return 'warning';
    return 'danger';
  }

  function viewBooks() {
    app.innerHTML = '<h1 class="page-title">Books</h1><p class="page-subtitle">Catalog</p><div class="card"><div class="card-body"><div id="table-wrap" class="table-wrap"></div></div></div>';
    API.books().then(rows => {
      const wrap = el('table-wrap');
      if (!rows || !rows.length) { wrap.innerHTML = '<p class="empty-state">No books found</p>'; return; }
      wrap.innerHTML = '<table><thead><tr><th>ISBN</th><th>Title</th><th>Author</th><th>Category</th><th>Copies</th><th>Available</th><th>Status</th></tr></thead><tbody>' +
        rows.map(b => '<tr><td><small>' + escapeHtml(b.isbn) + '</small></td><td><strong>' + escapeHtml(b.title) + '</strong></td><td>' + escapeHtml(b.author) + '</td><td>' + (b.category ? '<span class="badge secondary">' + escapeHtml(b.category) + '</span>' : '–') + '</td><td>' + b.total_copies + '</td><td>' + b.available_copies + '</td><td><span class="badge ' + badgeClass(b.status) + '">' + escapeHtml(b.status) + '</span></td></tr>').join('') + '</tbody></table>';
    }).catch(() => { el('table-wrap').innerHTML = '<p class="alert-error">Failed to load books</p>'; });
  }

  function viewMembers() {
    app.innerHTML = '<h1 class="page-title">Members</h1><p class="page-subtitle">Directory</p><div class="card"><div class="card-body"><div id="table-wrap" class="table-wrap"></div></div></div>';
    API.members().then(rows => {
      const wrap = el('table-wrap');
      if (!rows || !rows.length) { wrap.innerHTML = '<p class="empty-state">No members found</p>'; return; }
      wrap.innerHTML = '<table><thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Type</th><th>Status</th><th>Max Books</th></tr></thead><tbody>' +
        rows.map(m => '<tr><td>' + m.member_id + '</td><td><strong>' + escapeHtml(m.name) + '</strong></td><td>' + escapeHtml(m.email) + '</td><td><span class="badge secondary">' + escapeHtml(m.membership_type) + '</span></td><td><span class="badge ' + (m.status === 'active' ? 'success' : 'warning') + '">' + escapeHtml(m.status) + '</span></td><td>' + m.max_books_allowed + '</td></tr>').join('') + '</tbody></table>';
    }).catch(() => { el('table-wrap').innerHTML = '<p class="alert-error">Failed to load members</p>'; });
  }

  function viewRentals() {
    app.innerHTML = '<h1 class="page-title">Rentals</h1><p class="page-subtitle">All rentals</p><div class="card"><div class="card-body"><div id="table-wrap" class="table-wrap"></div></div></div>';
    API.rentals().then(rows => {
      const wrap = el('table-wrap');
      if (!rows || !rows.length) { wrap.innerHTML = '<p class="empty-state">No rentals</p>'; return; }
      wrap.innerHTML = '<table><thead><tr><th>ID</th><th>Book</th><th>Member</th><th>Rental Date</th><th>Due Date</th><th>Status</th><th>Days Overdue</th></tr></thead><tbody>' +
        rows.map(r => '<tr><td>' + r.rental_id + '</td><td><strong>' + escapeHtml(r.title) + '</strong><br><small>' + escapeHtml(r.author) + '</small></td><td>' + escapeHtml(r.member_name) + '</td><td>' + (r.rental_date || '') + '</td><td>' + (r.due_date || '') + '</td><td><span class="badge ' + (r.status === 'overdue' ? 'danger' : r.status === 'active' ? 'success' : 'secondary') + '">' + escapeHtml(r.status) + '</span></td><td>' + (r.days_overdue > 0 ? '<span class="badge warning">' + r.days_overdue + '</span>' : '–') + '</td></tr>').join('') + '</tbody></table>';
    }).catch(() => { el('table-wrap').innerHTML = '<p class="alert-error">Failed to load rentals</p>'; });
  }

  function viewReturns() {
    app.innerHTML = '<h1 class="page-title">Returns</h1><p class="page-subtitle">Return history</p><div class="card"><div class="card-body"><div id="table-wrap" class="table-wrap"></div></div></div>';
    API.returns().then(rows => {
      const wrap = el('table-wrap');
      if (!rows || !rows.length) { wrap.innerHTML = '<p class="empty-state">No returns yet</p>'; return; }
      wrap.innerHTML = '<table><thead><tr><th>Return ID</th><th>Rental</th><th>Book</th><th>Member</th><th>Rental Date</th><th>Due Date</th><th>Return Date</th><th>Condition</th><th>Days Overdue</th></tr></thead><tbody>' +
        rows.map(r => '<tr><td>' + r.return_id + '</td><td>' + r.rental_id + '</td><td><strong>' + escapeHtml(r.title) + '</strong></td><td>' + escapeHtml(r.member_name) + '</td><td>' + (r.rental_date || '') + '</td><td>' + (r.due_date || '') + '</td><td>' + (r.return_date || '') + '</td><td><span class="badge secondary">' + escapeHtml(r.condition_on_return || '') + '</span></td><td>' + (r.days_overdue > 0 ? '<span class="badge warning">' + r.days_overdue + '</span>' : '–') + '</td></tr>').join('') + '</tbody></table>';
    }).catch(() => { el('table-wrap').innerHTML = '<p class="alert-error">Failed to load returns</p>'; });
  }

  function viewFines() {
    app.innerHTML = '<h1 class="page-title">Fines</h1><p class="page-subtitle">Fine records</p><div class="card"><div class="card-body"><div id="table-wrap" class="table-wrap"></div></div></div>';
    API.fines().then(rows => {
      const wrap = el('table-wrap');
      if (!rows || !rows.length) { wrap.innerHTML = '<p class="empty-state">No fines found</p>'; return; }
      wrap.innerHTML = '<table><thead><tr><th>Fine ID</th><th>Rental</th><th>Member</th><th>Book</th><th>Reason</th><th>Amount</th><th>Paid</th><th>Outstanding</th><th>Status</th><th>Date</th></tr></thead><tbody>' +
        rows.map(f => '<tr><td>' + f.fine_id + '</td><td>' + f.rental_id + '</td><td>' + escapeHtml(f.member_name) + '</td><td>' + escapeHtml(f.book_title) + '</td><td>' + escapeHtml(f.fine_reason) + '</td><td>$' + Number(f.fine_amount).toFixed(2) + '</td><td>$' + Number(f.paid_amount || 0).toFixed(2) + '</td><td><strong>$' + Number(f.outstanding || 0).toFixed(2) + '</strong></td><td><span class="badge ' + (f.paid_status === 'paid' ? 'success' : 'warning') + '">' + escapeHtml(f.paid_status) + '</span></td><td>' + (f.fine_date || '') + '</td></tr>').join('') + '</tbody></table>';
    }).catch(() => { el('table-wrap').innerHTML = '<p class="alert-error">Failed to load fines</p>'; });
  }

  const routes = {
    'books': viewBooks,
    'members': viewMembers,
    'rentals': viewRentals,
    'returns': viewReturns,
    'fines': viewFines
  };

  function render() {
    const route = getRoute();
    const view = routes[route] || viewBooks;
    view();
    setActiveNav(route);
  }

  window.addEventListener('hashchange', render);
  if (!location.hash) location.hash = 'books';
  render();
})();
