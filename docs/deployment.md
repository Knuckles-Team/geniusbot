# Deployment

Axil ships as a Python package and as a standalone desktop executable.

## Package

```bash
uv sync --all-extras
uv run axil
```

## Executable

```bash
uv run pyinstaller --clean axil.spec
```

The `packaging/` directory and `setup.iss` hold the installer inputs. The `release.yml` workflow publishes releases.
