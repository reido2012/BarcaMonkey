from distutils.core import setup

setup(
    name='BarcaMonkey',
    version='0.1.0',
    author='Omar Reid',
    author_email='oreid52@googlemail.com',
    packages=['barcamonkey'],
    description='Collects Odds Data ',
    install_requires=[
        "slackclient",
        "xmltodict",
        "beautifulsoup4",
        "dateparser",
        "pytz"
    ],
)