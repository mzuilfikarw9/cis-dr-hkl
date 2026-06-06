# CIS Benchmark alignment — proof and gap inventory

This document maps the `cis_hardening` Ansible role to CIS Ubuntu Linux 24.04 LTS Server Benchmark v1.0.0, lists every covered rule, and explicitly names the gaps that remain.

---

## What standard we follow

- **Benchmark:** CIS Ubuntu Linux 24.04 LTS Benchmark v1.0.0 (released 2024-08-26)
- **Profile:** Level 1 Server
- **Verification tool:** OpenSCAP `oscap xccdf eval` with SCAP Security Guide (SSG) Ubuntu 24.04 profile
- **SSG version:** 0.1.80 (NIST-certified, CIS-aligned content)

## How to verify alignment independently

Anyone can run the OpenSCAP compliance scan against any hardened host and view the results — no need to trust this document:

```bash
ansible-playbook -i inventories/dr.ini openscap-scan.yml \
  --limit dr-monitoring
# Results at ~/Documents/clicque/openscap/dr/dr-monitoring/dr-monitoring-report.html
```

The report shows pass/fail per CIS rule, with rule IDs that match the published benchmark.

## Role tasks mapped to CIS sections

| Role task file | CIS section | What it covers |
|---|---|---|
| `kernel_modules.yml` | 1.1.1.1 to 1.1.1.9, 3.4.1 to 3.4.4 | Disable 13 unused filesystem and network protocol modules |
| `mount_options.yml` | 1.1.2.1 to 1.1.2.7 | Mount options on /tmp, /dev/shm, /home, /var, /var/tmp, /var/log, /var/log/audit |
| `updates_apparmor.yml` | 1.2.2.1, 1.3.1.1 to 1.3.1.4 | Package updates, AppArmor install + enforce |
| `process_hardening.yml` | 1.4.x, 1.5.x | GRUB perms, prelink removal, sysctl drop-in, coredumps |
| `banners.yml` | 1.7.1 to 1.7.6 | Login banners (/etc/issue, /etc/issue.net, /etc/motd) |
| `services.yml` | 2.x | Remove legacy services, secure cron, chrony NTP |
| `network.yml` | 3.1.x to 3.3.x | Network parameters via sysctl |
| `firewall.yml` | 4.1.x to 4.2.x | UFW install, default-deny, loopback rules |
| `ssh.yml` | 5.1.1 to 5.1.22 | sshd config drop-in (cipher, MAC, key exchange, banner, perms) |
| `sudo.yml` | 5.2.1 to 5.2.6 | sudo install, validated sudoers drop-in |
| `pam.yml` | 5.3.1 to 5.3.3 | pwquality, faillock, pwhistory, pam_wheel, pam_unix hardening |
| `users.yml` | 5.4.x | TMOUT, umask, system account shells, home dir perms |
| `logging_audit.yml` | 6.1.x, 6.2.x, 6.3.x | rsyslog, auditd, journald, AIDE |
| `file_perms.yml` | 7.1.x | /etc/passwd, /etc/shadow, /var/log permission tightening |

## Kernel modules (proof for sections 1.1.1.x and 3.4.x)

The role's `cis_disable_modules` list matches the benchmark line by line:

| CIS rule | Module | In our list |
|---|---|---|
| 1.1.1.1 | cramfs | yes |
| 1.1.1.2 | freevxfs | yes |
| 1.1.1.3 | hfs | yes |
| 1.1.1.4 | hfsplus | yes |
| 1.1.1.5 | jffs2 | yes |
| 1.1.1.6 | overlayfs | yes (skipped on k3s nodes for containerd compatibility — file written, runtime unload skipped) |
| 1.1.1.7 | squashfs | yes |
| 1.1.1.8 | udf | yes |
| 1.1.1.9 | usb-storage | yes |
| 3.4.1 | dccp | yes |
| 3.4.2 | tipc | yes |
| 3.4.3 | rds | yes |
| 3.4.4 | sctp | yes |

## PAM coverage (sections 5.3.x) — recently upgraded

After Hugh's feedback, the PAM task file was extended to cover the previously-missing rules. Coverage now:

