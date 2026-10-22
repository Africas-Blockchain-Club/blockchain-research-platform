# Backups and restore

Two layers protect the data that cannot be rebuilt: the database (payments, report history, searches), the saved reports (paid AI write-ups) and the AI usage log. Everything else (the built site, PDF cache, network snapshots) the platform rebuilds by itself.

| Layer | Where | How often | Kept |
|---|---|---|---|
| Fly volume snapshots | Fly.io, same region as the machine | Daily, automatic | 14 days |
| Off-site encrypted copy | GitHub Actions artifacts (`.github/workflows/backup.yml`) | Nightly at 02:30 UTC | 30 days |

Each nightly run proves its copy restores before keeping it: it unpacks the archive, runs SQLite's integrity check and confirms the tables are present. A failed run fails the workflow, and GitHub emails the owner.

The copy is encrypted with AES-256 using the `BACKUP_PASSPHRASE` secret. **The passphrase is held only by the owner, in a password manager. Without it the copies cannot be opened**, by anyone, including the owner.

## Secrets the backup needs

| Secret | What it is |
|---|---|
| `FLY_SSH_TOKEN` | `fly tokens create ssh -a blockchain-research-platform`: can only open SSH sessions to this app (and, as Fly documents, join the organisation's private network to do so) |
| `BACKUP_PASSPHRASE` | A long random passphrase; the owner keeps the only other copy |

## Restoring

1. Download the artifact `brp-backup-YYYY-MM-DD` from the latest successful run of the Off-site backup workflow, and unzip it.
2. Decrypt: `gpg --output brp-backup.tar.gz --decrypt brp-backup.tar.gz.gpg` (enter the passphrase).
3. Check it: `python scripts/backup_data.py --verify brp-backup.tar.gz`.
4. Upload it to the machine: `fly ssh sftp shell -a blockchain-research-platform`, then `put brp-backup.tar.gz /tmp/brp-backup.tar.gz`.
5. Unpack it over the live data and restart straight away, so every process reopens the restored database:
   `fly ssh console -a blockchain-research-platform -C "sh -c 'cd /data && tar -xzf /tmp/brp-backup.tar.gz && chown -R app:app local_dev.db reports usage_log.txt && rm /tmp/brp-backup.tar.gz'"`, then `fly machine restart <machine-id> -a blockchain-research-platform` (`fly machine list` shows the id).
6. Run the end-to-end check.

To restore from a Fly snapshot instead: `fly volumes snapshots list <volume-id>`, then `fly volumes create brp_data --snapshot-id <id> -a blockchain-research-platform` and move the machine onto the new volume.
