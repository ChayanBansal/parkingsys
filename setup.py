import email
from setuptools import find_packages, setup

setup(
    name="parkingsys",
    version="1.0.0",
    description="Parking Management System",
    author="Chayan Bansal",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask==2.1.2",
        "Flask-Cors==3.0.10",
        "tinydb==4.7.0"
        ]
)