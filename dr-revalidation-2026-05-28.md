

## Run details (for record / audit)

| Metric | Value |
|---|---|
| Date | 2026-05-28 |
| Environment | DR (172.16.202.0/24) |
| Hosts | 18 (haproxy×2, proxysql×2, k3s_masters×3, k3s_workers×5, mongo_rabbit×3, mysql×3) |
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
| UFW status | `inactive` on all 18 hosts (firewall tag skipped, as intended) |
| ip_forward on k3s tier | `1` (override file intact) |

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


