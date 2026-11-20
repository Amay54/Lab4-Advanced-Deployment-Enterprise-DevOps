#!/usr/bin/env python3
"""
Enterprise Automated Disaster Recovery - Restore Script
Module: question-1-disaster-recovery/scripts/restore.py
Description: Validates cryptographic integrity of target backup archive, unpacks database
             and application state, rebuilds database tables, and verifies consistency.
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
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
RESTORE_DIR = os.path.join(BASE_DIR, "restore")
os.makedirs(RESTORE_DIR, exist_ok=True)

def calculate_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def perform_restore(backup_archive_name, target_db_path, target_app_dir):
    start_time = time.time()
    archive_path = os.path.join(BACKUP_DIR, backup_archive_name)
    if not os.path.exists(archive_path):
        raise FileNotFoundError(f"Backup archive not found: {archive_path}")

    # 1. Integrity check via SHA256
    checksum_file = f"{archive_path}.sha256"
    print(f"[RESTORE ENGINE] Starting restoration process from {backup_archive_name}...")
    if os.path.exists(checksum_file):
        with open(checksum_file, "r") as f:
            expected_checksum = f.read().split()[0].strip()
        actual_checksum = calculate_sha256(archive_path)
        if expected_checksum != actual_checksum:
            raise ValueError(f"Integrity Check FAILED! Expected: {expected_checksum}, Actual: {actual_checksum}")
        print(f"[RESTORE ENGINE] Cryptographic SHA-256 integrity VERIFIED ({actual_checksum[:16]}...)")
    else:
        print("[RESTORE ENGINE] Warning: No checksum file found, skipping checksum verification.")

    # 2. Extract archive into temporary unpack directory
    unpack_dir = os.path.join(RESTORE_DIR, f"unpack_{int(time.time())}")
    os.makedirs(unpack_dir, exist_ok=True)
    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(path=unpack_dir)

    # Locate extracted folder
    subdirs = [os.path.join(unpack_dir, d) for d in os.listdir(unpack_dir) if os.path.isdir(os.path.join(unpack_dir, d))]
    extracted_root = subdirs[0] if subdirs else unpack_dir

    # 3. Database restoration
    sql_dump_file = os.path.join(extracted_root, "database_dump.sql")
    restored_stats = {"tables": {}, "total_records": 0}

    if os.path.exists(sql_dump_file):
        # Truncate / recreate target DB file cleanly
        try:
            if os.path.exists(target_db_path):
                os.remove(target_db_path)
        except Exception:
            # If still locked, truncate file
            with open(target_db_path, "wb") as f:
                f.truncate(0)
        os.makedirs(os.path.dirname(target_db_path), exist_ok=True)

        conn = sqlite3.connect(target_db_path)
        cursor = conn.cursor()
        with open(sql_dump_file, "r", encoding="utf-8") as f:
            sql_script = f.read()
        cursor.executescript(sql_script)
        conn.commit()

        # Query stats
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall() if not t[0].startswith("sqlite_")]
        for tbl in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
            count = cursor.fetchone()[0]
            restored_stats["tables"][tbl] = count
            restored_stats["total_records"] += count
        conn.close()
        print(f"[RESTORE ENGINE] Database reconstructed successfully: {len(tables)} tables, {restored_stats['total_records']} records restored.")
    else:
        print("[RESTORE ENGINE] Warning: No SQL dump found in archive.")

    # 4. Restore application assets
    app_source = os.path.join(extracted_root, "app_state")
    if os.path.exists(app_source):
        os.makedirs(target_app_dir, exist_ok=True)
        for item in os.listdir(app_source):
            s = os.path.join(app_source, item)
            d = os.path.join(target_app_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        print(f"[RESTORE ENGINE] Application state restored to {target_app_dir}")

    # Clean unpack
    shutil.rmtree(unpack_dir)

    duration = time.time() - start_time
    print(f"[RESTORE ENGINE] RESTORATION COMPLETE. Total duration: {duration:.3f}s")
    return {
        "status": "RESTORE_SUCCESS",
        "duration_seconds": round(duration, 3),
        "restored_stats": restored_stats,
        "timestamp_utc": datetime.now(timezone.utc).isoformat()
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        archive = sys.argv[1]
    else:
        # Default to latest
        archives = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".tar.gz")]
        archives.sort(reverse=True)
        if not archives:
            print("No backup archives available.")
            sys.exit(1)
        archive = archives[0]

    target_db = os.path.join(BASE_DIR, "data", "dr_enterprise.db")
    target_app = os.path.join(BASE_DIR, "data", "app_files")
    perform_restore(archive, target_db, target_app)
