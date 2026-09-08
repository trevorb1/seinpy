# Installation & Configuration

Follow these steps to set up `seinpy` on your local system and configure external APIs.

---

## User Installation

### 1. Install `seinpy`

`seinpy` is deployed to the Python Package Index (PyPI) and can be installed using pip.

```bash
pip install seinpy
```

Alternatively, you can clone the Git repository and install it from source:

```bash
git clone https://github.com/trevorb1/seinpy.git
cd seinpy
pip install .
```

### 2. Set up the OMDb API Key
If you plan to fetch Seinfeld Credits and Ratings via the [OMDb](https://www.omdbapi.com/) API, you will need to request a free API key from [OMDb](https://www.omdbapi.com/apikey.aspx).

Once you have your key, you can expose it as an environment variable:

**One-time setting (Linux/macOS):**
```bash
export OMDB_API_KEY="your_api_key_here"
```

**Persistent setting (Linux/macOS):**
Add it to your shell configuration file (e.g., `~/.bashrc`, `~/.zshrc`):
```bash
echo 'export OMDB_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

**Using directly in code:**
Alternatively, you can pass the OMDb API key directly to `read_episodes` or Strategy functions.

---

## Development Installation

`seinpy` uses **uv** for package and environment management.

### 1. Install `uv`
If you do not have `uv` installed, you can install it using:

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

For other platform-specific methods, see the official [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).

### 2. Fork and Clone the Repository
Clone the codebase to your local machine:
```bash
git clone https://github.com/trevorb1/seinpy.git
cd seinpy
```

### 3. Create and Activate Virtual Environment
Use `uv` to initialize a virtual environment:

**macOS & Linux:**
```bash
uv venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
uv venv
.venv\Scripts\Activate.ps1
```

### 4. Sync Dependencies
Sync the python virtual environment to install all required dependencies defined in the lockfile:

```bash
uv sync
```
