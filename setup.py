import setuptools

with open('README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name = 'risk_dash',
    version = '0.0.2',
    author = 'Alexander van Oene',
    author_email = 'alex.vanoene@gmail.com',
    description = 'A data framework to handle a portfolio of assets',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/avanoene/risk_dash',
    packages = setuptools.find_packages()
)
