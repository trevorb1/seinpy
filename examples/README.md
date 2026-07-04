# Examples 

Each datapoint collected is an `Episode`. Each episode is comprised of three components; a `Script`, a `Credit` and a `Rating`. Data for each `Script`, `Credit` and `Rating` can originate from different sources and **must** include a `Reference` which contains the `EpisodeNum`, the `EpisodeID` (the Season Episode identifier in the form `SxxExx`), and the `EpisodeTitle`. When assembling an `Episode`, the `Reference` for each `Script`, `Credit` and `Rating` are compared to ensure consistency. This is needed as, for example, two-part episodes or clip show episodes may be indexed differently between sources. 

### Reference

#### Example

### Script Extractors

#### Example

### Credit Extractors 

#### Example

### Rating Extractors 

#### Example

### Episode

#### Example

## Data Exporters 

### Json Exporter

#### Example

```python
from seinpy import JsonExporter
from seinpy.extractors import ScriptExtractor, CreditExtractor, RatingExtractor
from seinpy.schema import Episode

script_extractor = ScriptExtractor()
credit_extractor = CreditExtractor()
rating_extractor = RatingExtractor()

script_extractor.extract()
credit_extractor.extract()
rating_extractor.extract()

episode = Episode(script=script_extractor.data, credit=credit_extractor.data, rating=rating_extractor.data)

json_exporter = JsonExporter()
json_exporter.export([episode], "./data.json")
```