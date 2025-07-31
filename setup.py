from setuptools import setup

setup(
    name='site_file_enricher',
    version='0.0.1',
    packages=[
        '.site_file_enricher',
        '.site_file_enricher.model',
        '.site_file_enricher.io',
        '.site_file_enricher.file_parser',
        '.site_file_enricher.search'
    ]
)

# python setup.py bdist_wheel --universal
