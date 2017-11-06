import os.path
import sys

# Version file managment scheme and graceful degredation for
# setuptools borrowed and adapted from GitPython.
try:
    from setuptools import setup, find_packages

    # Silence pyflakes
    assert setup
    assert find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


from setuptools import setup, find_packages
setup(
    name="django-multitenant",
    version="1.0.1",
    packages=find_packages(),

    #install_requires=['gevent>=1.1.1'],
    #extras_require={
    #    'aws': ['boto>=2.40.0'],
    #    'azure': ['azure>=1.0.3'],
    #    'google': ['google-cloud-storage>=0.22.0'],
    #    'swift': ['python-swiftclient>=3.0.0',
    #              'python-keystoneclient>=3.0.0']
    #},

    author="Django-Multitenant Author",
    author_email="sai@citusdata.com",
    maintainer="Sai Srirampur",
    maintainer_email="sai@citusdata.com",
    description="Django Library to Implement Multi-tenant datbases",
    #long_description=read('README.rst'),
    classifiers=[
        'Topic :: Database',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    platforms=['any'],
    license="BSD",
    keywords=("citus django multi tenant"
              "django postgres multi-tenant"),
    url="https://github.com/citusdata/django-multitenant")

    # Include the VERSION file
    #package_data={'django-multitenant': ['0.1']})

    # install
    #entry_points={'console_scripts': ['django-multitenant=django-multitenant.cmd:main']})
