# BOINC + Science United

Distributed volunteer computing with adjustable effort profiles.

- **Service**: `boinc-client` (systemd)
- **Data dir**: `/var/lib/boinc-client/`
- **Local prefs**: `/etc/boinc-client/global_prefs_override.xml`

## Setup

```bash
sudo apt install boinc-client
sudo systemctl enable --now boinc-client
```

Install the control scripts:
```bash
sudo cp boinc-effort /usr/local/bin/
sudo cp boinc-science-united-attach /usr/local/bin/
sudo chmod +x /usr/local/bin/boinc-effort /usr/local/bin/boinc-science-united-attach
```

Attach to Science United:
```bash
boinc-science-united-attach
```

## Effort Profiles

| Profile | Description |
|---------|-------------|
| `low` | 30% cores, 60% usage - reduced heat/load |
| `medium` | 60% cores, 85% usage - balanced default |
| `high` | 100% cores, 100% usage - max performance |
| `pause` | Immediately stop all compute |
| `resume` | Resume compute |
| `for <min>` | Temporary pause for N minutes |
| `custom <a> <b> <c>` | Custom: max_ncpus_pct, cpu_usage_limit, suspend_cpu_usage |

## Commands

```bash
boinc-effort status                    # show current status
boinc-effort low|medium|high           # set effort profile
boinc-effort pause                     # pause compute
boinc-effort resume                    # resume compute
boinc-effort for 90                    # pause for 90 minutes
boinc-effort custom 50 75 50           # custom thresholds

sudo boinccmd --get_project_status     # project info
sudo boinccmd --get_task_summary       # task summary
sudo boinccmd --acct_mgr sync          # sync with Science United
```
