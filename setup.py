import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="graphical-models",
    version="0.0.1",
    author="D-K-E",
    author_email="qm.auber@tutanota.com",
    description="Graphical Models in Standard Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/D-K-E/graphical-models",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU GPL License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
