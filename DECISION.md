
---

## 📘 Polished `DECISION.md`

```markdown
# DECISION.md

## 🧠 Architecture Overview

This project uses a blue-green deployment model to ensure zero-downtime releases. Two app containers (`app_blue` and `app_green`) run simultaneously, with NGINX routing traffic to the active pool. Failover is handled automatically using NGINX's `proxy_next_upstream` logic.

## 🔧 Tools Used

- **Docker Compose**: Orchestrates multi-container setup
- **NGINX**: Acts as reverse proxy with failover logic
- **envsubst**: Injects environment variables into NGINX config
- **Healthchecks**: Ensure app containers are responsive

## 🔁 Failover Logic

- `ACTIVE_POOL` determines the primary container
- NGINX routes traffic to `app_${ACTIVE_POOL}`
- If the primary fails, NGINX retries the backup pool (`app_${BACKUP_POOL}`)
- Failover is triggered by `/chaos/start` endpoint

## ⚠️ Challenges Faced

- Initial image pull errors due to unavailable registry images
- Resolved by using public fallback image: `yimikaade/wonderful:devops-stage-two`
- Port conflicts resolved by mapping internal app ports to unique host ports

## ✅ Why This Design Works

- Fully parameterized via `.env` file
- Dynamic NGINX config generation using `entrypoint.sh`
- Clean separation of concerns between proxy and app containers
- Easy to test, extend, and deploy

## 📌 Notes

This setup is ready for production-like testing. Once official HNGx images are available, they can be swapped into `.env` without changing the architecture.