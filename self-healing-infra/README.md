# Self-Healing Infrastructure (VM-based) with Prometheus, Alertmanager & Ansible

This project demonstrates automatic **self-healing** of a service (**NGINX**) running on a **VM** using **Prometheus** + **Blackbox Exporter**, **Alertmanager**, and **Ansible**.

---

## Architecture
1. **Prometheus** scrapes:
   - **Blackbox Exporter** which probes `http://nginx:80/` for HTTP 2xx.
   - **Node Exporter** for CPU metrics.
2. **Alertmanager** triggers a **webhook** when:
   - NGINX is **down** (`probe_success == 0`).
   - CPU is **> 90% for 5m`.
3. **Webhook Server (Flask on host)** receives alerts and runs an **Ansible playbook** to **restart the NGINX service** on your VM.

---

## Prerequisites
- **Ubuntu VM** or similar Linux host
- NGINX installed on VM:
  ```bash
  sudo apt update && sudo apt install -y nginx
  ```
- Docker & Docker Compose (for Prometheus & Alertmanager)
- Python 3 + Flask (`pip install flask`)
- Ansible installed (`pip install ansible` or `sudo apt install ansible`)

---

## Quick Start
```bash
# 1) Extract and cd into the project
unzip self-healing-infra.zip
cd self-healing-infra

# 2) Start monitoring stack + exporters
docker compose up -d

# 3) Start webhook server on the HOST VM
export PROJECT_DIR="$(pwd)"
python3 scripts/webhook_server.py

# 4) On Linux, edit alertmanager/alertmanager.yml:
# Replace http://host.docker.internal:5001/webhook
# With http://<YOUR_VM_IP>:5001/webhook
docker compose restart alertmanager
```

Prometheus UI → http://localhost:9090  
Alertmanager UI → http://localhost:9093  
App (NGINX) → http://localhost:8080

---

## Trigger Self-Healing

### Simulate NGINX Failure
```bash
sudo systemctl stop nginx
```
Within ~30 seconds, Prometheus → Alertmanager → Webhook → Ansible → **NGINX restarts automatically**.

Check status:
```bash
systemctl status nginx
```

### Simulate High CPU Load
```bash
yes > /dev/null &
# Stop it later:
killall yes
```

---

## Demo Evidence
- **Alert firing** in Alertmanager UI (screenshot)
- **Prometheus graph** showing `probe_success=0`
- **/var/log/self-heal.log** output from webhook + Ansible
- **systemctl status nginx** showing recovery

---

## Clean Up
```bash
docker compose down -v
pkill -f webhook_server.py || true
```
