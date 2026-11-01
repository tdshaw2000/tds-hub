// Skins: each lives in themes/<id>/theme.css and is listed in skins.json (default + menu
// order). The gear menu saves the choice in this browser (localStorage) and swaps the
// stylesheet in place. No styling is set here. Without this script the default skin shows.
(function () {
  "use strict";

  const KEY = "hub_skin";
  const stylesheet = document.querySelector('link[rel="stylesheet"]');
  const themeCss = (id) => `themes/${id}/theme.css`;
  const safe = (id) => typeof id === "string" && /^[a-z0-9_-]+$/.test(id);

  const read = () => { try { return localStorage.getItem(KEY); } catch { return null; } };
  const write = (id) => { try { localStorage.setItem(KEY, id); } catch {} };

  // Apply a saved choice before the page paints, so there is no flash of the default.
  // It is checked against skins.json below.
  const saved = read();
  if (stylesheet && safe(saved)) stylesheet.setAttribute("href", themeCss(saved));

  async function init() {
    const header = document.querySelector("header");
    if (!stylesheet || !header) return;
    let config;
    try {
      const res = await fetch("skins.json", { cache: "no-cache" });
      if (!res.ok) throw new Error(res.status);
      config = await res.json();
    } catch {
      return;
    }
    const ids = config.skins.map((s) => s.id);
    let current = ids.includes(saved) ? saved : config.default;
    stylesheet.setAttribute("href", themeCss(current));

    const picker = document.createElement("details");
    picker.className = "skin-picker";
    const toggle = document.createElement("summary");
    toggle.className = "skin-picker-toggle";
    toggle.setAttribute("aria-label", "Change skin");
    toggle.textContent = "⚙";
    const menu = document.createElement("div");
    menu.className = "skin-menu";
    const title = document.createElement("p");
    title.className = "skin-menu-title";
    title.textContent = "Skin";
    menu.append(title);

    const options = config.skins.map((skin) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "skin-option";
      button.textContent = skin.label;
      button.addEventListener("click", () => {
        current = skin.id;
        write(current);
        stylesheet.setAttribute("href", themeCss(current));
        mark();
        picker.open = false;
      });
      menu.append(button);
      return [skin.id, button];
    });
    const mark = () => {
      for (const [id, button] of options) {
        if (id === current) button.setAttribute("aria-current", "true");
        else button.removeAttribute("aria-current");
      }
    };
    mark();
    picker.append(toggle, menu);
    header.append(picker);

    // A tap anywhere outside the open menu closes it.
    document.addEventListener("click", (event) => {
      if (picker.open && !picker.contains(event.target)) picker.open = false;
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
