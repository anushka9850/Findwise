function toggleTheme() {
  document.body.classList.toggle('dark');
  localStorage.setItem('findwise-theme', document.body.classList.contains('dark') ? 'dark' : 'light');
}

function saveItem(button) {
  button.classList.toggle('active');
  button.textContent = button.classList.contains('active') ? '♥' : '♡';
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character]));
}

function liveCard(product) {
  const image = product.image
    ? `<img src="${escapeHtml(product.image)}" alt="${escapeHtml(product.name)}" loading="lazy">`
    : '<span class="image-fallback">image unavailable</span>';
  const meta = product.price !== null
    ? `$${Number(product.price).toFixed(2)}`
    : `${product.reviews} reviews`;
  const badge = product.stock !== null ? `${product.stock} IN STOCK` : 'TRENDING';
  return `<article class="card" data-brand="${escapeHtml(product.brand).toLowerCase()}" data-category="${escapeHtml(product.category).toLowerCase()}"><div class="product-image">${image}<button class="save" type="button" aria-label="Save ${escapeHtml(product.name)}" onclick="saveItem(this)">♡</button></div><div class="card-body"><div class="card-brand">${escapeHtml(product.brand)}</div><h3 title="${escapeHtml(product.name)}">${escapeHtml(product.name)}</h3><div class="meta"><span class="rating"><b>★</b> ${Number(product.rating).toFixed(1)} · ${meta}</span><span class="badge">${badge}</span></div></div></article>`;
}

async function refreshLiveProducts(button) {
  button.disabled = true;
  button.textContent = '↻ Fetching...';
  try {
    const response = await fetch('/api/live-products', { cache: 'no-store' });
    if (!response.ok) throw new Error('Live feed request failed');
    const payload = await response.json();
    document.getElementById('liveGrid').innerHTML = payload.products.map(liveCard).join('');
    document.getElementById('liveStatus').textContent = `● ${payload.status} · synced ${new Date().toLocaleTimeString()}`;
  } catch (error) {
    document.getElementById('liveStatus').textContent = '● Live feed unavailable · showing last results';
  } finally {
    button.disabled = false;
    button.textContent = '↻ Refresh';
  }
}

function filterCards() {
  const brand = document.getElementById('brandFilter')?.value || '';
  const category = document.getElementById('categoryFilter')?.value || '';
  document.querySelectorAll('#productGrid .card').forEach((card) => {
    const matchesBrand = !brand || card.dataset.brand.includes(brand);
    const matchesCategory = !category || card.dataset.category.includes(category);
    card.hidden = !(matchesBrand && matchesCategory);
  });
}

if (localStorage.getItem('findwise-theme') === 'dark') document.body.classList.add('dark');

const liveRefreshButton = document.querySelector('.refresh-button');
if (liveRefreshButton) setInterval(() => refreshLiveProducts(liveRefreshButton), 60000);
