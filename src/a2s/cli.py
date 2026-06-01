#!/usr/bin/env python3
import argparse
import runpy
import sys
from a2s.command_registry import COMMAND_SCRIPTS


def main() -> int:
    parser = argparse.ArgumentParser(prog="any2screen", description="Unified entrypoint for Any2Screen modules")
    parser.add_argument("module", choices=sorted(COMMAND_SCRIPTS.keys()), help="Module to run")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments passed to selected module")
    ns = parser.parse_args()

    script = COMMAND_SCRIPTS[ns.module]
    sys.argv = [str(script), *ns.args]
    runpy.run_path(str(script), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
