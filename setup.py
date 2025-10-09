from setuptools import setup, find_packages

setup(
    name="smartcity-datalake",
    # version="0.1.0",
    description="Smart City datalake, flows and tools",
    packages=find_packages(include=["smartcity*", "prefect_flows*"]),
)
