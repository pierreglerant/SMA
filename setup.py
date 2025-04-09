from setuptools import setup, find_packages

setup(
    name="first_model",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "mesa>=2.1.1",
        "solara>=1.32.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
    ],
) 