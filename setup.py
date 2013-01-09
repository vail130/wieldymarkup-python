import sys
from wieldymarkup import __version__
from distutils.core import setup

# To install the wieldymarkup-python library, open a Terminal shell, then run this
# file by typing:
#
# python setup.py install
#
# You need to have the setuptools module installed. Try reading the setuptools
# documentation: http://pypi.python.org/pypi/setuptools
REQUIRES = ["six"]

if sys.version_info >= (3,0):
  REQUIRES.append('unittest2py3k')
else:
  REQUIRES.append('unittest2')

setup(
  name = "wieldymarkup",
  version = __version__,
  packages = ['wieldymarkup', 'wieldymarkup.test'],
  description = "WieldyMarkup HTML Abstraction Markup Language Compiler",
  author = "Vail Gold",
  author_email = "vail@vailgold.com",
  url = "http://github.com/vail130/wieldymarkup-python/",
  license = "LICENSE.txt",
  install_requires = REQUIRES,
  classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.5",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.2",
    "Topic :: Software Development :: Libraries :: Python Modules",
  ],
  long_description = """\
  WieldyMarkup HTML Abstraction Markup Language Compiler
  ----------------------------

  DESCRIPTION
  The WieldyMarkup compiler allows you to write more concise HTML templates
  for your modern web applications. It works with other templating engines
  as well, like Underscore, Mustache, et cetera.
  See http://www.github.com/vail130/wieldymarkup-python for more information.

  LICENSE The WieldyMarkup HTML Abstraction Markup Language Compiler is
  distributed under the MIT License.""" )