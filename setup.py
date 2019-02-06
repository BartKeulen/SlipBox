import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="slipbox",
    version="0.0.1",
    author="Bart Keulen",
    author_email="contact@bartkeulen.com",
    description="A command line application for creating a slipbox",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/pypa/sampleproject",
    packages=['slipbox'],
    entry_points='''
        [console_scripts]
        sb=slipbox:cli
    '''
)