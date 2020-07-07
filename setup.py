from setuptools import setup, find_packages
from os import path
from io import open


# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name="django-multitenant",
    version='2.2.2',  # Required
    description='Django Library to Implement Multi-tenant databases',
    url="https://github.com/citusdata/django-multitenant",
    author='Louise Grandjonc',
    author_email='louise.grandjonc@microsoft.com',

    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Database",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers"
    ],

    keywords=("citus django multi tenant"
              "django postgres multi-tenant"),
    packages=find_packages(exclude=['tests']),  # Required
)
