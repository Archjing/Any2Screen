from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

# Front-door command registry.
# Add new subcommands here without changing CLI routing logic.
COMMAND_SCRIPTS = {
    "doc2md": ROOT / "src/a2s/doc2md.py",
    "md2html": ROOT / "src/a2s/md2html.py",
    "md2img": ROOT / "src/a2s/md2img.py",
}
