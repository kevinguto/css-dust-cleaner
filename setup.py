# coding: utf8

import re
import os.path


ROOT = os.path.dirname(__file__)
README = open(os.path.join(ROOT, 'README.md')).read()
INIT_PY = open(os.path.join(ROOT, 'dustcleaner', '__init__.py')).read()
VERSION = re.search("VERSION = '([^']+)'", INIT_PY).group(1)


setup(
    name='dustcleaner',
    version=VERSION,
    author='Kriss Mikelsons',
    author_email='kriss@application.lv',
    description=
        'Tool that removes unused CSS selectors by searching through definied directories',
    long_description=README,
    url='http://github.com/mkriss/css-dust-cleaner',
    license='MIT',
    packages=['dustcleaner'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
    ],
    **extra_kwargs
)