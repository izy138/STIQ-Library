/**
 * API client for Library Management System frontend
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
    stats: () => api('/stats'),

    books: (params) => api('/books' + (params && Object.keys(params).length ? '?' + new URLSearchParams(params) : '')),
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

    fines: () => api('/fines'),

    query: (id) => api('/queries/' + encodeURIComponent(id))
  };
})();
