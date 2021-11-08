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
        "sqlalchemy[asyncio,aiosqlite]",
        "rich",
        "requests",
    ],
    extras_require={
        "testing": ["pytest", "pytest-cov", "sqlalchemy[mypy]"],
        "docs": [
            "sphinx",
            "autodoc_pydantic",
            "sphinx-rtd-theme",
            "myst_parser",
            "autoapi",
        ],
    },
    entry_points={
        "console_scripts": [
            "modak = MODAK.cli:modak",
            "modak-validate-json = MODAK.cli:validate_json",
            "modak-schema = MODAK.cli:schema",
            "modak-import-script = MODAK.cli:import_script",
            "modak-dbshell = MODAK.cli:dbshell",
        ],
    },
)
