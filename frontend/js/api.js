/**
 * API client for Library Management System (vanilla frontend).
 */
(function () {
  const base = window.API_BASE || '';
  const api = (path, options = {}) => {
    const url = path.startsWith('http') ? path : base + '/api' + (path.startsWith('/') ? path : '/' + path);
    return fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options
    }).then(r => {
      if (!r.ok) throw new Error(r.statusText || 'Request failed');
      const ct = r.headers.get('content-type');
      if (ct && ct.includes('application/json')) return r.json();
      return r.text();
    });
  };

  window.LibraryAPI = {
    get: (path) => api(path),
    post: (path, body) => api(path, { method: 'POST', body: JSON.stringify(body) }),
    put: (path, body) => api(path, { method: 'PUT', body: JSON.stringify(body) }),
    delete: (path) => api(path, { method: 'DELETE' }),

    stats: () => api('/stats'),
    recentRentals: () => api('/dashboard/recent-rentals'),
    overdue: () => api('/dashboard/overdue'),

    books: (params) => api('/books' + (params && Object.keys(params).length ? '?' + new URLSearchParams(params) : '')),
    categories: () => api('/books/categories'),
    addBook: (data) => api('/books', { method: 'POST', body: JSON.stringify(data) }),
    updateBook: (id, data) => api('/books/' + id, { method: 'PUT', body: JSON.stringify(data) }),
    deleteBook: (id) => api('/books/' + id, { method: 'DELETE' }),

    members: (params) => api('/members' + (params && Object.keys(params).length ? '?' + new URLSearchParams(params) : '')),
    addMember: (data) => api('/members', { method: 'POST', body: JSON.stringify(data) }),
    updateMember: (id, data) => api('/members/' + id, { method: 'PUT', body: JSON.stringify(data) }),

    rentals: () => api('/rentals'),
    checkout: (data) => api('/rentals/checkout', { method: 'POST', body: JSON.stringify(data) }),

    returns: () => api('/returns'),
    activeRentalsForReturn: () => api('/returns/active-rentals'),
    processReturn: (data) => api('/returns', { method: 'POST', body: JSON.stringify(data) }),

    fines: (params) => api('/fines' + (params && Object.keys(params).length ? '?' + new URLSearchParams(params) : '')),

    report: (id) => api('/reports/' + encodeURIComponent(id)),
    reportOverdue: () => api('/reports/overdue'),
    reportUnpaidFines: () => api('/reports/unpaid-fines'),
    reportPopular: () => api('/reports/popular'),
    reportAvailability: () => api('/reports/availability')
  };
})();
