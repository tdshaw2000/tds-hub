(async () => {
  const list = document.getElementById('apps');
  const empty = document.getElementById('empty');
  const filter = document.getElementById('filter');

  let apps = [];
  try {
    const res = await fetch('apps.json', { cache: 'no-cache' });
    if (!res.ok) throw new Error(res.status);
    apps = await res.json();
  } catch (err) {
    empty.textContent = 'Could not load apps.json.';
    empty.hidden = false;
    return;
  }

  const el = (tag, cls, text) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text) e.textContent = text;
    return e;
  };

  const cards = apps.map(app => {
    const li = document.createElement('li');
    const a = el('a', 'card');
    a.href = app.url;
    a.append(el('span', 'icon', app.icon || '🔗'));
    const body = el('div');
    body.append(el('p', 'name', app.name));
    if (app.description) body.append(el('p', 'desc', app.description));
    try { body.append(el('p', 'host', new URL(app.url, location.href).host)); } catch {}
    a.append(body);
    li.append(a);
    list.append(li);
    return { li, text: `${app.name} ${app.description || ''}`.toLowerCase() };
  });

  const apply = () => {
    const q = filter.value.trim().toLowerCase();
    let shown = 0;
    for (const c of cards) {
      const match = !q || c.text.includes(q);
      c.li.hidden = !match;
      if (match) shown++;
    }
    empty.textContent = 'No apps match.';
    empty.hidden = shown > 0;
  };
  filter.addEventListener('input', apply);
  apply();
})();
