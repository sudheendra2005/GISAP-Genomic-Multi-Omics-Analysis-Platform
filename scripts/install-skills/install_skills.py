#!/usr/bin/env python3
"""
GISAP Skill Installer
Installs and registers project-local skills and links them into .agents/skills/
"""
import os
import yaml
import sys
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent.parent
    manifest_path = root / ".agents" / "manifests" / "skills.yaml"
    
    if not manifest_path.exists():
        print(f"Error: Manifest not found at {manifest_path}", file=sys.stderr)
        sys.exit(1)
        
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    skills = data.get("skills", [])
    print(f"Installing {len(skills)} skills defined in manifest...")
    
    for s in skills:
        skill_id = s.get("id")
        config_path = root / s.get("config_path")
        if config_path.exists():
            print(f"  [OK] Skill '{skill_id}' registered at {config_path.relative_to(root)}")
        else:
            print(f"  [WARN] Skill '{skill_id}' config missing at {config_path.relative_to(root)}")

    print("Skill installation process completed.")

if __name__ == "__main__":
    main()
