from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kalshi-python-unofficial",  # Replace with your desired package name
    version="0.0.1",
    author="humz2k",
    description="A unofficial Python wrapper for the Kalshi API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/humz2k/kalshi-python-unofficial",  # Replace with your repo URL
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=["websockets>=10.0", "Requests", "cryptography"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Choose your license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    include_package_data=True,
)
