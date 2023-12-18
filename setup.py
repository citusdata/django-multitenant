from setuptools import setup, find_packages
from os import path
from io import open

# read the contents of your README file
this_directory = path.dirname(path.abspath(__file__))

with open(path.join(this_directory, "README.md")) as f:
    long_description = f.read()


# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name="django-multitenant",
    version="4.1.1",  # Required
    description="Django Library to Implement Multi-tenant databases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/citusdata/django-multitenant",
    author="Gurkan Indibay",
    author_email="gindibay@microsoft.com",
    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable ",
        "Topic :: Database",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords=("citus django multi tenant" "django postgres multi-tenant"),
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests", "docs", "docs.*"]
    ),
)
