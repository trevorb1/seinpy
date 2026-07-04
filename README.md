# seinpy
`Seinpy` is an extensible Python tool to build and programatically access data on Seinfeld scripts!

## Project Structure

`Seinpy` can broadly be broken into two functions. 
1. Extracting Seinfeld data into standard data structures.
2. Exporting Seinfeld data from these standard data structures.

## Development

Development covers how to install and contribute to `seinpy`.

### Installation 

1. If you don’t already have `uv` installed, and are using macOS or Linux, install it with:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or see the official [uv installation](https://docs.astral.sh/uv/getting-started/installation/) guide for platform-specific options.

2. Fork and clone the repository 

```bash
https://github.com/trevorb1/seinpy.git
cd seinpy
```

3. Create and Activate the Environment with `uv`

```bash 
uv venv
source .venv/bin/activate   # on macOS/Linux
.venv\Scripts\activate      # on Windows (PowerShell: .venv\Scripts\Activate.ps1)
```

4. (Optional) Sync Environment

If you need to bring the environment in sync with the `uv.lock`/`pyproject.toml` file, run the folling command. 

```bash 
uv sync
```

### Code Contributions 

1. Create a new branch 

```bash 
git checkout -b feature-branch 
```

2. Make code changes and add tests if required 

3. Run tests

```bash 
uv run pytest
```

Additionally, you can view a full coverage report with 

```bash 
uv run pytest --cov=seinpy tests/ --cov-report=term-missing
```

4. Install and Run Pre-Commit Hooks 

```bash 
uv run pre-commit install
```

5. Push changes and lauch a pull request

```bash 
uv run pre-commit install
```



