# CIS L1 Server — DR fleet OpenSCAP scan summary

**Scan date:** 2026-06-07
**Profile:** xccdf_org.ssgproject.content_profile_cis_level1_server
**Datastream:** content/ssg-ubuntu2404-ds.xml (NIST-certified SCAP Security Guide)
**Scanner:** OpenSCAP (NIST SCAP 1.2 validated)
**Score column:** OpenSCAP XCCDF default weighted scoring (`urn:xccdf:scoring:default`) — matches each per-host OpenSCAP HTML report.

## Per-host weighted score

| Host | Pass | Fail | N/A | Score (weighted %) |
|---|---:|---:|---:|---:|
| dr-k3s-master-02 | 314 | 46 | 48 | 82.19% |
| dr-k3s-master-03 | 314 | 46 | 48 | 82.19% |
| dr-k3s-worker-04 | 313 | 47 | 48 | 81.90% |
| dr-k3s-worker-05 | 313 | 47 | 48 | 81.90% |
| dr-k3s-master-01 | 312 | 48 | 48 | 81.70% |
| dr-k3s-worker-01 | 312 | 48 | 48 | 81.60% |
| dr-k3s-worker-02 | 312 | 48 | 48 | 81.60% |
| dr-k3s-worker-03 | 312 | 48 | 48 | 81.60% |
| dr-mysql-01 | 300 | 49 | 49 | 76.78% |
| dr-mysql-02 | 300 | 49 | 49 | 76.78% |
| dr-mysql-03 | 300 | 49 | 49 | 76.78% |
| dr-proxysql-01 | 300 | 49 | 49 | 76.78% |
| dr-proxysql-02 | 300 | 49 | 49 | 76.78% |
| dr-mongo-rabbit-01 | 299 | 50 | 49 | 76.78% |
| dr-mongo-rabbit-02 | 299 | 50 | 49 | 76.78% |
| dr-mongo-rabbit-03 | 296 | 55 | 47 | 76.34% |
| dr-haprox-01 | 302 | 56 | 50 | 75.40% |
| dr-haprox-02 | 302 | 56 | 50 | 75.40% |
| dr-minio-01 | 291 | 58 | 49 | 73.47% |
| dr-minio-02 | 291 | 58 | 49 | 73.47% |
| dr-minio-03 | 289 | 60 | 49 | 72.87% |
| dr-lisabackend | 293 | 65 | 50 | 72.08% |
| dr-monitoring | 291 | 67 | 50 | 71.49% |

## Fleet roll-up

- **Hosts scanned:** 23
- **Hosts >=80% target (weighted score):** 8 / 23
- **Score range:** 71.49% - 82.19%
- **Mean score:** 77.51%

## Note on the customer-facing metric

The weighted score above is the auditor-facing number from OpenSCAP. Against the customer's list of 47 items (Hugh's items 38-85), 43 are closed and verifiable in the main config files on every host. The 4 remaining are UFW firewall rules (4.2.3, 4.2.4, 4.2.6, 4.2.7), deferred to a maintenance window because of k3s networking risk.
