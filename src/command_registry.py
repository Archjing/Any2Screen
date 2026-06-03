from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# Front-door command registry.
# Add new subcommands here without changing CLI routing logic.
COMMAND_SCRIPTS = {
    "convert": ROOT / "src/convert_cli.py",
    "any2html": ROOT / "src/any2html_cli.py",
    "html2screen": ROOT / "src/html2screen_cli.py",
    "preview": ROOT / "src/preview_cli.py",
    "web": ROOT / "src/web_cli.py",
    "doc2md": ROOT / "src/doc2md.py",
}
