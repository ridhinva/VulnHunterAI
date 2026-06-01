"""VulnHunterAI CLI."""
from __future__ import annotations
import asyncio
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from vuln_hunter.tools.registry import get_registry

app = typer.Typer(name="vulnhunter", no_args_is_help=True)
console = Console()

BANNER = "[bold red]\n ██╗   ██╗██╗   ██╗██╗     ███╗   ██╗██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗\n ██║   ██║██║   ██║██║     ████╗  ██║██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗\n ██║   ██║██║   ██║██║     ██╔██╗ ██║███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝\n ╚██╗ ██╔╝██║   ██║██║     ██║╚██╗██║██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗\n  ╚████╔╝ ╚██████╔╝███████╗██║ ╚████║██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║\n   ╚═══╝   ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝\n[/bold red][bold cyan]  Autonomous AI-Powered Pentest Framework v1.0.0[/bold cyan]\n"

@app.callback(invoke_without_command=True)
def main(ctx):
    if ctx.invoked_subcommand is None:
        console.print(BANNER)
        console.print("[dim]Run 'vulnhunter --help' for commands.[/dim]")

@app.command()
def scan(target: str = typer.Option(...,"--target","-t"),
         scope: str = typer.Option("","--scope","-s"),
         intensity: str = typer.Option("normal","--intensity","-i"),
         mode: str = typer.Option("sequential","--mode","-m"),
         max_cost: float = typer.Option(10.0,"--max-cost")):
    """Run a pentest engagement."""
    console.print(BANNER)
    console.print(f"[green]Target:[/green] {target}  [cyan]Mode:[/cyan] {mode}  [cyan]Intensity:[/cyan] {intensity}")
    r = get_registry()
    console.print(f"[green]Tools:[/green] {r.installed_count}/{r.total_count} installed")
    try:
        from vuln_hunter.core.orchestrator import Orchestrator
        from vuln_hunter.core.llm_provider import LLMProvider, ProviderType
        provider = LLMProvider(ProviderType.OPENROUTER, max_cost=max_cost)
        orch = Orchestrator(provider=provider, max_cost=max_cost)
        state = asyncio.get_event_loop().run_until_complete(orch.run(target))
        console.print(f"[bold green]Done![/bold green] Cost: ${state.cost:.2f}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")

@app.command()
def quick(target: str = typer.Option(...,"--target","-t")):
    """Quick scan."""
    console.print(BANNER); console.print(f"[green]Quick scan[/green] -> {target}")

@app.command()
def scope(action: str = typer.Argument(...), value: str = typer.Option("","--value","-v")):
    """Manage scope."""
    from vuln_hunter.engine.scope.scope import ScopeEnforcer
    se = ScopeEnforcer()
    if action == "add": se.add_allowed(value); console.print(f"[green]+[/green] {value}")
    elif action == "remove": se.remove(value); console.print(f"[yellow]-[/yellow] {value}")
    elif action == "validate":
        ok = se.is_in_scope(value)
        console.print(f"{value} -> {'[green]IN SCOPE[/green]' if ok else '[red]OUT[/red]'}")

@app.command()
def findings(severity: str = typer.Option("", "--severity", "-s")):
    """List findings."""
    console.print("[yellow]No active engagement. Run 'vulnhunter scan' first.[/yellow]")

@app.command()
def status():
    """Tool status."""
    r = get_registry()
    t = Table(title="VulnHunterAI")
    t.add_column("Category"); t.add_column("Installed"); t.add_column("Total")
    for cat in r.CATEGORIES if hasattr(r, 'CATEGORIES') else ["web","network","cloud","osint","password","binary","api","exploit"]:
        installed = len(r.list_tools(cat, installed_only=True))
        total = len(r.list_tools(cat))
        t.add_row(cat, str(installed), str(total))
    console.print(t)

@app.command()
def version():
    """Version info."""
    console.print("VulnHunterAI v1.0.0 | Python 3.10+")

def cli_main():
    app()

if __name__ == "__main__":
    cli_main()
