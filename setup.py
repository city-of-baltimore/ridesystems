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
        'mechanize',
        'requests',
        'retry',
        'bs4',
    ]
)
