
# For some usefule documentation, see
# https://docs.python.org/2/distutils/setupscript.html.
# This page is useful for dependencies: 
# http://python-packaging.readthedocs.io/en/latest/dependencies.html.

from distutils.core import setup

setup(
  name = "gbsc_dnanexus",
  version = "0.1.0",
  description = "DNAnexus utilities",
  author = "Nathaniel Watson",
  author_email = "nathankw@stanford.edu",
  url = "https://github.com/StanfordBioinformatics/gbsc_dnanexus",
  packages = ["gbsc_dnanexus"],
  install_requires = [
    "dxpy",
  ],
  scripts = ["gbsc_dnanexus/scripts/invite_user_to_projects.py"]
)
