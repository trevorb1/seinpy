# Examples

This page contains examples and walk-throughs of common operations with `seinpy`.

---

## 1. Basic Reading and Exporting

This example demonstrates how to read all Seinfeld episode scripts from the Kaggle source using `Source` and export them to a JSON file.

```python
from seinpy import read_episodes, write_episodes, Source

# Configure source
source = Source(script="kaggle")

# Read scripts
episodes = read_episodes(source=source, get_all=True)

# Export the episodes into a single JSON file
write_episodes(
    save_type="json",
    save_path="seinfeld_episodes.json",
    data=episodes,
)
```

---

## 2. Using Custom Sources and Extractors

You can configure different extractors for scripts, credits, and ratings. Here is how to configure `seinpy` to use Seinology scripts combined with OMDb credits.

```python
import os
from seinpy import read_episodes, Source

# Ensure you have your OMDb API Key set
os.environ["OMDB_API_KEY"] = "your_api_key"

# Instantiate the Source configuration
source = Source(
    script="seinology",
    credit="omdb",
    rating="omdb",
)

# Fetch episode 1 of Season 1
episodes = read_episodes(
    source=source,
    seasons=[1],
    episode_nums=[1],
)
```

---

## 3. Exporting to a Database

`seinpy` supports exporting structured scripts directly to a relational SQLite database.

```python
from seinpy import read_episodes, write_episodes, Source

# Read episodes from Kaggle dataset
episodes = read_episodes(
    source=Source(script="kaggle"),
    get_all=True
)

# Export to a SQLite database file
write_episodes(
    save_type="database",
    save_path="seinfeld.db",
    data=episodes,
)
```
