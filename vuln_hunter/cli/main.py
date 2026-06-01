"""VulnHunterAI CLI."""
from __future__ import annotations

import asyncio
import typer
from rich.console import Console
from rich.table import Table
from vuln_hunter.tools.registry import get_registry

console = Console()

BANNER = "[bold cyan]  VulnHunterAI v1.0.0 — Autonomous AI Pentest Framework[/bold cyan]\n"

app = typer.Typer(name="vulnhunter", add_completion=False, no_args_is_help=True)


@app.command()
def scan(
    target: str = typer.Argument(..., help="Target URL, IP, or domain"),
    scope: str = typer.Option("", "-s", "--scope", help="Scope file"),
    intensity: str = typer.Option("normal", "-i", "--intensity", help="safe|normal|aggressive|insane"),
    mode: str = typer.Option("sequential", "-m", "--mode", help="sequential|swarm"),
    max_cost: float = typer.Option(10.0, "--max-cost", help="Max USD"),
):
    """Start a full pentest engagement against a target."""
    print(BANNER)
    console.print(f"[green]Target:[/green] {target}  [cyan]Mode:[/cyan] {mode}  [cyan]Intensity:[/cyan] {intensity}")
    r = get_registry()
    console.print(f"[green]Tools:[/green] {r.installed_count}/{r.total_count} installed")
    try:
        from vuln_hunter.core.orchestrator import Orchestrator
        from vuln_hunter.core.llm_provider import LLMProvider, ProviderType
        provider = LLMProvider(ProviderType.OPENROUTER, max_cost=max_cost)
        orch = Orchestrator(provider=provider, max_cost=max_cost)
        loop = asyncio.new_event_loop()
        state = loop.run_until_complete(orch.run(target))
        console.print(f"[bold green]Done![/bold green]  Cost: ${state.cost:.2f}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@app.command()
def quick(
    target: str = typer.Argument(..., help="Target URL, IP, or domain"),
    intensity: str = typer.Option("normal", "-i", "--intensity"),
):
    """Fast scan with default settings."""
    print(BANNER)
    console.print(f"[green]Quick scan[/green] -> {target} ({intensity})")


@app.command()
def scope_cmd(
    action: str = typer.Argument(..., help="add|remove|validate|list"),
    value: str = typer.Option("", "-v", "--value", help="Value"),
    scope_file: str = typer.Option("scope.txt", "-f", "--file", help="Scope file"),
):
    """Manage engagement scope. Use: vulnhunter scope-cmd add -v *.example.com"""
    from vuln_hunter.engine.scope.scope import ScopeEnforcer
    se = ScopeEnforcer(scope_file)
    if action == "add":
        se.add_allowed(value)
        console.print(f"[green]+[/green] {value}")
    elif action == "remove":
        se.remove(value)
        console.print(f"[yellow]-[/yellow] {value}")
    elif action == "validate":
        ok = se.is_in_scope(value)
        console.print(f"{value} -> {'[green]IN SCOPE[/green]' if ok else '[red]OUT[/red]'}")
    elif action == "list":
        for d in se._allowed_domains:
            console.print(f"  {d}")
    else:
        console.print(f"[red]Unknown:[/red] {action}")


@app.command()
def findings(
    severity: str = typer.Option("", "-s", "--severity", help="Filter by severity"),
    category: str = typer.Option("", "-c", "--category", help="Filter by category"),
    export_fmt: str = typer.Option("", "--export", help="json|csv"),
):
    """List and filter findings."""
    from vuln_hunter.engine.findings.findings_db import FindingsDB
    db = FindingsDB()
    loop = asyncio.new_event_loop()
    results = loop.run_until_complete(db.list_all(severity or None, category or None))
    if export_fmt:
        path = loop.run_until_complete(db.export(export_fmt))
        console.print(f"Exported: [cyan]{path}[/cyan]")
    elif results:
        t = Table(title="Findings")
        t.add_column("ID", style="dim")
        t.add_column("Title", style="bold")
        t.add_column("Severity")
        for f in results[:50]:
            t.add_row(f.id, f.title[:50], f.severity)
        console.print(t)
    else:
        console.print("[yellow]No findings. Run 'vulnhunter scan' first.[/yellow]")


@app.command()
def status():
    """Show tool and system status."""
    r = get_registry()
    t = Table(title="VulnHunterAI Tool Status")
    t.add_column("Category", style="cyan")
    t.add_column("Installed", style="green")
    t.add_column("Total")
    for cat in ["web", "network", "cloud", "osint", "password", "binary", "api", "exploit"]:
        inst = len(r.list_tools(cat, installed_only=True))
        tot = len(r.list_tools(cat))
        t.add_row(cat, str(inst), str(tot))
    t.add_row("[bold]TOTAL[/bold]", f"[bold]{r.installed_count}[/bold]", f"[bold]{r.total_count}[/bold]")
    console.print(t)


@app.command()
def version():
    """Show version."""
    import sys
    print(BANNER.strip())
    console.print(f"Python {sys.version.split()[0]}")


def cli_main():
    app()

if __name__ == "__main__":
    cli_main()
