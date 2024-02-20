from setuptools import setup, find_packages

PACKAGE_VERSION = "1.1"

MINIMUM_PYTHON_VERSION = 3.6


PACKAGES = find_packages()


with open("requirements.txt", "r") as f:
    REQUIREMENTS = f.read().splitlines()


setup(
    name="uprm-gps-utils",
    version=PACKAGE_VERSION,
    install_requires=[REQUIREMENTS],
    author="UPRM Roboboat Team",
    author_email="pedrocpt2001@icloud.com",
    packages=PACKAGES,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=f">={MINIMUM_PYTHON_VERSION}",
)