"""
Skills Manager - Orchestrates Agent Skills, UI/UX Pro Max, and Impeccable

Provides programmatic access to external skills for automated code quality,
testing, accessibility auditing, and design system validation.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class SkillInvocation:
    """Represents a single skill invocation."""
    skill_name: str
    command: str
    args: List[str]
    output: Optional[str] = None
    error: Optional[str] = None
    return_code: int = 0


class SkillsManager:
    """Manages invocation of external Claude Code skills."""

    def __init__(self, repo_root: Optional[Path] = None, config_path: Optional[Path] = None):
        """Initialize Skills Manager."""
        self.repo_root = repo_root or Path(__file__).parent.parent.parent
        self.config_path = config_path or self.repo_root / ".claude" / "skills-config.json"
        self.config = self._load_config()
        self.skills_dir = self.repo_root / "skills"

    def _load_config(self) -> Dict[str, Any]:
        """Load skills configuration from JSON."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        return {"enabled_skills": []}

    async def invoke_skill(
        self,
        skill_name: str,
        command: str,
        *args: str,
        timeout: int = 300
    ) -> SkillInvocation:
        """Invoke a skill command asynchronously."""
        full_command = [sys.executable, "-m", skill_name, command, *args]

        try:
            process = await asyncio.create_subprocess_exec(
                *full_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.repo_root),
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            return SkillInvocation(
                skill_name=skill_name,
                command=command,
                args=list(args),
                output=stdout.decode() if stdout else None,
                error=stderr.decode() if stderr else None,
                return_code=process.returncode,
            )

        except asyncio.TimeoutError:
            return SkillInvocation(
                skill_name=skill_name,
                command=command,
                args=list(args),
                error=f"Skill invocation timed out after {timeout}s",
                return_code=1,
            )
        except Exception as e:
            return SkillInvocation(
                skill_name=skill_name,
                command=command,
                args=list(args),
                error=str(e),
                return_code=1,
            )

    async def suggest_tests(self, service_path: str) -> SkillInvocation:
        """Use Agent Skills to suggest tests for a service."""
        return await self.invoke_skill(
            "agent-skills",
            "suggest-tests",
            f"--service={service_path}"
        )

    async def analyze_coverage(self, target_path: str) -> SkillInvocation:
        """Use Agent Skills to analyze test coverage."""
        return await self.invoke_skill(
            "agent-skills",
            "analyze-coverage",
            f"--target={target_path}"
        )

    async def detect_patterns(self, directory: str) -> SkillInvocation:
        """Use Agent Skills to detect anti-patterns."""
        return await self.invoke_skill(
            "agent-skills",
            "detect-patterns",
            f"--directory={directory}"
        )

    async def audit_accessibility(self, frontend_path: str, auto_fix: bool = False) -> SkillInvocation:
        """Use UI/UX Pro Max to audit accessibility (WCAG compliance)."""
        args = [f"--path={frontend_path}"]
        if auto_fix:
            args.append("--fix")
        return await self.invoke_skill(
            "ui-ux-pro-max",
            "audit-accessibility",
            *args
        )

    async def validate_responsive(self, frontend_path: str) -> SkillInvocation:
        """Use UI/UX Pro Max to validate responsive design."""
        return await self.invoke_skill(
            "ui-ux-pro-max",
            "validate-responsive",
            f"--path={frontend_path}"
        )

    async def setup_design_system(self, frontend_path: str) -> SkillInvocation:
        """Use UI/UX Pro Max to setup design system."""
        return await self.invoke_skill(
            "ui-ux-pro-max",
            "setup-design-system",
            f"--path={frontend_path}"
        )

    async def quality_report(self, branch: Optional[str] = None) -> SkillInvocation:
        """Use Impeccable to generate quality report."""
        args = []
        if branch:
            args.append(f"--branch={branch}")
        return await self.invoke_skill(
            "impeccable",
            "quality-report",
            *args
        )

    async def lint(self, service_or_path: Optional[str] = None) -> SkillInvocation:
        """Use Impeccable to lint code."""
        args = []
        if service_or_path:
            if service_or_path.startswith("services/"):
                args.append(f"--service={service_or_path.replace('services/', '')}")
            else:
                args.append(f"--path={service_or_path}")
        return await self.invoke_skill(
            "impeccable",
            "lint",
            *args
        )

    async def format_code(self, path: str) -> SkillInvocation:
        """Use Impeccable to format code."""
        return await self.invoke_skill(
            "impeccable",
            "format",
            f"--path={path}"
        )

    async def run_workflow(self, workflow_name: str) -> List[SkillInvocation]:
        """Run a predefined workflow of skill invocations."""
        workflows = self.config.get("workflow", {})
        if workflow_name not in workflows:
            return [SkillInvocation(
                skill_name="workflow",
                command=workflow_name,
                args=[],
                error=f"Workflow '{workflow_name}' not found",
                return_code=1,
            )]

        steps = workflows[workflow_name]
        results = []

        for step in steps:
            # Parse step format: "skill:command"
            if ":" not in step:
                continue

            skill, command = step.split(":", 1)
            result = await self.invoke_skill(skill, command)
            results.append(result)

            # Stop on first error
            if result.return_code != 0:
                break

        return results

    def get_enabled_skills(self) -> List[str]:
        """Get list of enabled skills."""
        return [skill["name"] for skill in self.config.get("enabled_skills", [])]

    def is_skill_available(self, skill_name: str) -> bool:
        """Check if a skill is installed and available."""
        skill_path = self.skills_dir / skill_name
        return skill_path.exists()


# Sync wrapper for convenience
def invoke_skill_sync(
    skill_name: str,
    command: str,
    *args: str,
    repo_root: Optional[Path] = None
) -> SkillInvocation:
    """Synchronous wrapper for skill invocation."""
    manager = SkillsManager(repo_root=repo_root)
    return asyncio.run(manager.invoke_skill(skill_name, command, *args))


if __name__ == "__main__":
    # Example usage
    import asyncio

    async def main():
        manager = SkillsManager()

        print("Available skills:", manager.get_enabled_skills())

        # Run quality report
        result = await manager.quality_report(branch="main")
        print(f"\nQuality Report Result:")
        print(f"  Return Code: {result.return_code}")
        if result.output:
            print(f"  Output:\n{result.output}")
        if result.error:
            print(f"  Error:\n{result.error}")

    asyncio.run(main())
