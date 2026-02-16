"""Set up the initial workspace directory structure."""
import os
import json


WORKSPACE_ROOT = os.environ.get("WORKSPACE_ROOT", "/srv/workspace")


def setup():
    """Create initial workspace structure with sample files."""

    # --- Visible content ---

    projects_dir = os.path.join(WORKSPACE_ROOT, "projects")
    os.makedirs(projects_dir, exist_ok=True)

    readme_content = """# DataHub Workspace

Welcome to your DataHub workspace. This directory contains your projects and data files.

## Getting Started

Use the REST API to manage files in this workspace. See the main page for API documentation.

## Structure

- `projects/` — Project directories
  - `analysis/` — Data analysis scripts
  - `datasets/` — Raw and processed datasets
- `shared/` — Shared team resources
"""
    with open(os.path.join(WORKSPACE_ROOT, "README.md"), "w") as f:
        f.write(readme_content)

    # Analysis project
    analysis_dir = os.path.join(projects_dir, "analysis")
    os.makedirs(analysis_dir, exist_ok=True)

    with open(os.path.join(analysis_dir, "pipeline.py"), "w") as f:
        f.write('''"""Data processing pipeline for quarterly reports."""
import csv
import json
from pathlib import Path


def load_dataset(path):
    """Load a CSV dataset from the given path."""
    records = []
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return records


def aggregate(records, group_by, metric):
    """Aggregate records by a grouping column."""
    groups = {}
    for rec in records:
        key = rec.get(group_by, "unknown")
        val = float(rec.get(metric, 0))
        groups.setdefault(key, []).append(val)
    return {k: sum(v) / len(v) for k, v in groups.items()}


def export_report(data, output_path):
    """Export aggregated report as JSON."""
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Report written to {output_path}")


if __name__ == "__main__":
    dataset = load_dataset("../../datasets/quarterly_sales.csv")
    result = aggregate(dataset, "region", "revenue")
    export_report(result, "report_output.json")
''')

    with open(os.path.join(analysis_dir, "config.json"), "w") as f:
        json.dump({
            "database": "postgresql://readonly:readonly@db.internal:5432/analytics",
            "output_dir": "./reports",
            "log_level": "INFO",
            "max_workers": 4,
        }, f, indent=2)

    # Datasets
    datasets_dir = os.path.join(projects_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)

    with open(os.path.join(datasets_dir, "quarterly_sales.csv"), "w") as f:
        f.write("region,quarter,revenue,units\n")
        f.write("north,Q1,245000,1200\n")
        f.write("south,Q1,198000,980\n")
        f.write("east,Q1,312000,1550\n")
        f.write("west,Q1,276000,1340\n")
        f.write("north,Q2,267000,1310\n")
        f.write("south,Q2,215000,1050\n")
        f.write("east,Q2,334000,1620\n")
        f.write("west,Q2,289000,1400\n")

    # Shared team resources
    shared_dir = os.path.join(WORKSPACE_ROOT, "shared")
    os.makedirs(shared_dir, exist_ok=True)

    with open(os.path.join(shared_dir, "team_access.md"), "w") as f:
        f.write("""# Team Access

## Workspace Accounts

| Username  | Role    | Notes                       |
|-----------|---------|-----------------------------|
| admin     | admin   | Full workspace management   |
| analyst   | viewer  | Read-only workspace access  |

Default password for the analyst account: `workspace`

For admin access, contact the workspace administrator.
""")

    with open(os.path.join(shared_dir, "onboarding.md"), "w") as f:
        f.write("""# Onboarding Guide

## Quick Start

1. Log in via the API: `POST /api/session` with your credentials
2. Use the returned token for all subsequent API calls
3. Browse workspace files via `GET /api/workspace`

## Important Notes

- Hidden files and directories (starting with `.`) are not shown in directory listings
- The workspace root is `/srv/workspace`
- Check `/api/status` for server runtime info
""")

    # Shared notes
    with open(os.path.join(WORKSPACE_ROOT, "CHANGELOG.txt"), "w") as f:
        f.write("2024-01-10: Initial workspace setup\n")
        f.write("2024-02-15: Added analyst read-only account\n")
        f.write("2024-03-01: Migrated to new server infrastructure\n")
        f.write("2024-03-15: Updated hidden file handling for security\n")
        f.write("2024-04-01: Added Q2 dataset for analysis team\n")

    # --- Hidden content (only accessible via the vulnerability) ---

    # Hidden config directory with sensitive credentials
    config_dir = os.path.join(WORKSPACE_ROOT, ".config")
    os.makedirs(config_dir, exist_ok=True)

    flag = os.environ.get("FLAG", "FLAG{placeholder}")
    with open(os.path.join(config_dir, "credentials.json"), "w") as f:
        json.dump({
            "api_key": flag,
            "service_account": "workspace-admin@datahub.internal",
            "cluster_endpoint": "https://k8s.datahub.internal:6443",
            "ca_cert": "/etc/ssl/certs/datahub-ca.pem",
        }, f, indent=2)

    with open(os.path.join(config_dir, "settings.json"), "w") as f:
        json.dump({
            "theme": "dark",
            "auto_save": True,
            "auto_save_interval": 120,
            "show_hidden": False,
            "default_kernel": "python3",
        }, f, indent=2)

    # Hidden runtime directory
    runtime_dir = os.path.join(WORKSPACE_ROOT, ".runtime")
    os.makedirs(runtime_dir, exist_ok=True)

    print(f"Workspace initialized at {WORKSPACE_ROOT}")


if __name__ == "__main__":
    setup()
