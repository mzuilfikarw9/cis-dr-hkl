# How to run the CIS hardening script

A practical walkthrough for anyone (future team members) running this against a fleet.

---

## 1. Prerequisites

On your laptop:

- macOS or Linux with a terminal
- **Ansible 2.14+** installed (`brew install ansible` on Mac, `apt install ansible` on Ubuntu)
- **Python 3.9+** (Ansible needs it)
- SSH key with access to the target fleet
- Vault password for the encrypted `group_vars/dr/vault.yml`

Verify before starting:

```bash
ansible --version          # should show 2.14 or newer
python3 --version          # 3.9+
```

## 2. Clone the repo

```bash
git clone git@github.com:mzuilfikarw9/cis-dr-hkl.git
cd cis-dr-hkl
```

## 3. Configure your environment

### 3a. Drop the vault password file

The repo's encrypted files (`group_vars/dr/vault.yml`) need this to decrypt:

```bash
# Get the vault password
# Then drop it into a file in the repo root:
printf '%s' 'YOUR_VAULT_PASSWORD' > .vault_pass
chmod 600 .vault_pass
```

Don't use `echo` (it adds a trailing newline that breaks ansible-vault). Use `printf '%s'` exactly.

### 3b. Verify your SSH key path

Look at the inventory — the SSH key path is set per-inventory:

```bash
grep "ansible_ssh_private_key_file" inventories/dr.ini
```

If it points somewhere you don't have the key, edit the inventory or override on the command line:

```bash
ansible-playbook ... --private-key=~/path/to/your/key.pem ...
```

### 3c. Test SSH connectivity

Before any playbook run, verify you can reach the fleet:

```bash
ansible -i inventories/dr.ini dr -m ping
```

Every host should return `pong`. If any fail, fix SSH first.

## 4. Always dry-run first (`--check --diff`)

This simulates the run without changing anything on the hosts. Read-only:

```bash
ansible-playbook -i inventories/dr.ini site.yml \
  --check --diff \
  --limit dr-haprox-01 2>&1 | tail -30
```

Single host first. If clean (`failed=0`), expand to a full tier:

```bash
ansible-playbook -i inventories/dr.ini site.yml \
  --check --diff \
  --limit haproxy 2>&1 | tail -30
```

If still clean, expand to the full environment:

```bash
ansible-playbook -i inventories/dr.ini site.yml \
  --check --diff \
  --limit dr 2>&1 | tee /tmp/dryrun.log | tail -30
```

## 5. Live apply (the actual hardening)

### Safe subset (zero traffic disruption, recommended first run)

10 tags that don't restart services or block traffic:

```bash
TIERS=(haproxy proxysql k3s_workers k3s_masters mongo_rabbit mysql)
SAFE_TAGS='ssh,sudo,pam,users,process_hardening,network,kernel_modules,logging_audit,file_perms,banners'

for TIER in "${TIERS[@]}"; do
  echo "=== Tier: $TIER ==="
  ansible-playbook -i inventories/dr.ini site.yml \
    --limit "$TIER" \
    --tags "$SAFE_TAGS" 2>&1 | tail -10
  sleep 30
done
```


## 6. The three rules — never break these

1. **Never remove `/etc/sysctl.d/99-k3s-overrides.conf`** from any k3s node. It's the fix for the Apr 20 ip_forward break.
2. **Always include `localhost` in `--limit`** when running `reboot-ha.yml`. Otherwise the safety-gate play skips and the tripwire fails.
3. **Always pass `-e confirm_reboot=YES`** to `reboot-ha.yml`. There's a confirmation gate at the top.

## 7. Typical workflow summary

For a routine apply (no reboot needed):

```
1. git clone
2. drop .vault_pass
3. ansible -i ... -m ping (verify connectivity)
4. ansible-playbook ... --check --diff --limit one-host  (dry-run)
5. ansible-playbook ... --limit one-tier  (real apply)
6. ansible-playbook openscap-scan.yml  (compliance evidence)
```

For a full hardening + reboot inside a maintenance window:

```
1-2. Same as above
3. preflight-check.yml  (cluster health green?)
4. preflight-ip-forward.yml  (ip_forward gate green?)
5. site.yml  (apply full role per-tier)
6. reboot-ha.yml -e confirm_reboot=YES  (tier-serial reboot)
7. preflight-check.yml  (cluster healthy after reboot?)
8. openscap-scan.yml  (compliance evidence)
```

## 8. Useful one-liners

```bash
# What's listening on each host (for cis_extra_allow_ports planning)
ansible -i inventories/dr.ini dr \
  -m shell -a 'ss -tln | awk "NR>1 {split(\$4,a,\":\"); print a[length(a)]}" | sort -un | xargs' -b

# Any failed services?
ansible -i inventories/dr.ini dr -m shell -a 'systemctl --failed --no-legend' -b

# Verify k3s override file on k3s nodes
ansible -i inventories/dr.ini "k3s_masters:k3s_workers" \
  -m shell -a 'ls /etc/sysctl.d/99-k3s-overrides.conf && cat /proc/sys/net/ipv4/ip_forward' -b

# Show inventory grouping
ansible-inventory -i inventories/dr.ini --graph
```

---
