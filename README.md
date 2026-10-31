# tds-hub

Home page linking the apps running on my OCI VM, served at <https://tds-hub.duckdns.org>.

## Layout

- `site/` is the static site: `index.html`, `style.css`, `app.js`.
- `site/apps.json` is the app list. Each entry has `name`, `url`, `description`, and an optional emoji `icon`.

## Adding an app

Add an entry to `site/apps.json` and pull on the VM. No build step.

## Local preview

```sh
python3 -m http.server -d site 8000
```
