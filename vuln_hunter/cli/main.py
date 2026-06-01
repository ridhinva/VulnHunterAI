"""VulnHunterAI CLI."""
from __future__ import annotations

import asyncio
import sys
import typer
from rich.console import Console
from rich.table import Table
from vuln_hunter.tools.registry import get_registry

console = Console()
app = typer.Typer(name="vulnhunter", add_completion=False)


@app.command()
def scan(
    target: str = typer.Argument(..., metavar="TARGET", help="Target URL, IP, or domain"),
    scope: str = typer.Option("", "-s", "--scope", help="Scope file"),
    intensity: str = typer.Option("normal", "-i", "--intensity", help="safe|normal|aggressive|insane"),
    mode: str = typer.Option("sequential", "-m", "--mode", help="sequential|swarm"),
    max_cost: float = typer.Option(10.0, "--max-cost", help="Max USD"),
):
    """Start a full pentest engagement against a target."""
    console.print("[bold cyan]VulnHunterAI v1.0.0[/bold cyan]")
    console.print(f"[green]Target:[/green] {target}  [cyan]Mode:[/cyan] {mode}  [cyan]Intensity:[/cyan] {intensity}")
    r = get_registry()
    console.print(f"[green]Tools:[/green] {r.installed_count}/{r.total_count} installed")
    try:
        from vuln_hunter.core.orchestrator import Orchestrator
        from vuln_hunter.core.llm_provider import LLMProvider, ProviderType
        provider = LLMProvider(ProviderType.OPENROUTER)
        orch = Orchestrator(provider=provider, max_cost=max_cost)
        loop = asyncio.new_event_loop()
        state = loop.run_until_complete(orch.run(target))
        console.print(f"[bold green]Done![/bold green]  Cost: ${state.cost:.2f}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@app.command()
def quick(
    target: str = typer.Argument(..., metavar="TARGET", help="Target URL, IP, or domain"),
    intensity: str = typer.Option("normal", "-i", "--intensity"),
):
    """Fast scan with default settings."""
    console.print("[bold cyan]VulnHunterAI v1.0.0[/bold cyan]")
    console.print(f"[green]Quick scan[/green] -> {target} ({intensity})")


@app.command()
def scope(
    action: str = typer.Argument(..., metavar="ACTION", help="add|remove|validate|list"),
    value: str = typer.Option("", "-v", "--value", help="Value"),
    scope_file: str = typer.Option("scope.txt", "-f", "--file", help="Scope file path"),
):
    """Manage engagement scope. Create a scope file with domains (one per line)."""
    from vuln_hunter.engine.scope.scope import ScopeEnforcer
    se = ScopeEnforcer(scope_file)
    if action == "add":
        se.add_allowed(value)
        # Persist to scope file
        try:
            with open(scope_file, "a") as f:
                f.write(value + "\n")
            console.print(f"[green]+[/green] {value} (appended to {scope_file})")
        except Exception:
            console.print(f"[green]+[/green] {value} (memory only)")
    elif action == "remove":
        se.remove(value)
        console.print(f"[yellow]-[/yellow] {value}")
    elif action == "validate":
        ok = se.is_in_scope(value)
        console.print(f"{value} -> {'[green]IN SCOPE[/green]' if ok else '[red]OUT[/red]'}")
    elif action == "list":
        domains = se._allowed_domains
        if domains:
            for d in domains:
                console.print(f"  {d}")
        else:
            console.print(f"[dim]No entries. Create {scope_file} or use 'scope add'[/dim]")
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
def gravatar(
    email: str = typer.Argument(..., help="Email to look up"),
):
    """Look up a Gravatar profile by email (no API key needed)."""
    with console.status(f"[cyan]Looking up Gravatar for {email}...[/cyan]"):
        from vuln_hunter.integrations.gravatar import lookup_gravatar
        result = lookup_gravatar(email)

    if result.get("found"):
        t = Table(title=f"Gravatar: {email}")
        t.add_column("Field", style="cyan")
        t.add_column("Value", style="green")
        t.add_row("Display Name", result.get("display_name", ""))
        t.add_row("Profile", result.get("profile_url", ""))
        t.add_row("Photo", result.get("thumbnail_url", ""))
        if result.get("accounts"):
            for a in result["accounts"]:
                t.add_row(f"  {a['service']}", a.get("url", ""))
        console.print(t)
    elif result.get("found") is False:
        console.print(f"[yellow]No Gravatar found for {email}[/yellow]")
    else:
        console.print(f"[red]Error:[/red] {result.get('error', 'unknown')}")


@app.command()
def version():
    """Show version."""
    console.print("[bold cyan]VulnHunterAI v1.0.0[/bold cyan]")
    console.print(f"Python {sys.version.split()[0]}")


def cli_main():
    app()

if __name__ == "__main__":
    cli_main()
