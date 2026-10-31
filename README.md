# tds-hub

Home page linking the apps running on my OCI VM, served at <https://tds-hub.duckdns.org>.

## Layout

- `site/` is the static site: `index.html`, `style.css`, `app.js`.
- `site/apps.json` is the app list. Each entry has `name`, `url`, `description`, and an optional emoji `icon`.
- `deploy/` runs it on the VM: an nginx container on the shared edge Caddy network, alias `tds-hub`, port 8000.

## Adding an app

Add an entry to `site/apps.json` and merge to `main`. The Deploy workflow updates the VM's
checkout within a minute; the site is bind-mounted, so there's no restart.

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

## Automatic deploys (one-time setup)

`.github/workflows/deploy.yml` runs on every push to `main`. It SSHes to the VM with a key that
can only run `deploy/deploy-launcher.sh`, which resets the checkout to `origin/main`, runs
`docker compose up -d` and reloads nginx. Same mechanism as puzzle-trainer.

1. On the VM, install the launcher beside the checkout (not inside it):

   ```sh
   cp ~/apps/tds-hub/repo/deploy/deploy-launcher.sh ~/apps/tds-hub/
   chmod +x ~/apps/tds-hub/deploy-launcher.sh
   ~/apps/tds-hub/deploy-launcher.sh      # should end with "tds-hub deployed: <sha>"
   ```

2. Make a deploy key restricted to that launcher:

   ```sh
   ssh-keygen -t ed25519 -f ~/hub-deploy-key -C "tds-hub deploy" -N ""
   RESTRICTION="command=\"$HOME/apps/tds-hub/deploy-launcher.sh\",no-agent-forwarding,no-X11-forwarding,no-port-forwarding,no-pty"
   echo "$RESTRICTION $(cat ~/hub-deploy-key.pub)" >> ~/.ssh/authorized_keys
   cat ~/hub-deploy-key
   ```

3. In GitHub, Settings, Secrets and variables, Actions, add two repository secrets, then
   `rm ~/hub-deploy-key ~/hub-deploy-key.pub` on the VM:

   - `DEPLOY_HOST`: the VM's IP or hostname (same value as the other repos).
   - `DEPLOY_SSH_KEY`: the whole private key printed above, including the BEGIN and END lines.

4. In the Actions tab, run the Deploy workflow (Run workflow) to check it.

If `deploy-launcher.sh` itself changes, repeat step 1's `cp`: it lives outside the checkout
on purpose, so it isn't updated automatically.
