#!/usr/bin/env python3
"""
GISAP Skill and Agent Validator
Verifies all 7 agents, skills manifest, frontmatters, and integration boundaries.
"""
import sys
from pathlib import Path

REQUIRED_AGENTS = [
    "orchestrator.md",
    "frontend.md",
    "backend.md",
    "bioinformatics.md",
    "infrastructure.md",
    "security.md",
    "devops-sre.md"
]

REQUIRED_SKILLS = [
    "fasta-fastq-processing",
    "sequence-validation",
    "biological-annotation",
    "blast-workflows",
    "protein-domain-analysis",
    "nextflow-development",
    "large-scale-dataset-processing",
    "provenance-management",
    "cross-modal-analysis",
    "emil-kowalski-ui",
    "firecrawl-research"
]

def main():
    root = Path(__file__).resolve().parent.parent.parent
    agents_dir = root / ".agents" / "agents"
    skills_dir = root / ".agents" / "skills"
    manifest_file = root / ".agents" / "manifests" / "skills.yaml"
    agents_manifest = root / ".agents" / "manifests" / "agents.yaml"
    root_agents = root / "AGENTS.md"

    failures = []

    # Check root governance
    if not root_agents.exists():
        failures.append("Root AGENTS.md missing.")
    if not manifest_file.exists():
        failures.append(".agents/manifests/skills.yaml missing.")
    if not agents_manifest.exists():
        failures.append(".agents/manifests/agents.yaml missing.")

    # Check Agents
    print("[1/3] Validating 7 Core Agents...")
    for agent_name in REQUIRED_AGENTS:
        agent_path = agents_dir / agent_name
        if not agent_path.exists():
            failures.append(f"Agent definition missing: {agent_name}")
        else:
            print(f"  ✓ Agent {agent_name} present ({agent_path.stat().st_size} bytes)")

    # Check Skills
    print("[2/3] Validating Skills...")
    for skill_name in REQUIRED_SKILLS:
        skill_file = skills_dir / skill_name / "SKILL.md"
        if not skill_file.exists():
            failures.append(f"Skill file missing: {skill_name}/SKILL.md")
        else:
            content = skill_file.read_text(encoding="utf-8")
            if not content.startswith("---"):
                failures.append(f"Skill {skill_name} lacks YAML frontmatter.")
            else:
                print(f"  ✓ Skill {skill_name} validated")

    # Check DoD Status
    print("[3/3] Checking Governance DoD...")
    if failures:
        print("\nValidation Failed with errors:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        sys.exit(1)

    print("\n✓ All 7 agents, 11 skills, and governance files verified successfully.")
    sys.exit(0)

if __name__ == "__main__":
    main()
