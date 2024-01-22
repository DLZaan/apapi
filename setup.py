import os

from setuptools import find_packages, setup

REQUIRES_PYTHON = "~=3.8"

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "requirements.txt"), encoding="utf-8") as f:
    requires = f.readlines()

with open(os.path.join(here, "requirements-dev.txt"), encoding="utf-8") as f:
    dev_requires = f.readlines()[1:]

about = {}
with open(os.path.join(here, "apapi", "__version__.py"), encoding="utf-8") as f:
    exec(f.read(), about)

try:
    with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = about["__description__"]

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    author_email=about["__author_email__"],
    maintainer=about["__author__"],
    maintainer_email=about["__author_email__"],
    url=about["__url__"],
    license=about["__license__"],
    platforms="any",
    keywords="anaplan anaplanapi anaplanconnector client",
    packages=find_packages(),
    include_package_data=True,
    python_requires=REQUIRES_PYTHON,
    install_requires=requires,
    extras_require={
        "dev": dev_requires,
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries",
    ],
    project_urls={
        "Documentation": "https://dlzaan.github.io/apapi/apapi.html",
        "Source": "https://github.com/DLZaan/apapi",
        "Changelog": "https://pip.pypa.io/en/stable/news/",
    },
    entry_points={
        "console_scripts": [
            "apapi=apapi.__main__:main",
        ]
    },
)
