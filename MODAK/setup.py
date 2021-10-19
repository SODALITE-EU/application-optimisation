from setuptools import find_packages, setup

setup(
    name="MODAK",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pydantic[email]",
        "Jinja2",
        "fastapi",
        "uvicorn",
    ],
    extras_require={
        "testing": ["pytest", "pytest-cov"],
    },
    entry_points={
        "console_scripts": [
            "modak = MODAK.cli:validate_json",
            "modak-validate-json = MODAK.cli:validate_json",
            "modak-schema = MODAK.cli:schema",
        ],
    },
)
