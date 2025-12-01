# check_stack.py
import sys
import importlib
import subprocess


def show_pkg(name, import_name=None):
    import_name = import_name or name
    try:
        m = importlib.import_module(import_name)
        v = getattr(m, "__version__", "no __version__ attribute")
        print(f"{name:12s} -> {v}")
    except ImportError:
        print(f"{name:12s} -> NOT INSTALLED")


def show_cli(cmd, label=None):
    label = label or cmd[0]
    try:
        print(f"\n[{label}]")
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False
        )
        print(result.stdout.strip())
    except FileNotFoundError:
        print(f"{label} -> NOT FOUND (not on PATH)")


def main():
    print("=== PYTHON VERSION ===")
    print(sys.version)
    print()

    print("=== PYTHON PACKAGES (import) ===")
    show_pkg("duckdb")
    show_pkg("pandas")
    show_pkg("streamlit")
    show_pkg("meltano")
    # dbt-core is installed as 'dbt'
    show_pkg("dbt-core", import_name="dbt")

    # dbt-duckdb is a plugin, not a simple top-level module,
    # we mainly check via CLI below.

    print("\n=== CLI VERSIONS ===")
    show_cli(["meltano", "--version"], label="meltano --version")
    show_cli(["dbt", "--version"], label="dbt --version")


if __name__ == "__main__":
    main()
