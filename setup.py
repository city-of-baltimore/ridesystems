from setuptools import setup, find_packages

setup(
    name="ridesystems",
    version="0.3",
    author="Brian Seel",
    author_email="brian.seel@baltimorecity.gov",
    description="Interface with the Ridesystems website",
    packages=find_packages('src'),
    package_data={'ridesystems': ['py.typed'], },
    python_requires='>=3.0',
    package_dir={'': 'src'},
    install_requires=[
        'mechanize~=0.4.5',
        'requests~=2.25.1',
        'tenacity~=8.0.1',
        'beautifulsoup4~=4.9.3',
        'pandas~=1.3.0',
    ]
)
