import setuptools

setuptools.setup(
    name="ridesystems",
    version="0.3",
    author="Brian Seel",
    author_email="brian.seel@baltimorecity.gov",
    description="Interface with the Ridesystems website",
    packages=['ridesystems'],
    package_data={'ridesystems': ['py.typed'],},
    python_requires='>=3.0',
    package_dir = {'ridesystems': 'src'},
    install_requires=[
        'mechanize',
        'requests',
        'retry',
        'bs4',
    ]
)
