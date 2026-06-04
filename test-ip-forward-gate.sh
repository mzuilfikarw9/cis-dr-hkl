set -euo pipefail

cd "$(dirname "$0")"

INVENTORY="inventories/dr.ini"
PLAYBOOK="preflight-ip-forward.yml"
ENV_NAME="dr"

echo "============================================================"
echo " ip_forward gate — DR validation"
echo "============================================================"

echo
echo "[1/3] Syntax check..."
ansible-playbook --syntax-check -i "$INVENTORY" "$PLAYBOOK" -e target_env="$ENV_NAME"

echo
echo "[2/3] Dry-run (--check, no host changes)..."
ansible-playbook -i "$INVENTORY" "$PLAYBOOK" -e target_env="$ENV_NAME" --check --diff

echo
echo "[3/3] Live run on DR..."
ansible-playbook -i "$INVENTORY" "$PLAYBOOK" -e target_env="$ENV_NAME"

echo
echo "============================================================"
echo " DR validation complete. If all 18 hosts are GREEN above,"
echo " you are clear to point this at prod tonight:"
echo
echo "   ansible-playbook -i inventories/prod.ini \\"
echo "     preflight-ip-forward.yml -e target_env=prod"
echo "============================================================"
