# tds-hub

Home page linking the apps running on my OCI VM, served at <https://tds-hub.duckdns.org>.

## Layout

- `site/` is the static site: `index.html`, `style.css`, `app.js`.
- `site/apps.json` is the app list. Each entry has `name`, `url`, `description`, and an optional emoji `icon`.
- `deploy/` runs it on the VM: an nginx container on the shared edge Caddy network, alias `tds-hub`, port 8000.

## Adding an app

Add an entry to `site/apps.json`, merge, then on the VM: `git -C ~/apps/tds-hub/repo pull`.
No restart needed; the site is bind-mounted.

## Local preview

```sh
python3 -m http.server -d site 8000
```

## One-time VM setup

Same VM and edge Caddy stack as scramble-challenge, wca-records-analyser, timer-app-pr-tracker
and puzzle-trainer. Run as `ubuntu`.

1. Check `tds-hub.duckdns.org` points at the VM's IP.

2. Clone and start the container:

   ```sh
   mkdir -p ~/apps/tds-hub
   git clone https://github.com/tdshaw2000/tds-hub ~/apps/tds-hub/repo
   cd ~/apps/tds-hub/repo/deploy && docker compose up -d
   ```

   The repo is public, so this needs no GitHub login on the VM, like the other apps.

3. Route the hostname. Merge the scramble-challenge PR that adds `HUB_SITE_ADDRESS` to
   `edge/compose.yaml` and `edge/Caddyfile` (reference block in
   [`deploy/caddy/tds-hub.caddy`](deploy/caddy/tds-hub.caddy)). Then:

   ```sh
   cd ~ && git clone --depth 1 https://github.com/tdshaw2000/scramble-challenge sc-tmp
   cp sc-tmp/edge/compose.yaml sc-tmp/edge/Caddyfile ~/apps/caddy/ && rm -rf sc-tmp
   cd ~/apps/caddy
   echo 'HUB_SITE_ADDRESS=tds-hub.duckdns.org' >> .env
   docker compose up -d       # recreates Caddy: a few seconds of downtime for all apps
   docker compose exec caddy caddy validate --config /etc/caddy/Caddyfile
   curl -sI https://tds-hub.duckdns.org/ | head -1    # HTTP/2 200
   ```

   Caddy gets the Let's Encrypt certificate itself.
