from seinpy.scripts.kaggle import KaggleScriptExtractor

extractor = KaggleScriptExtractor()

script = extractor.extract(episode_id="S01E04", as_df=True)

print(script)
