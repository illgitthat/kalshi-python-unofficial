from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kalshi-python-unofficial",
    version="0.2.0",
    author="humz2k",
    description="An unofficial Python wrapper for the Kalshi API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/illgitthat/kalshi-python-unofficial",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=["websockets>=10.0", "Requests", "cryptography"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    include_package_data=True,
)
