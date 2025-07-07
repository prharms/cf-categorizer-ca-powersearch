"""Setup configuration for the Campaign Finance Contributor Categorization Tool."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cf-categorizer-ca-powersearch",
    version="1.0.0",
    author="prharms",
    description="AI-powered tool to categorize California PowerSearch campaign finance contributors using Claude 4 Sonnet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prharms/cf-categorizer-ca-powersearch",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "categorize-contributors=src.categorize_contributors:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md"],
    },
) 