import re
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

VERSION = None
REQUIREMENTS = [
    'pygame==1.9.3',
    'pretty_midi',
    'midiutil'
]

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

def find_version(fname):
    """Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    """
    version = ''
    with open(fname, 'r') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version

__version__ = find_version("sonify/__init__.py")

setup(
    name='sonify',
    version=__version__,
    description='A sample Python project',
    url='https://github.com/erinspace/sonify/',
    author='Erin Braswell',
    author_email='erin.braswell@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='midi music data',
    packages=find_packages(exclude=('test*', 'examples','docs')),
    install_requires=REQUIREMENTS,
    extras_require={  # Optional
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    project_urls={
        'Bug Reports': 'https://github.com/erinspace/sonify/issues',
        'Source': 'https://github.com/erinspace/sonify',
    },
)