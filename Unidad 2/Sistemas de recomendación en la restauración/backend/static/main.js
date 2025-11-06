async function postJSON(url, data) {
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!resp.ok) throw new Error('HTTP ' + resp.status);
  return resp.json();
}
// helper to GET JSON
async function getJSON(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error('HTTP ' + r.status);
  return r.json();
}

let clients = [];

async function loadClients() {
  const sel = document.getElementById('clientSelect');
  // show loading placeholder
  sel.innerHTML = '';
  const loading = document.createElement('option');
  loading.value = '';
  loading.text = 'Cargando clientes...';
  loading.disabled = true;
  sel.appendChild(loading);
  try {
    clients = await getJSON('/clients');
    sel.innerHTML = '';
    const optNew = document.createElement('option');
    optNew.value = '';
    optNew.text = '— Nuevo / Ninguno —';
    sel.appendChild(optNew);
    if (!clients || clients.length === 0) {
      const none = document.createElement('option');
      none.value = '';
      none.text = 'No hay clientes aún';
      sel.appendChild(none);
      return;
    }
    clients.forEach(c => {
      const o = document.createElement('option');
      o.value = c.id;
      o.text = c.name;
      sel.appendChild(o);
    });
  } catch (err) {
    console.error('loadClients', err);
    sel.innerHTML = '';
    const errOpt = document.createElement('option');
    errOpt.value = '';
    errOpt.text = 'Error cargando clientes';
    errOpt.disabled = true;
    sel.appendChild(errOpt);
  }
}

async function getRecommendationsForClient(clientId) {
  try {
    const res = await postJSON(`/recommend/client/${clientId}`, {});
    return res;
  } catch (err) {
    console.error('getRecommendationsForClient', err);
    return [];
  }
}

function showResults(results, title) {
  const out = document.getElementById('results');
  const titleEl = document.getElementById('resultsTitle');
  titleEl.textContent = title || 'Resultados';
  out.innerHTML = '';
  if (!results || results.length === 0) {
    out.innerHTML = '<div class="muted">No hay recomendaciones.</div>';
    return;
  }
  results.forEach(r => {
    const div = document.createElement('div');
    div.className = 'dish';
    div.innerHTML = `<strong>${r.dish}</strong> <span style="color:${r.available? '#0b6':'#c33'}">${r.available? 'Disponible':'No disponible'}</span><br><small class="muted">Score: ${(r.score*100).toFixed(0)}%</small><div style="margin-top:6px" class="small">Ingredientes: ${r.ingredients.join(', ')}</div>`;
    out.appendChild(div);
  });
}

function lockFields(lock) {
  // some layouts removed the direct pref/restr inputs; guard them
  const prefEl = document.getElementById('pref');
  const restrEl = document.getElementById('restr');
  if (prefEl) prefEl.disabled = !!lock;
  if (restrEl) restrEl.disabled = !!lock;
}

function attachHandlers() {
  const clientSelect = document.getElementById('clientSelect');
  if (clientSelect) clientSelect.addEventListener('change', async (e) => {
    const val = e.target.value;
    if (!val) {
      // new client / none
      lockFields(false);
      // clear client details
      document.getElementById('cd_name').textContent = 'Nombre: —';
      document.getElementById('cd_pref').textContent = '—';
      document.getElementById('cd_restr').textContent = '—';
      document.getElementById('cd_allergies').textContent = '—';
      // clear results title
      showResults([], 'Resultados');
      return;
    }
    // existing client selected
    lockFields(true);
    // load client data
    const cid = parseInt(val, 10);
    try {
      const c = await getJSON(`/clients/${cid}`);
      // show details (we don't assume pref/restr inputs exist)
      const cdName = document.getElementById('cd_name');
      const cdPref = document.getElementById('cd_pref');
      const cdRestr = document.getElementById('cd_restr');
      const cdAll = document.getElementById('cd_allergies');
      if (cdName) cdName.textContent = `Nombre: ${c.name}`;
      if (cdPref) cdPref.textContent = c.preference;
      if (cdRestr) cdRestr.textContent = c.restriction;
      if (cdAll) cdAll.textContent = c.allergies || '—';
      // fetch and show recommendations for this client
      const recs = await getRecommendationsForClient(cid);
      showResults(recs, `Recomendaciones para: ${c.name}`);
    } catch (err) {
      console.error('get client', err);
    }
  });
  const newClientBtn = document.getElementById('newClientBtn');
  if (newClientBtn) newClientBtn.addEventListener('click', () => {
    // clear selection to create a new client
    const cs = document.getElementById('clientSelect'); if (cs) cs.value = '';
    // copy current pref/restr into new form and show (guard fields)
    const nn = document.getElementById('newName'); if (nn) nn.value = '';
    const na = document.getElementById('newAllergies'); if (na) na.value = '';
    const np = document.getElementById('newPref'); const nr = document.getElementById('newRestr');
    const prefEl = document.getElementById('pref'); const restrEl = document.getElementById('restr');
    if (np && prefEl) np.value = prefEl.value;
    if (nr && restrEl) nr.value = restrEl.value;
    lockFields(false);
    // clear client details area
    const cdn = document.getElementById('cd_name'); if (cdn) cdn.textContent = 'Nombre: —';
    const cdp = document.getElementById('cd_pref'); if (cdp) cdp.textContent = '—';
    const cdr = document.getElementById('cd_restr'); if (cdr) cdr.textContent = '—';
    const cda = document.getElementById('cd_allergies'); if (cda) cda.textContent = '—';
  });

  const saveBtn = document.getElementById('saveClientBtn');
  if (saveBtn) saveBtn.addEventListener('click', async () => {
    const nameEl = document.getElementById('newName');
    const name = nameEl ? nameEl.value.trim() : '';
    if (!name) return alert('Ingresa un nombre para el cliente');
    const pref = (document.getElementById('newPref')||{}).value || 'Carnívoro';
    const restr = (document.getElementById('newRestr')||{}).value || 'Ninguna';
    const allergies = (document.getElementById('newAllergies')||{}).value.trim() || '';
    try {
      const res = await postJSON('/clients', { name, preference: pref, restriction: restr, allergies });
      await loadClients();
      // select the new client if present
      const cs2 = document.getElementById('clientSelect'); if (cs2) cs2.value = res.id;
      // update details view
      const cdn = document.getElementById('cd_name'); if (cdn) cdn.textContent = `Nombre: ${res.name}`;
      const cdp = document.getElementById('cd_pref'); if (cdp) cdp.textContent = res.preference;
      const cdr = document.getElementById('cd_restr'); if (cdr) cdr.textContent = res.restriction;
      const cda = document.getElementById('cd_allergies'); if (cda) cda.textContent = res.allergies || '—';
      // fetch and show recommendations for the new client
      const recsNew = await getRecommendationsForClient(res.id);
      showResults(recsNew, `Recomendaciones para: ${res.name}`);
      alert('Cliente guardado');
    } catch (err) {
      console.error('save client', err);
      alert('Error guardando cliente');
    }
  });
}

// initial load once DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
  attachHandlers();
  await loadClients();
});
