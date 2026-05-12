from pathlib import Path

import tomli


def define_env(env):  # noqa: ANN001
    @env.macro
    def get_version() -> str:
        pyproject = Path(__file__).parent.parent / "pyproject.toml"
        with pyproject.open("rb") as f:
            data = tomli.load(f)
        return data["project"]["version"]
