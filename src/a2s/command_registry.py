from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

# Front-door command registry.
# Add new subcommands here without changing CLI routing logic.
COMMAND_SCRIPTS = {
    "convert": ROOT / "src/a2s/convert_cli.py",
    "any2html": ROOT / "src/a2s/any2html_cli.py",
    "html2screen": ROOT / "src/a2s/html2screen_cli.py",
    "doc2md": ROOT / "src/a2s/doc2md.py",
}
