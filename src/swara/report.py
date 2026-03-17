"""Rich-formatted composition reports for SWARA."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from swara.models import Composition, CompositionSection
from swara.composition.jugalbandi import JugalbandiComposition


def print_composition_report(composition: Composition, console: Console | None = None) -> None:
    """Print a rich-formatted report of a composition."""
    if console is None:
        console = Console()

    # Header
    console.print(Panel(
        f"[bold magenta]SWARA Composition Report[/bold magenta]\n"
        f"Raga: [bold cyan]{composition.raga.name}[/bold cyan] "
        f"(Thaat: {composition.raga.thaat or 'N/A'})\n"
        f"Taal: [bold green]{composition.taal.name}[/bold green] "
        f"({composition.taal.matra} matras)\n"
        f"Laya: [bold yellow]{composition.config.laya.value}[/bold yellow]",
        title="SWARA",
        border_style="bright_blue",
    ))

    # Raga details
    raga_table = Table(title="Raga Details", border_style="cyan")
    raga_table.add_column("Property", style="bold")
    raga_table.add_column("Value")

    aroh_str = " ".join(n.swara.value for n in composition.raga.aroh)
    avroh_str = " ".join(n.swara.value for n in composition.raga.avroh)
    raga_table.add_row("Aroh", aroh_str)
    raga_table.add_row("Avroh", avroh_str)
    raga_table.add_row("Vadi", composition.raga.vadi.value if composition.raga.vadi else "N/A")
    raga_table.add_row("Samvadi", composition.raga.samvadi.value if composition.raga.samvadi else "N/A")
    raga_table.add_row("Time", composition.raga.time_of_day or "N/A")
    raga_table.add_row("Rasa", composition.raga.rasa or "N/A")

    if composition.raga.komal_swaras:
        raga_table.add_row("Komal Swaras", ", ".join(s.value for s in composition.raga.komal_swaras))
    if composition.raga.tivra_swaras:
        raga_table.add_row("Tivra Swaras", ", ".join(s.value for s in composition.raga.tivra_swaras))

    console.print(raga_table)

    # Taal details
    taal_table = Table(title="Taal Structure", border_style="green")
    taal_table.add_column("Property", style="bold")
    taal_table.add_column("Value")
    taal_table.add_row("Name", composition.taal.name)
    taal_table.add_row("Matras", str(composition.taal.matra))
    taal_table.add_row("Vibhag", " | ".join(str(v) for v in composition.taal.vibhag))
    taal_table.add_row("Sam", str(composition.taal.sam))
    taal_table.add_row("Khali", ", ".join(str(k) for k in composition.taal.khali))
    theka_str = " ".join(b.value for b in composition.taal.theka)
    taal_table.add_row("Theka", theka_str)
    console.print(taal_table)

    # Sections summary
    section_table = Table(title="Composition Sections", border_style="yellow")
    section_table.add_column("Section", style="bold")
    section_table.add_column("Duration (s)", justify="right")
    section_table.add_column("Notes", justify="right")
    section_table.add_column("Bols", justify="right")

    section_colors = {
        CompositionSection.ALAP: "blue",
        CompositionSection.JOR: "green",
        CompositionSection.JHALA: "yellow",
        CompositionSection.GAT: "red",
    }

    for section in composition.sections:
        color = section_colors.get(section.section_type, "white")
        section_table.add_row(
            f"[{color}]{section.section_type.value.capitalize()}[/{color}]",
            f"{section.duration_seconds:.1f}",
            str(len(section.notes)),
            str(len(section.bol_sequence)),
        )

    section_table.add_row(
        "[bold]Total[/bold]",
        f"[bold]{composition.total_duration:.1f}[/bold]",
        f"[bold]{composition.note_count}[/bold]",
        f"[bold]{composition.bol_count}[/bold]",
    )

    console.print(section_table)

    # Note preview for each section
    for section in composition.sections:
        if section.notes:
            preview_notes = section.notes[:16]
            note_str = " ".join(
                f"{n.swara.value}{'*' if n.has_gamak else ''}{'~' if n.has_meend else ''}"
                for n in preview_notes
            )
            suffix = "..." if len(section.notes) > 16 else ""
            console.print(
                f"  [dim]{section.section_type.value.capitalize()} preview:[/dim] {note_str}{suffix}"
            )


def print_jugalbandi_report(
    composition: JugalbandiComposition,
    instrument_a_name: str = "Sitar",
    instrument_b_name: str = "Veena",
    console: Console | None = None,
) -> None:
    """Print a report for a jugalbandi composition."""
    if console is None:
        console = Console()

    console.print(Panel(
        f"[bold magenta]Jugalbandi Composition[/bold magenta]\n"
        f"Raga: [bold cyan]{composition.raga.name}[/bold cyan]\n"
        f"Laya: [bold yellow]{composition.laya.value}[/bold yellow]\n"
        f"Style: [bold green]{composition.interaction_style}[/bold green]\n"
        f"Duration: {composition.total_duration:.1f}s",
        title="SWARA Jugalbandi",
        border_style="bright_magenta",
    ))

    # Instrument summary
    inst_table = Table(title="Instrument Parts", border_style="cyan")
    inst_table.add_column("Instrument", style="bold")
    inst_table.add_column("Phrases", justify="right")
    inst_table.add_column("Total Notes", justify="right")

    inst_table.add_row(
        instrument_a_name,
        str(len(composition.instrument_a_phrases)),
        str(composition.total_notes_a),
    )
    inst_table.add_row(
        instrument_b_name,
        str(len(composition.instrument_b_phrases)),
        str(composition.total_notes_b),
    )
    console.print(inst_table)

    # Timeline
    console.print("\n[bold]Timeline:[/bold]")
    all_phrases = [
        (p, instrument_a_name, "cyan") for p in composition.instrument_a_phrases
    ] + [
        (p, instrument_b_name, "green") for p in composition.instrument_b_phrases
    ]
    all_phrases.sort(key=lambda x: x[0].start_time)

    for phrase, name, color in all_phrases[:20]:
        role = "CALL" if phrase.is_call else "RESP"
        preview = " ".join(n.swara.value for n in phrase.notes[:8])
        suffix = "..." if len(phrase.notes) > 8 else ""
        console.print(
            f"  [{color}]{phrase.start_time:6.1f}s [{role:4s}] {name}: {preview}{suffix}[/{color}]"
        )

    if len(all_phrases) > 20:
        console.print(f"  [dim]... and {len(all_phrases) - 20} more phrases[/dim]")


def format_raga_card(raga_name: str, console: Console | None = None) -> None:
    """Print a detailed card for a single raga."""
    if console is None:
        console = Console()

    from swara.composition.raga_engine import RagaCompositionEngine

    raga = RagaCompositionEngine.get_raga(raga_name)

    aroh = " ".join(n.swara.value for n in raga.aroh)
    avroh = " ".join(n.swara.value for n in raga.avroh)
    pakad = " ".join(n.swara.value for n in raga.pakad) if raga.pakad else "N/A"

    content = (
        f"[bold]Thaat:[/bold] {raga.thaat or 'N/A'}\n"
        f"[bold]Aroh:[/bold] {aroh}\n"
        f"[bold]Avroh:[/bold] {avroh}\n"
        f"[bold]Pakad:[/bold] {pakad}\n"
        f"[bold]Vadi:[/bold] {raga.vadi.value if raga.vadi else 'N/A'}\n"
        f"[bold]Samvadi:[/bold] {raga.samvadi.value if raga.samvadi else 'N/A'}\n"
        f"[bold]Time:[/bold] {raga.time_of_day or 'N/A'}\n"
        f"[bold]Rasa:[/bold] {raga.rasa or 'N/A'}"
    )

    if raga.komal_swaras:
        content += f"\n[bold]Komal:[/bold] {', '.join(s.value for s in raga.komal_swaras)}"
    if raga.tivra_swaras:
        content += f"\n[bold]Tivra:[/bold] {', '.join(s.value for s in raga.tivra_swaras)}"

    console.print(Panel(content, title=f"Raga {raga.name}", border_style="cyan"))
