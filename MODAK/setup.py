from setuptools import find_packages, setup

setup(
    name="MODAK",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pydantic[email]",
        "numpy",
        "pandas",
        "Flask",
        "Jinja2",
        "gunicorn",
    ],
    entry_points={
        "console_scripts": [
            "modak-validate-json = MODAK.cli:validate_json",
        ],
    },
)
