import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = fh.readlines()

with open("requirements_develop.txt", "r") as fh:
    requirements_develop = fh.readlines()

setuptools.setup(
    name="dcs-worklog",
    version="0.0.36",
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
        # see: https://pypi.org/classifiers/
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Office/Business",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    extras_require={"develop": requirements_develop},
    entry_points={"console_scripts": ["wl=worklog:run",]},
)
