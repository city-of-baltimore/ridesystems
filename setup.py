import setuptools

setuptools.setup(
    name="ridesystems",
    version="0.1",
    author="Brian Seel",
    author_email="brian.seel@baltimorecity.gov",
    description="Interface with the Ridesystems website",
    packages=['ridesystems'],
    python_requires='>=3.0',
    package_dir = {'ridesystems': 'src'},
    install_requires=[
        'mechanize',
        'requests',
        'retry',
        'bs4',
    ]
)
