# seinpy
`Seinpy` is an extensible Python tool to build and programatically access data on Seinfeld scripts!

## Project Structure

`Seinpy` can broadly be broken into two functions. 
1. Extracting Seinfeld data into standard data structures.
2. Exporting Seinfeld data from these standard data structures.

## Installation

Detailed step-by-step setup and environment configuration are available in the [Installation Guide](docs/installation.md). `seinpy` is available on PyPI. 

```bash 
pip install seinpy
```

## Example

```python 
from seinpy import read_episodes, write_episodes, Source

# Configure source
source = Source(script="kaggle")

# Read scripts
episodes = read_episodes(source=source, episode_ids=["S01E01"])

# Export the episodes into a single JSON file
write_episodes(
    save_type="json",
    save_path="seinfeld_episodes.json",
    data=episodes,
)
```

## Code Contributions

For guidelines on how to set up the repository for development, run tests, and submit code changes, please refer to the [Contributing Guide](docs/contributing.md) in the documentation site.

## Dependencies 

This project relies on data from the following sources. Please consider checking out the projects yourselves! 
* Kaggle Seinfeld Scripts: [https://www.kaggle.com/datasets/benedictoliver/seinfeld-scripts](https://www.kaggle.com/datasets/benedictoliver/seinfeld-scripts)
* OMDb: [https://www.omdbapi.com/](https://www.omdbapi.com/)
* IMDb: [https://www.imdb.com/](https://www.imdb.com/)




