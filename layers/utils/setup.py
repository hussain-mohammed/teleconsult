import os

from setuptools import find_packages, setup

thelibFolder = os.path.dirname(os.path.realpath(__file__))
requirementPath = thelibFolder + "/requirements.txt"
install_requires = []
if os.path.isfile(requirementPath):
    print(f"found requirements.txt at: {requirementPath}")
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()
else:
    print("== Couldn't find requirements.txt in path ===")

setup(
    name="utils",
    version="0.1.0",
    description="Setting up a util package for locqum telemedicine",
    author="Adil",
    author_email="adiluddin.mohammed@fissionlabs.com",
    packages=find_packages(
        include=["utils", "utils.templates.*", "utils.*"]
    ),
    package_data={"utils": ["*.json", "*.html", "templates/**/*.html"]},
    install_requires=install_requires,
)
