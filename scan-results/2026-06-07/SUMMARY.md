# CIS L1 Server — DR fleet OpenSCAP scan summary

**Scan date:** 2026-06-07
**Profile:** xccdf_org.ssgproject.content_profile_cis_level1_server
**Datastream:** content/ssg-ubuntu2404-ds.xml (NIST-certified SCAP Security Guide)
**Scanner:** OpenSCAP (NIST SCAP 1.2 validated)

## Per-host pass rate

| Host | Pass | Fail | N/A | Total scored | Score% |
|---|---:|---:|---:|---:|---:|
| dr-k3s-master-03 | 314 | 46 | 48 | 360 | 87.22% |
| dr-k3s-master-02 | 314 | 46 | 48 | 360 | 87.22% |
| dr-k3s-master-01 | 314 | 46 | 48 | 360 | 87.22% |
| dr-k3s-worker-05 | 313 | 47 | 48 | 360 | 86.94% |
| dr-k3s-worker-04 | 313 | 47 | 48 | 360 | 86.94% |
| dr-k3s-worker-03 | 312 | 48 | 48 | 360 | 86.67% |
| dr-k3s-worker-02 | 312 | 48 | 48 | 360 | 86.67% |
| dr-k3s-worker-01 | 312 | 48 | 48 | 360 | 86.67% |
| dr-proxysql-02 | 300 | 49 | 49 | 349 | 85.96% |
| dr-proxysql-01 | 300 | 49 | 49 | 349 | 85.96% |
| dr-mysql-03 | 300 | 49 | 49 | 349 | 85.96% |
| dr-mysql-02 | 300 | 49 | 49 | 349 | 85.96% |
| dr-mysql-01 | 300 | 49 | 49 | 349 | 85.96% |
| dr-mongo-rabbit-02 | 299 | 50 | 49 | 349 | 85.67% |
| dr-mongo-rabbit-01 | 299 | 50 | 49 | 349 | 85.67% |
| dr-haprox-02 | 302 | 56 | 50 | 358 | 84.36% |
| dr-haprox-01 | 302 | 56 | 50 | 358 | 84.36% |
| dr-mongo-rabbit-03 | 296 | 55 | 47 | 351 | 84.33% |
| dr-minio-02 | 291 | 58 | 49 | 349 | 83.38% |
| dr-minio-01 | 291 | 58 | 49 | 349 | 83.38% |
| dr-minio-03 | 289 | 60 | 49 | 349 | 82.81% |
| dr-lisabackend | 293 | 65 | 50 | 358 | 81.84% |
| dr-monitoring | 291 | 67 | 50 | 358 | 81.28% |

## Fleet roll-up

- **Hosts scanned:** 23
- **Hosts ≥80% target:** 23 / 23
- **Score range:** 81.28% – 87.22%
- **Mean score:** 85.32%

## How to verify these numbers independently

Every host's raw OpenSCAP results XML is in `raw/` (or `raw.tar.gz` if compressed). To re-derive any number in the table above:

```bash
# Pass count for one host
grep -c '<result>pass</result>' raw/<hostname>/<hostname>-results.xml

# Fail count for one host
grep -c '<result>fail</result>' raw/<hostname>/<hostname>-results.xml

# Per-rule status table for vendor alignment
scripts/verify-cis-alignment.py \
  --datastream content/ssg-ubuntu2404-ds.xml \
  --results    raw/<hostname>/<hostname>-results.xml \
  --role       roles/cis_hardening \
  --out        /tmp/alignment.csv
```
