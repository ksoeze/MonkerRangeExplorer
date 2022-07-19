from setuptools import setup

with open("README.org", "r") as fh:
    long_description = fh.read()

setup(name='',
      version='0.1.0',
      author="ksoeze",
      author_email="h.e.@gmx.at",
      description="",
      long_description=long_description,
      packages=setuptools.find_packages()
      )
