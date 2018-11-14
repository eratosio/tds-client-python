
import os
from setuptools import setup, find_packages

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

def get_version(version_file):
    ns = {}
    exec(read(version_file), ns)
    return ns['__version__']

setup(
    name = 'tds_client',
    version = get_version('tds_client/version.py'),
    author = 'Mac Coombe',
    author_email = 'mac.coombe@csiro.au',
    description = ('Thredds Data Server (TDS) Client'),
    # TODO: license = '',
    keywords = 'Thredds',
    url = 'https://bitbucket.csiro.au/projects/SC/repos/tds-client-python/browse',
    packages = find_packages(),
    long_description = read('readme.md'),
    install_requires = [
        'requests',
        'pydap',
        'netCDF4'
    ],
    entry_points = {
        'tds_client.service': [
            'OpenDAP = tds_client.service.opendap:OPeNDAPService',
            'NetcdfSubset = tds_client.service.ncss:NetCDFSubsetService'
        ]
    },
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Topic :: Scientific/Engineering :: Information Analysis',
        # TODO: 'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7'
    ]
)
