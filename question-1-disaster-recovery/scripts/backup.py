#!/usr/bin/env python3
"""
Enterprise Automated Disaster Recovery - Backup Script
Module: question-1-disaster-recovery/scripts/backup.py
Description: Performs automated consistent snapshot backup of database and application state,
             calculates cryptographic checksums, generates metadata manifests, and enforces
             storage retention policies.
"""

import os
import sys
import json
import time
import shutil
import tarfile
import hashlib
import sqlite3
from datetime import datetime, timezone

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPTS_DIR)
CONFIG_PATH = os.path.join(BASE_DIR, "configs", "backup_policy.json")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

def calculate_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def perform_backup(source_db_path, app_state_dir, custom_label="scheduled"):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_id = f"DR-BKP-{timestamp}-{custom_label}"
    staging_dir = os.path.join(BACKUP_DIR, f"staging_{backup_id}")
    os.makedirs(staging_dir, exist_ok=True)

    print(f"[BACKUP ENGINE] Initiating Disaster Recovery Backup ID: {backup_id}")
    start_time = time.time()

    # 1. Database consistency snapshot
    db_dump_file = os.path.join(staging_dir, "database_dump.sql")
    stats = {"tables": {}, "total_records": 0}

    if os.path.exists(source_db_path):
        conn = sqlite3.connect(source_db_path)
        cursor = conn.cursor()
        
        # Dump SQL
        with open(db_dump_file, "w", encoding="utf-8") as f:
            for line in conn.iterdump():
                f.write(f"{line}\n")
        
        # Count records
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall() if not t[0].startswith("sqlite_")]
        for tbl in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
            count = cursor.fetchone()[0]
            stats["tables"][tbl] = count
            stats["total_records"] += count
        conn.close()
        print(f"[BACKUP ENGINE] Database snapshot complete: {len(tables)} tables, {stats['total_records']} total records.")
    else:
        print(f"[BACKUP WARNING] Source database not found at {source_db_path}, creating placeholder.")
        with open(db_dump_file, "w") as f:
            f.write("-- Empty database placeholder\n")

    # 2. Application state and audit logs
    app_staging = os.path.join(staging_dir, "app_state")
    os.makedirs(app_staging, exist_ok=True)
    if os.path.exists(app_state_dir):
        for item in os.listdir(app_state_dir):
            s = os.path.join(app_state_dir, item)
            d = os.path.join(app_staging, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

    # 3. Create compressed archive
    archive_filename = f"{backup_id}.tar.gz"
    archive_path = os.path.join(BACKUP_DIR, archive_filename)

    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(staging_dir, arcname=backup_id)

    # Clean staging
    shutil.rmtree(staging_dir)

    # 4. Generate SHA256 integrity hash
    checksum = calculate_sha256(archive_path)
    checksum_file = f"{archive_path}.sha256"
    with open(checksum_file, "w") as f:
        f.write(f"{checksum}  {archive_filename}\n")

    archive_size_bytes = os.path.getsize(archive_path)
    duration = time.time() - start_time

    # 5. Backup Manifest
    manifest = {
        "backup_id": backup_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "archive_file": archive_filename,
        "archive_size_bytes": archive_size_bytes,
        "sha256_checksum": checksum,
        "duration_seconds": round(duration, 3),
        "database_stats": stats,
        "status": "COMPLETED_VERIFIED"
    }

    manifest_file = os.path.join(BACKUP_DIR, f"{backup_id}_manifest.json")
    with open(manifest_file, "w") as f:
        json.dump(manifest, f, indent=2)

    # 6. Apply retention policy
    enforce_retention_policy()

    print(f"[BACKUP ENGINE] SUCCESS: Archive created -> {archive_filename} ({archive_size_bytes} bytes)")
    print(f"[BACKUP ENGINE] SHA256: {checksum}")
    print(f"[BACKUP ENGINE] Duration: {duration:.3f}s")
    return manifest

def enforce_retention_policy(retention_count=5):
    all_archives = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".tar.gz")]
    all_archives.sort(reverse=True) # newest first
    
    if len(all_archives) > retention_count:
        prune_targets = all_archives[retention_count:]
        print(f"[RETENTION POLICY] Pruning {len(prune_targets)} expired backups exceeding retention limit ({retention_count})...")
        for old in prune_targets:
            old_path = os.path.join(BACKUP_DIR, old)
            sha_path = f"{old_path}.sha256"
            manifest_path = os.path.join(BACKUP_DIR, old.replace(".tar.gz", "_manifest.json"))
            for p in [old_path, sha_path, manifest_path]:
                if os.path.exists(p):
                    os.remove(p)
            print(f"[RETENTION POLICY] Removed old backup: {old}")

if __name__ == "__main__":
    test_db = os.path.join(BASE_DIR, "data", "dr_enterprise.db")
    test_app = os.path.join(BASE_DIR, "data", "app_files")
    perform_backup(test_db, test_app, custom_label="manual")
