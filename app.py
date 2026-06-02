from __future__ import annotations

import argparse
import uuid

from rich.console import Console
from rich.panel import Panel

from digital_twin.agent import ScientistTwinAgent
from digital_twin.config import settings

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive Digital Twin of a Scientist")
    parser.add_argument("--session", default=None, help="Session id for short-term memory")
    args = parser.parse_args()

    session_id = args.session or str(uuid.uuid4())[:8]
    agent = ScientistTwinAgent(session_id=session_id)

    console.print(Panel.fit(
        f"Digital Twin: {settings.scientist_name}\nSession: {session_id}\nType 'exit' to quit.",
        title="AIMS DTU Summer Project 2026",
    ))

    while True:
        question = console.input("[bold cyan]You:[/bold cyan] ").strip()
        if question.lower() in {"exit", "quit", "q"}:
            break
        if not question:
            continue
        try:
            answer = agent.answer(question)
            console.print(Panel(answer, title=f"{settings.scientist_name} Twin"))
        except Exception as exc:
            console.print(f"[red]Error:[/red] {exc}")


if __name__ == "__main__":
    main()
