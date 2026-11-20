# Question 1: Disaster Recovery Mechanism

## 1. Aim and Objectives
The objective of this practical is to design, implement, and demonstrate an automated Disaster Recovery (DR) mechanism for an enterprise application database and state files.
The practical specifically demonstrates:
- Automated consistent snapshot backup generation.
- Integrity verification using SHA-256 cryptographic hashing.
- Backup storage management and retention policies.
- Controlled disaster simulation (storage corruption / data loss).
- Rapid restoration mechanism and failover.
- Quantitative measurement of **Recovery Time Objective (RTO)** and **Recovery Point Objective (RPO)**.

---

## 2. Tools and Technologies Used
- **Programming Language**: Python 3.13
- **Database Engine**: SQLite 3 (transaction-consistent SQL dump & binary snapshots)
- **Archiving & Compression**: Standard library `tarfile` (gzip compression)
- **Data Integrity**: Standard library `hashlib` (SHA-256 digest calculation and validation)
- **OS Platform**: Windows / Linux compatible

---

## 3. Disaster Recovery Architecture & Strategy

```
  +-------------------------------------------------------------+
  |                   Production Environment                    |
  |  +--------------------+             +--------------------+  |
  |  | SQLite Database    |             | Application State  |  |
  |  | 100 Customers /    |             | Audit Logs & Files |  |
  |  | Financial Records  |             +---------+----------+  |
  |  +---------+----------+                       |             |
  +------------|----------------------------------|-------------+
               |                                  |
               v                                  v
  +-------------------------------------------------------------+
  |              Automated Backup Engine (backup.py)            |
  |  - Transactional consistency lock & SQL dump generation     |
  |  - Gzip Tar compression: DR-BKP-<timestamp>.tar.gz         |
  |  - SHA-256 checksum generation & validation manifest        |
  |  - Retention policy enforcement (maintains latest 5 backups)|
  +------------------------------+------------------------------+
                                 |
                                 v
  +-------------------------------------------------------------+
  |               Catastrophic Event Simulation                 |
  |  - High-severity storage corruption                         |
  |  - Corrupted header causes: "file is not a database"        |
  |  - Application health checks fail                           |
  +------------------------------+------------------------------+
                                 | Trigger Failover / DR Alert
                                 v
  +-------------------------------------------------------------+
  |              Automated Restore Engine (restore.py)          |
  |  - Integrity check verifies SHA-256 checksum of archive     |
  |  - Decompresses archive into isolated staging environment    |
  |  - Reconstructs schema and records from SQL script           |
  |  - Restores application logs and state files                 |
  |  - Validates record counts & restores healthy service       |
  +-------------------------------------------------------------+
```

### Key Metrics Defined:
- **Recovery Time Objective (RTO)**: The maximum acceptable duration of application downtime after a disaster strikes before service is fully restored.
  - *Target SLA*: < 60 seconds
  - *Achieved in Practical*: **0.046 seconds**
- **Recovery Point Objective (RPO)**: The maximum acceptable age of files/records that can be lost from storage when a disaster occurs.
  - *Target SLA*: < 300 seconds
  - *Achieved in Practical*: **1.54 seconds** (representing only the 6 in-flight un-checkpointed live records)

---

## 4. Implementation Files & Directory Structure

```
question-1-disaster-recovery/
├── backups/                    # Storage destination for backup archives & manifests
├── configs/
│   └── backup_policy.json      # Backup frequency and retention configuration
├── data/                       # Production database and application state files
│   ├── enterprise_production.db
│   └── app_files/
├── evidence/                   # Execution logs and JSON verification output
│   ├── dr_execution_evidence.json
│   └── dr_execution_log.md
├── restore/                    # Temporary staging for extraction during recovery
├── scripts/
│   ├── backup.py               # Automated backup generator
│   ├── restore.py              # Automated restore runner
│   └── disaster_simulation.py  # End-to-end failure simulation & measurement
└── README.md                   # This documentation
```

---

## 5. Execution Steps and Commands

