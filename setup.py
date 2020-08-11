import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = fh.readlines()

with open("requirements_test.txt", "r") as fh:
    requirements_test = fh.readlines()

setuptools.setup(
    name="dcs-worklog",
    version="0.0.22",
    author="Fabian Mueller",
    author_email="repository@dotcs.me",
    description="Simple CLI tool to log work and projects",
    license="GPLv3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dotcs/worklog",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    extras_require={"testing": requirements_test},
    entry_points={"console_scripts": ["wl=worklog:run",]},
)
