"""Test all imports work."""
import pytest

def test_package_import():
    import vuln_hunter
    assert vuln_hunter.__version__ == "1.0.0"

def test_tools_registry():
    from vuln_hunter.tools.registry import get_registry
    r = get_registry()
    assert r.total_count > 0
    assert r.installed_count >= 0

def test_core():
    from vuln_hunter.core.config import get_settings
    from vuln_hunter.core.llm_provider import LLMProvider, ProviderType
    from vuln_hunter.core.orchestrator import Orchestrator, CampaignState
    s = get_settings()
    assert s.model == "openrouter/owl-alpha"

def test_swarm():
    from vuln_hunter.swarm.blackboard import Blackboard, FindingType
    bb = Blackboard()
    bb.add_finding(FindingType.SUBDOMAIN, {"host": "test.com"}, 0.9)
    assert len(bb.get_findings()) == 1

def test_agents():
    from vuln_hunter.agents.base import BaseAgent
    from vuln_hunter.agents.recon_agent import ReconAgent
    a = BaseAgent()
    assert a is not None

def test_engine_scope():
    from vuln_hunter.engine.scope.scope import ScopeEnforcer
    se = ScopeEnforcer()
    se.add_allowed("*.example.com")
    assert se.is_in_scope("api.example.com")
    assert not se.is_in_scope("evil.com")

def test_engine_cvss():
    from vuln_hunter.engine.findings.cve_db import CVSSCalculator
    score = CVSSCalculator.calculate("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")
    assert score == 9.8

def test_cli():
    from vuln_hunter.cli.main import cli_main, app
    assert app is not None
