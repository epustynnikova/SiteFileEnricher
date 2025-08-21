## Create a `virtualenv` and installing

```
pip install typing-extensions aiohttp lxml bs4 fuzzywuzzy cssselect
pip install site_file_enricher-0.0.1-py2.py3-none-any.whl --force-reinstall
virtualenv venv 	 	
source venv/bin/activate 	
```

To deactvate the virtual environment run `deactivate`

## Simple run

```python
import os
from site_file_enricher.script import enrich_file_with_default_settings

if __name__ == "__main__":
    path = os.path.abspath('input_tsv_file.txt')
    cert_path = os.path.abspath('russiantrustedca/russiantrustedca.pem')
    enrich_file_with_default_settings(path, cert_path)
```

## Create the wheel

In the directory `YOUR_ROOT` run `python setup.py bdist_wheel --universal`.
After that your wheel file will be created under the `dist/` folder.
