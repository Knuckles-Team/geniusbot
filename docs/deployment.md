# Deployment

GeniusBot ships as a Python package and as a standalone desktop executable.

## Package

```bash
uv sync --all-extras
uv run geniusbot
```

## Executable

```bash
uv run pyinstaller --clean geniusbot.spec
```

The `packaging/` directory and `setup.iss` hold the installer inputs. The `release.yml` workflow publishes releases.
