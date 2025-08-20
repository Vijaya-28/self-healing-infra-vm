#!/usr/bin/env bash
set -euo pipefail
LOGFILE="/var/log/self-heal.log"
mkdir -p "$(dirname "$LOGFILE")"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Alert received, running Ansible..." | tee -a "$LOGFILE"

# Ensure PROJECT_DIR points to the project root (update if you moved the folder)
export PROJECT_DIR="${PROJECT_DIR:-$HOME/self-healing-infra}"

# Run the playbook
ansible-playbook -i "$PROJECT_DIR/ansible/inventory.ini" "$PROJECT_DIR/ansible/restart_service.yml" | tee -a "$LOGFILE"
