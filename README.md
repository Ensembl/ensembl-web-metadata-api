# Ensembl Web Metadata API
Metadata API for new Ensembl website (https://beta.ensembl.org)

Project is managed with uv.
If you don't have it:
```bash
pipx install uv
# This should also give you optional dev dependencies
uv sync --locked
cp .env.sample .env
# Look at .env, edit as appropriate
# ensure the metadata DuckDB is copied to ./data/duck_meta.db
uv run uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

### Build and run with Docker/podman
```bash
sudo podman build --tag=duck-meta .
vi .env # add values for PORT / enable or disable redis
sudo podman run -it --mount type=bind,src=./data,dst=/data -p 8000:8000 duck-meta:latest
```

### Run together with Redis
```bash
vi .env # add values for PORT / enable or disable redis
sudo podman-compose up
```

### Run unit tests:
```bash
uv run pytest
```

### Format code
```bash
uv run black src/api
```

### Dependency management
```bash
# Add/remove project dependency
uv add httpx
uv remove httpx
# Dev dependency
uv add --dev httpx
# Alternative
uv add httpx --group dev
uv remove --dev httpx
# List dependencies
uv tree

# A venv is managed by uv. You don't need an extra one. You don't have to
# activate it. pyproject.toml is updated for you. A uv.lock file is written and
# kept up to date. Changes to uv.lock should be committed to git.
```
