"""CLI entry point for training baseline Nobel prediction models."""

from __future__ import annotations

from pathlib import Path

import click

from backend.app.services.modeling import train_models


@click.command()
@click.option("--output", type=click.Path(path_type=Path), default=Path("../shared/artifacts"))
def main(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    artifacts = train_models()
    click.echo("Artifacts generated:")
    for name, path in artifacts.items():
        click.echo(f"- {name}: {path}")


if __name__ == "__main__":
    main()

