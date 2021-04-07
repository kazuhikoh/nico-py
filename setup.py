import setuptools

with open('requirements') as requirements_file:
    install_requirements = requirements_file.read().splitlines()

setuptools.setup(
    name="nico-py",
    version="1.0.0",
    description=":)",
    author="kazuhikoh",
    packages=setuptools.find_packages(),
    python_requires='>=3.7',
    install_requires=install_requirements,
    entry_points={
        "console_scripts": [
            "nico=nico:main"
        ]
    }
)
