/**
 * API client - Books, Members, Rentals, Returns, Fines only
 */
(function () {
  const base = window.API_BASE || '';
  const api = (path) => {
    const url = path.startsWith('http') ? path : base + '/api' + (path.startsWith('/') ? path : '/' + path);
    return fetch(url, { headers: { 'Content-Type': 'application/json' } }).then(r => {
      if (!r.ok) throw new Error(r.statusText || 'Request failed');
      return r.json();
    });
  };

  window.LibraryAPI = {
    books: () => api('/books'),
    members: () => api('/members'),
    rentals: () => api('/rentals'),
    returns: () => api('/returns'),
    fines: () => api('/fines')
  };
})();
