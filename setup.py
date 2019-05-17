# Copyright (C) 2008, 2009 Michael Trier and contributors
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of the GitPython project nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

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
    version="2.0.9",
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
