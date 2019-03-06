from setuptools import find_packages, setup

setup(
    name="discourse-sso",
    version="0.1.0",
    author="Kitware, Inc.",
    author_email="kitware@kitware.com",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        "flask",
        "marshmallow>=3.0.0rc4",
        "python-dotenv",
        "webargs",
    ],
    extras_require={
        "dev": [
            "black",
            "flake8",
            "flake8-import-order",
            "mypy",
            "pep8-naming",
            "pytest",
            "tox",
        ]
    },
    license="Apache Software License 2.0",
)
