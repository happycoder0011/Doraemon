#!/usr/bin/env python3
"""
validate_config.py — WebForge project.config.yaml validator.

Emits plain-language errors (per ARCHITECTURE.md §3.5). Usage:

    python3 scripts/validate_config.py projects/<slug>/project.config.yaml

Exit codes:
    0 — config is valid
    1 — one or more blocking errors
    2 — config file missing or unreadable
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write(
        "PyYAML is required. Install with: pip install pyyaml\n"
    )
    sys.exit(2)

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")


def load(path: Path) -> dict:
    try:
        with path.open() as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        sys.stderr.write(f"Could not find config at {path}.\n")
        sys.exit(2)
    except yaml.YAMLError as e:
        sys.stderr.write(f"Could not parse YAML in {path}: {e}\n")
        sys.exit(2)
    if not isinstance(data, dict):
        sys.stderr.write(f"{path} did not load as a mapping (got {type(data).__name__}).\n")
        sys.exit(2)
    return data


def validate(cfg: dict) -> list[str]:
    errors: list[str] = []

    # --- required top-level keys ---
    for key in ("project", "deliverables", "infrastructure", "operator", "budget"):
        if key not in cfg:
            errors.append(f"Missing required section `{key}`.")

    # --- project ---
    proj = cfg.get("project") or {}
    if not proj.get("name"):
        errors.append("Missing `project.name`.")
    slug = proj.get("slug")
    if not slug:
        errors.append("Missing `project.slug` (e.g. \"acme-plumbing\").")
    elif not SLUG_RE.match(slug):
        errors.append(
            f"`project.slug` \"{slug}\" must be lowercase letters, digits, and hyphens, "
            "starting and ending with a letter or digit."
        )
    ptype = proj.get("type")
    if ptype and ptype not in {
        "local-services", "saas", "ecommerce", "info-site", "personal-brand", "agency"
    }:
        errors.append(
            f"`project.type` \"{ptype}\" is not one of: "
            "local-services, saas, ecommerce, info-site, personal-brand, agency."
        )

    # --- infrastructure / cms consistency ---
    infra = cfg.get("infrastructure") or {}
    deploy = infra.get("deployment_target")
    web = (cfg.get("deliverables") or {}).get("website") or {}
    cms = web.get("cms")

    if cms == "wordpress" and deploy and deploy not in {"wp-hosting", "aws"}:
        errors.append(
            f"You picked WordPress but `{deploy}` for hosting. "
            "WordPress sites need a WordPress-capable host (wp-hosting or aws). "
            "Want me to switch hosting?"
        )
    if cms == "shopify" and deploy and deploy != "shopify":
        errors.append(
            f"You picked Shopify CMS but `{deploy}` for deployment. "
            "Shopify handles its own hosting — switch `infrastructure.deployment_target` to `shopify`."
        )
    if cms == "webflow" and deploy and deploy != "webflow":
        errors.append(
            f"You picked Webflow CMS but `{deploy}` for deployment. "
            "Webflow hosts itself — switch `infrastructure.deployment_target` to `webflow`."
        )
    if deploy == "shopify" and cms and cms != "shopify":
        errors.append(
            f"You picked Shopify deployment but `{cms}` as CMS. "
            "On Shopify, the CMS IS Shopify."
        )
    if deploy == "webflow" and cms and cms != "webflow":
        errors.append(
            f"You picked Webflow deployment but `{cms}` as CMS. "
            "On Webflow, the CMS IS Webflow."
        )

    # --- local-services + local_seo hint ---
    seo = (cfg.get("deliverables") or {}).get("seo") or {}
    if ptype == "local-services" and seo.get("local_seo") is False:
        errors.append(
            "Project type is `local-services` but `local_seo` is `false`. "
            "Local-services clients typically need local SEO. "
            "Set `deliverables.seo.local_seo: true` or confirm this is intentional."
        )

    # --- ongoing SEO ↔ monthly reporting ---
    ongoing = seo.get("ongoing_months", 0) or 0
    analytics = (cfg.get("deliverables") or {}).get("analytics") or {}
    monthly = analytics.get("monthly_reporting")
    if ongoing > 0 and monthly is False:
        errors.append(
            f"You've commissioned {ongoing} months of ongoing SEO but disabled monthly reporting. "
            "How will the client see progress? Enable `deliverables.analytics.monthly_reporting: true`."
        )

    # --- operator + approvals sanity ---
    operator = cfg.get("operator") or {}
    expertise = operator.get("expertise")
    approvals = cfg.get("approvals") or {}
    mode = approvals.get("mode")
    if expertise == "non-technical" and mode == "technical-gated":
        errors.append(
            "Operator is `non-technical` but `approvals.mode` is `technical-gated`. "
            "A non-technical operator will be buried in implementation approvals. "
            "Switch to `judgment-gated` (recommended) or `minimal`."
        )

    # --- budget sanity ---
    budget = cfg.get("budget") or {}
    per_run = budget.get("per_run_cap_usd")
    total = budget.get("total_project_usd")
    if per_run is None:
        errors.append("Missing `budget.per_run_cap_usd`.")
    if per_run is not None and total is not None and per_run > total:
        errors.append(
            f"`budget.per_run_cap_usd` (${per_run}) is larger than "
            f"`budget.total_project_usd` (${total}). A single run can't cost more than the whole project."
        )

    return errors


def main() -> int:
    p = argparse.ArgumentParser(description="Validate a WebForge project.config.yaml")
    p.add_argument("config", type=Path, help="Path to project.config.yaml")
    args = p.parse_args()

    cfg = load(args.config)
    errors = validate(cfg)
    if errors:
        sys.stderr.write(f"\n{len(errors)} issue(s) in {args.config}:\n\n")
        for i, e in enumerate(errors, 1):
            sys.stderr.write(f"  {i}. {e}\n")
        sys.stderr.write("\nFix these and re-run.\n")
        return 1
    print(f"OK — {args.config} is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())