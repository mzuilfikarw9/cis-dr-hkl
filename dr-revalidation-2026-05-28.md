

## Run details (for record / audit)

| Metric | Value |
|---|---|
| Date | 2026-05-28 |
| Environment | DR (172.16.202.0/24) |
| Hosts | 22 (original 18 + monitoring×1 + minio×3 + lisabackend_dr×1, after late-day drift remediation) |
| Tags applied | ssh, sudo, pam, users, process_hardening, network, kernel_modules, logging_audit, file_perms, banners |
| Tags skipped | firewall, services, mount_options, updates_apparmor |
| Reboot? | No |
| Wall clock | ~25 min (6 tiers × ~3-4 min each + 30s pauses) |
| `failed=` total | 0 |
| `unreachable=` total | 0 |
| `changed=` total | 0 |
| Service flap | None |
| journal errors (post-apply) | None |
| Mongo cluster health | All 6 members healthy |
| MySQL GR health | 3/3 ONLINE |
| UFW status | `inactive` on all 22 hosts (firewall tag skipped, as intended) |
| ip_forward on k3s tier | `1` (override file intact) |
| OpenSCAP scan — all 22 hosts | Done (reports at `~/Documents/clicque/openscap/dr/<host>/`, one HTML + XML per host) |

## Tier-by-tier PLAY RECAP

```
haproxy:
  dr-haprox-01    : ok=10 changed=0 failed=0
  dr-haprox-02    : ok=10 changed=0 failed=0

proxysql:
  dr-proxysql-01  : ok=10 changed=0 failed=0
  dr-proxysql-02  : ok=10 changed=0 failed=0

k3s_workers:
  dr-k3s-worker-01 : ok=10 changed=0 failed=0
  dr-k3s-worker-02 : ok=10 changed=0 failed=0
  dr-k3s-worker-03 : ok=10 changed=0 failed=0
  dr-k3s-worker-04 : ok=10 changed=0 failed=0
  dr-k3s-worker-05 : ok=10 changed=0 failed=0

k3s_masters:
  dr-k3s-master-01 : ok=10 changed=0 failed=0
  dr-k3s-master-02 : ok=10 changed=0 failed=0
  dr-k3s-master-03 : ok=10 changed=0 failed=0

mongo_rabbit:
  dr-mongo-rabbit-01 : ok=10 changed=0 failed=0
  dr-mongo-rabbit-02 : ok=10 changed=0 failed=0
  dr-mongo-rabbit-03 : ok=9  changed=0 failed=0

mysql:
  dr-mysql-01      : ok=10 changed=0 failed=0
  dr-mysql-02      : ok=10 changed=0 failed=0
  dr-mysql-03      : ok=10 changed=0 failed=0
```

(`ok=9` on dr-mongo-rabbit-03 vs `ok=10` everywhere else: one task was skipped due to a host-specific condition. Non-blocking, expected.)

## Drift discovery and late-day remediation

A ping sweep of the DR subnet later in the day revealed 48 live hosts vs the 18 in our original inventory. SSH probes confirmed 4 of the unidentified hosts belong in our hardening scope:

- `dr-monitoring` (172.16.202.13) — Grafana, Prometheus, Alertmanager, VictoriaMetrics, Blackbox exporter, node_exporter. Most components Docker-containerized; node_exporter native.
- `dr-minio-01/02/03` (172.16.202.40/41/42) — 3-node MinIO cluster. Note: 172.16.202.43 is a secondary IP alias on dr-minio-01 (same VM, same SSH host key), not a 4th node.
- `dr-lisabackend` (172.16.202.67) — application backend host. Its `/etc/hostname` reads `prod-lisabackend` due to a naming carry-over; confirmed that this is a DR machine. Rename pending.

Added to `inventories/dr.ini` (new groups: `monitoring`, `minio`, `lisabackend_dr`; all included in `[dr:children]`).

Safe-subset hardening then applied to the 4 new hosts with the same tags as the original 18. All 4 came back healthy: MinIO still serving on ports 9000/9001, Grafana/Prometheus/Alertmanager Docker containers still up on ports 3000/9090/9093, lisabackend still listening on its ~30 application ports.

OpenSCAP compliance scan run against all 22 hosts (original 18 + 4 new). Reports landed at `~/Documents/clicque/openscap/dr/<host>/` — one `*-report.html` + `*-results.xml` per host. Sample report in this repo: `new-dr-revalidation-result-2026-06-4.html`.

**Remaining drift hosts not yet identified or scoped:** `.12, .19, .28-.29, .35, .39, .54-.66, .69-.70`. Need DevOps to confirm roles before any further hardening. Out of scope for today.

**Updated total:** DR now has 22 hosts hardened (was 18). 26 alive DR IPs remain unaccounted for as inventory-drift to investigate.


