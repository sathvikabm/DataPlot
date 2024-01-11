from setuptools import setup, find_packages

# Since in dockerfile upgrade pip setuptools wheel is present need to define a setup.py file
setup(
    name="app",
    version="1.0",
    long_description=__doc__,
    packages=find_packages(
        include=["app"],
    ),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask"],
    entry_points={
        "console_scripts": [
            "run-app = app:main",
        ]
    },
)