### Step 1: Run the Complete Disaster Recovery Simulation
Execute the automated simulation script which creates baseline data, performs backup, injects catastrophic corruption, triggers recovery, and logs results:

```bash
python question-1-disaster-recovery/scripts/disaster_simulation.py
```

### Step 2: Run Manual Backup (Optional standalone execution)
To create a fresh standalone backup:
```bash
python question-1-disaster-recovery/scripts/backup.py
```

### Step 3: Run Manual Restore (Optional standalone execution)
To restore from the latest available backup archive:
```bash
python question-1-disaster-recovery/scripts/restore.py
```

---

## 6. Actual Execution Output & Verification Results

```text
===========================================================================
 LAB 4 - QUESTION 1: DISASTER RECOVERY PRACTICAL SIMULATION
===========================================================================
[SIMULATION SETUP] Populating database with 100 enterprise customer records...
Step 1: Baseline established with 100 customers and 100 transactions.

Step 2: Taking Scheduled Snapshot Backup at Checkpoint T0: 2026-11-20T10:29:41.172504+00:00
[BACKUP ENGINE] Initiating Disaster Recovery Backup ID: DR-BKP-20261120_102941-checkpoint-t0
[BACKUP ENGINE] Database snapshot complete: 2 tables, 200 total records.
[BACKUP ENGINE] SUCCESS: Archive created -> DR-BKP-20261120_102941-checkpoint-t0.tar.gz (3477 bytes)
[BACKUP ENGINE] SHA256: 6f5de5d7909d55674ff5a199b55f3627fb079f90009feb1b4aca5b5c1af0519d
[BACKUP ENGINE] Duration: 0.020s

Step 3: Simulating live online transactions occurring after snapshot T0...
  Inserted 6 real-time transactions after Checkpoint T0.

Step 4: [CRITICAL EVENT] Simulating Hardware Storage Failure & Database Corruption!
  Database binary header corrupted! Verifying application failure...
  Health Check Result: FAILED (Expected) -> Error: file is not a database

Step 5: Alert Triggered! Executing Automated Recovery Runbook...
[RESTORE ENGINE] Starting restoration process from DR-BKP-20261120_102941-checkpoint-t0.tar.gz...
[RESTORE ENGINE] Cryptographic SHA-256 integrity VERIFIED (6f5de5d7909d5567...)
[RESTORE ENGINE] Database reconstructed successfully: 2 tables, 200 records restored.
[RESTORE ENGINE] Application state restored to data/app_files
[RESTORE ENGINE] RESTORATION COMPLETE. Total duration: 0.044s

Step 6: Verifying post-recovery database and application integrity...
  Customers in restored DB: 100 (Baseline: 100)
  Transactions in restored DB: 100 (Baseline: 100)
  Uncommitted delta lost in disaster: 6 transactions

===========================================================================
 DISASTER RECOVERY METRICS EVALUATION
===========================================================================
 Checkpoint Backup Time (T0) : 2026-11-20 10:29:41 UTC
 Disaster Event Time (T_dis) : 2026-11-20 10:29:42 UTC
 Restoration Time (T_rec)    : 2026-11-20 10:29:42 UTC
 Recovery Time Objective (RTO): 0.046 seconds (Target: < 60.0s) -> PASSED
 Recovery Point Objective (RPO): 1.54 seconds (Data window: delta of 6 un-checkpointed records)
===========================================================================
```

---

## 7. Observations and Findings
1. **Zero Data Corruption During Restore**: The SHA-256 integrity check verified that the backup archive was bit-for-bit identical to the generated snapshot prior to decompression.
2. **Sub-second RTO**: Automated recovery script re-instantiated tables and records in **46 milliseconds**, beating the 60-second enterprise SLA by several orders of magnitude.
3. **Controlled RPO**: Because snapshots can be triggered at regular intervals, the RPO was constrained to the delta accrued between snapshot T0 and disaster time (1.54 seconds).
4. **Retention Efficiency**: The built-in policy prunes old snapshots past the configured count (default 5), preventing unbounded disk exhaustion.
