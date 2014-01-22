xivo-fetchfw
=========
[![Build Status](https://travis-ci.org/xivo-pbx/xivo-fetchfw.png?branch=master)](https://travis-ci.org/xivo-pbx/xivo-fetchfw)

A simple "out-of-control" package manager in python.

fetchfw main goal is to provide installation/upgrade/uninstallation of
packages for which the main content is not redistributable.

The common usage is that you have some files downloadable over the internet
which you want to be able to download, possibly apply some filters over them
(extract a zip file, exclude some directories) and then copy the result on a
specific path of your filesystem, keeping information about which files have
been created in the process so you can remove them later.

That said, you can also use it as a simple, general-purpose, package manager.

Requirements
============

Minimum python version is python 2.6. Does not work on python 3.

Dependencies
============

* Beautiful Soup
  * http://www.crummy.com/software/BeautifulSoup/
* xivo_fetchfw depends on progressbar
  * http://pypi.python.org/pypi/progressbar
* some unit tests depend on the "mock" python package
  * http://pypi.python.org/pypi/mock