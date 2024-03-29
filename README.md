# xivo-fetchfw
[![Build Status](https://jenkins.wazo.community/buildStatus/icon?job=xivo-fetchfw)](https://jenkins.wazo.community/job/xivo-fetchfw)

A simple "out-of-control" package manager in python.

fetchfw main goal is to provide installation/upgrade/uninstallation of
packages for which the main content is not redistributable.

The common usage is that you have some files downloadable over the internet
which you want to be able to download, possibly apply some filters over them
(extract a zip file, exclude some directories) and then copy the result on a
specific path of your filesystem, keeping information about which files have
been created in the process so you can remove them later.

That said, you can also use it as a simple, general-purpose, package manager.

## Requirements

Minimum python version is python 3.9.

## Dependencies

* xivo_fetchfw depends on `progressbar`
  * http://pypi.python.org/pypi/progressbar

## Running unit tests

```
pip install tox
tox --recreate
```
