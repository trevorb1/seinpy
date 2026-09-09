# Reference

This page provides background information, structural details, and architectural patterns of the **seinpy** package.

---

## About & Background

`seinpy` was built to address the lack of structured, easily accessible datasets containing Seinfeld episode scripts and their associated metadata. While script transcript datasets exist, they are often inconsistent in formatting, missing key details, or lack metadata (such as user ratings and cast/crew credits).

`seinpy` acts as a data pipeline that:

1. Downloads and parses raw scripts from multiple web sources.
2. Cross-references episodes against metadata to resolve inconsistencies in season and episode numbering.
3. Automatically fetches rich metadata (cast credits, rating distributions).
4. Exports the compiled data into CSV, JSON, or SQL Databases.

---

## Architecture

The package is designed around the **Strategy Pattern**. This makes it easy to switch out the extraction source for scripts, ratings, or credits without changing the core execution engine.

```mermaid
flowchart TD
    subgraph ClientLayer["Client & Orchestration"]
        Context["<b>Context</b><br/><code>seinpy.context.Context</code>"]
    end

    subgraph StrategyLayer["Strategy Contracts (seinpy.base)"]
        direction TB
        SE["<b>ScriptExtractor</b><br/><i>extract_script()</i>"]
        CE["<b>CreditExtractor</b><br/><i>extract_credit()</i>"]
        RE["<b>RatingExtractor</b><br/><i>extract_rating()</i>"]
        EX["<b>Exporter</b><br/><i>export()</i>"]
    end

    subgraph DriverLayer["Available Implementations"]
        direction TB
        SE_Drivers["<b>Script Extractors</b><br/>• KaggleScriptExtractor<br/>• SeinologyScriptExtractor<br/>• SeinfeldScriptsExtractor<br/>• IMDbScriptExtractor"]
        CE_Drivers["<b>Credit Extractors</b><br/>• OMDBCreditExtractor<br/>• RottenTomatoesCreditExtractor"]
        RE_Drivers["<b>Rating Extractors</b><br/>• OMDBRatingExtractor<br/>• RottenTomatoesRatingExtractor"]
        EX_Drivers["<b>Exporters</b><br/>• CsvExporter<br/>• JsonExporter<br/>• DatabaseExporter"]
    end

    Context -->|"delegates to"| SE
    Context -->|"delegates to"| CE
    Context -->|"delegates to"| RE
    Context -->|"delegates to"| EX

    SE -.->|"implements"| SE_Drivers
    CE -.->|"implements"| CE_Drivers
    RE -.->|"implements"| RE_Drivers
    EX -.->|"implements"| EX_Drivers
```

### Components

- **Context**: The orchestrator that receives concrete Strategy instances via its constructor or helper function `read_episodes`.
- **Script Extractors**: Strategies responsible for pulling and parsing episode scripts.
- **Credit Extractors**: Strategies responsible for pulling cast/crew metadata.
- **Rating Extractors**: Strategies responsible for pulling ratings (e.g., from OMDb or Rotten Tomatoes).
- **Exporters**: Strategies responsible for converting list of structured Pydantic/SQLModel models into target files.

---

## Usage Options & Configuration

When calling `read_episodes()`, you configure your source strategies using a source dictionary.

```python
source = {
    "script": "kaggle",  # Option for script source
    "credit": "omdb",       # Option for credits metadata
    "rating": "omdb",       # Option for ratings metadata
}
```

### Script Extraction Sources
- **`seinology`**: Extracts transcripts from Seinology.
- **`seinfeldscripts`**: Extracts transcripts from seinfeldscripts.com.
- **`kaggle`**: Extracts from Kaggle's Seinfeld script dataset.
- **`imdb`** / **`imsdb`**: Extracts scripts from IMSDb.

!!! warning

    Only `kaggle` is currently supported for script extraction

### Credit Extraction Sources
- **`omdb`**: Uses the Open Movie Database (OMDb) API. Requires `OMDB_API_KEY`.
- **`rottentomatoes`**: Scrapes Rotten Tomatoes for ratings/credits.

!!! warning

    Only `omdb` is currently supported for credit extraction

### Rating Extraction Sources
- **`omdb`**: Uses the Open Movie Database (OMDb) API. Requires `OMDB_API_KEY`.
- **`rottentomatoes`**: Scrapes Rotten Tomatoes for ratings/credits.

!!! warning

    Only `omdb` is currently supported for rating extraction

### Exporter Output Types
- **`csv`**: Writes tabular episode and line data.
- **`json`**: Writes a nested JSON schema representation.
- **`database`**: Populates a relational database (SQLite/PostgreSQL) using SQLModel.
