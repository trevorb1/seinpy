# Examples

This page contains examples and walk-throughs of common operations with `seinpy`.

---

## 1. Basic Reading and Exporting

This example demonstrates how to read all Seinfeld episode scripts from the Kaggle source using `Source` and export them to a JSON file.

```python
from seinpy import read_episodes, write_episodes, Source

# Configure source
# Select any of script, credit, and rating sources.
source = Source(script="kaggle", credit="omdb", rating="omdb")

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

## 2. Filtering by episode number

To filter by episode number, use the `episode_nums` parameter in the `read_episodes` function.

```python
from seinpy import read_episodes, write_episodes, Source

# Configure source
# Select any of script, credit, and rating sources.
source = Source(script="kaggle", credit="omdb", rating="omdb")

# Read episodes 1 and 2 of season 1
episodes = read_episodes(source=source, seasons=[1], episode_nums=[1, 2])

# Export the episodes into a single CSV file
write_episodes(
    save_type="csv",
    save_path="seinfeld_episodes.csv",
    data=episodes,
)
```

---

## 3. Changing the logging level

To change the logging level, import `configure_logging` from the `seinpy.logging` module and set the desired level.

```python
from seinpy import read_episodes, write_episodes, Source
from seinpy.logging import LogLevels, configure_logging

# Set logging level to INFO and above
configure_logging(LogLevels.info)

# Configure source
# Select any of script, credit, and rating sources.
source = Source(script="kaggle", credit="omdb", rating="omdb")

# Read scripts
episodes = read_episodes(source=source, seasons=[1], episode_nums=[1, 2])

# Export the episodes into a single SQLite database file
write_episodes(
    save_type="database",
    save_path="seinfeld_episodes.db",
    data=episodes,
)
```
