"""CLI interface for SWARA using Click and Rich."""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from swara.models import Laya


console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="swara")
def cli() -> None:
    """SWARA - Indian Classical Music Composer.

    Compose and synthesize Indian classical music with tabla, sitar,
    veena, and tanpura.
    """


@cli.command()
def list_ragas() -> None:
    """List all available ragas with details."""
    from swara.composition.raga_engine import RagaCompositionEngine, RAGA_REGISTRY

    table = Table(title="Available Ragas", border_style="cyan")
    table.add_column("Name", style="bold cyan")
    table.add_column("Thaat")
    table.add_column("Vadi")
    table.add_column("Samvadi")
    table.add_column("Time of Day")
    table.add_column("Rasa")

    for key in sorted(RAGA_REGISTRY.keys()):
        raga = RAGA_REGISTRY[key]
        table.add_row(
            raga.name,
            raga.thaat or "-",
            raga.vadi.value if raga.vadi else "-",
            raga.samvadi.value if raga.samvadi else "-",
            raga.time_of_day or "-",
            raga.rasa or "-",
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(RAGA_REGISTRY)} ragas[/dim]")


@cli.command()
def list_taals() -> None:
    """List all available taals with their thekas."""
    from swara.instruments.tabla import TAAL_REGISTRY

    table = Table(title="Available Taals", border_style="green")
    table.add_column("Name", style="bold green")
    table.add_column("Matras", justify="right")
    table.add_column("Vibhag")
    table.add_column("Theka")

    for key in sorted(TAAL_REGISTRY.keys()):
        taal = TAAL_REGISTRY[key]
        theka_str = " ".join(b.value for b in taal.theka[:12])
        if len(taal.theka) > 12:
            theka_str += " ..."
        table.add_row(
            taal.name,
            str(taal.matra),
            " | ".join(str(v) for v in taal.vibhag),
            theka_str,
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(TAAL_REGISTRY)} taals[/dim]")


@cli.command()
@click.option("--raga", required=True, help="Name of the raga")
@click.option("--taal", default="teentaal", help="Name of the taal")
@click.option(
    "--laya",
    type=click.Choice(["vilambit", "madhya", "drut"]),
    default="madhya",
    help="Tempo (vilambit/madhya/drut)",
)
@click.option("--duration", default=60.0, type=float, help="Duration in seconds")
@click.option(
    "--sections",
    default="alap,jor,jhala,gat",
    help="Comma-separated list of sections",
)
@click.option("--seed", default=None, type=int, help="Random seed for reproducibility")
def compose(
    raga: str,
    taal: str,
    laya: str,
    duration: float,
    sections: str,
    seed: int | None,
) -> None:
    """Compose a piece in the given raga and taal."""
    from swara.composition.raga_engine import RagaCompositionEngine
    from swara.report import print_composition_report

    section_list = [s.strip() for s in sections.split(",")]

    try:
        engine = RagaCompositionEngine(seed=seed)
        composition = engine.compose(
            raga_name=raga,
            sections=section_list,
            duration=duration,
            laya=Laya(laya),
        )
        print_composition_report(composition, console)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@cli.command()
@click.option("--raga", required=True, help="Name of the raga")
@click.option("--taal", default="teentaal", help="Name of the taal")
def report(raga: str, taal: str) -> None:
    """Generate a detailed report for a raga and taal combination."""
    from swara.report import format_raga_card
    from swara.instruments.tabla import TAAL_REGISTRY

    try:
        format_raga_card(raga, console)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    # Show taal info
    taal_key = taal.lower().replace(" ", "")
    if taal_key in TAAL_REGISTRY:
        taal_def = TAAL_REGISTRY[taal_key]
        theka_str = " ".join(b.value for b in taal_def.theka)
        console.print(f"\n[bold green]Taal: {taal_def.name}[/bold green] ({taal_def.matra} matras)")
        console.print(f"Theka: {theka_str}")
        console.print(f"Vibhag: {' | '.join(str(v) for v in taal_def.vibhag)}")
    else:
        console.print(f"[yellow]Taal '{taal}' not found.[/yellow]")


@cli.command()
@click.option("--raga", required=True, help="Name of the raga")
@click.option(
    "--laya",
    type=click.Choice(["vilambit", "madhya", "drut"]),
    default="madhya",
)
@click.option("--duration", default=30.0, type=float)
@click.option(
    "--style",
    type=click.Choice(["sawal_jawab", "parallel", "layakari"]),
    default="sawal_jawab",
)
@click.option("--instrument-a", default="Sitar", help="First instrument name")
@click.option("--instrument-b", default="Veena", help="Second instrument name")
def jugalbandi(
    raga: str,
    laya: str,
    duration: float,
    style: str,
    instrument_a: str,
    instrument_b: str,
) -> None:
    """Generate a jugalbandi (duet) composition."""
    from swara.composition.jugalbandi import JugalbandiComposer
    from swara.report import print_jugalbandi_report

    try:
        composer = JugalbandiComposer()
        comp = composer.compose_duet(
            raga_name=raga,
            duration=duration,
            laya=Laya(laya),
            interaction_style=style,
        )
        print_jugalbandi_report(comp, instrument_a, instrument_b, console)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@cli.command()
@click.option("--raga", required=True, help="Name of the raga")
def raga_info(raga: str) -> None:
    """Show detailed information about a raga."""
    from swara.report import format_raga_card

    try:
        format_raga_card(raga, console)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@cli.command()
def list_bols() -> None:
    """List all available tabla bol patterns."""
    from swara.instruments.tabla import BOL_PATTERNS

    table = Table(title="Tabla Bol Patterns", border_style="yellow")
    table.add_column("Name", style="bold")
    table.add_column("Matras", justify="right")
    table.add_column("Bols")
    table.add_column("Description")

    for pattern in BOL_PATTERNS:
        bol_str = " ".join(b.value for b in pattern.bols[:10])
        if len(pattern.bols) > 10:
            bol_str += " ..."
        table.add_row(
            pattern.name,
            str(pattern.matra_count),
            bol_str,
            pattern.description,
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(BOL_PATTERNS)} patterns[/dim]")


if __name__ == "__main__":
    cli()