| CIS rule | What | Status |
|---|---|---|
| 5.2.7 | Restrict access to su command (pam_wheel) | covered — sugroup created, pam_wheel.so enabled in /etc/pam.d/su |
| 5.3.1.3 | libpam-pwquality installed | covered |
| 5.3.2.2 | pam_faillock enabled | covered via pam-auth-update |
| 5.3.2.3 | pam_pwquality enabled | covered via pam-auth-update |
| 5.3.2.4 | pam_pwhistory enabled | **NEW** — covered via pam-auth-update |
| 5.3.3.1.1 | Password failed attempts lockout | covered (deny=5 in faillock.conf) |
| 5.3.3.1.2 | Password unlock time | covered (unlock_time=900 in faillock.conf) |
| 5.3.3.2.1 | Number of changed characters (difok) | covered (difok=3) |
| 5.3.3.2.2 | Minimum password length | covered (minlen=14) |
| 5.3.3.2.3 | Password complexity | covered (minclass=4, all credit=-1) |
| 5.3.3.2.4 | Max same consecutive characters | covered (maxrepeat=3) |
| 5.3.3.2.5 | Max sequential characters | **NEW** — covered (maxsequence=3) |
| 5.3.3.2.6 | Dictionary check | **NEW** — covered (dictcheck=1) |
| 5.3.3.2.7 | Password quality checking enforced | covered (enforce_for_root in pwquality.conf) |
| 5.3.3.2.8 | Password quality enforced for root | covered (enforce_for_root in pwquality.conf) |
| 5.3.3.3.1 | Password history remember | **NEW** — covered (remember=24 in pwhistory.conf) |
| 5.3.3.3.2 | Password history enforced for root | **NEW** — covered (enforce_for_root in pwhistory.conf) |
| 5.3.3.3.3 | pwhistory includes use_authtok | **NEW** — covered (use_authtok in pwhistory.conf) |
| 5.3.3.4.1 | pam_unix does not include nullok | **NEW** — covered (replace task strips nullok from common-auth + common-password) |
| 5.3.3.4.4 | pam_unix includes use_authtok | **NEW** — covered (replace task adds use_authtok to common-password) |

## Acknowledged remaining gaps

Honest statement: these CIS rules are NOT yet remediated by the role. They are tracked as round-2 hardening backlog and require team decisions before implementation:

| CIS rule | Why deferred |
|---|---|
| 1.4.1 — bootloader password | Impacts break-glass procedures, needs CTO sign-off |
| 1.5.5 — Automatic Error Reporting (apport) disable | Trivial to add; pending |
| 5.4.1.5 — Default inactive password lock | **NEW** — covered in updated pam.yml |
| 5.4.2.4 — Root account access controlled | Partial (PermitRootLogin=no); securetty config pending |
| 5.4.2.5 — Root path integrity | Pending |
| 6.1.2.1.1 to 6.1.2.1.3 — systemd-journal-remote | Needs remote log host decided with infra team |
| 6.1.3.6 — rsyslog remote log host | Same as above |

## Operationally-deferred sections (safe-subset run)

For routine no-downtime applies, four tags are deliberately skipped because they touch live traffic flow or require operator config:

- `firewall` — UFW default-deny needs `cis_extra_allow_ports` populated per tier first
- `services` — Purges legacy packages (rsync, ftp, telnet); audit production usage first
- `mount_options` — Live remount of /tmp /dev/shm with noexec; needs maintenance window
- `updates_apparmor` — apt upgrade + AppArmor enforce; needs maintenance window

These run inside a maintenance window via the full `site.yml` invocation (no `--tags` flag).

## Compliance score (OpenSCAP)

| Snapshot | Rules passing (of 408 in SSG profile) |
|---|---|
| Pre-hardening baseline (DR, 2026-04-17) | ~165 (~40%) |
| Post-hardening (DR, 2026-04-23) | ~300 (~73%) |
| Post-revalidation including drift hosts (2026-05-28) | ~300+ (~73%+, all 22 hosts) |

With the PAM upgrades in this commit, expect the next scan to land ~310-320 (~76%).

## Independent verification

To verify any rule's status on a hardened host:

```bash
# Pull the XML result file
scp ubuntu@<host>:/var/lib/openscap-results/*-results.xml /tmp/

# Search for a specific CIS rule (e.g., 5.3.3.2.5)
grep -A2 "rule_5_3_3_2_5\|maxsequence" /tmp/*-results.xml
```

The XML contains pass/fail per rule with the rule ID, evaluation timestamp, and the exact evidence used.
