from setuptools import setup, find_packages

setup(
    name = "jpio",
    packages = find_packages(),
    version = "0.2.0",
    description = "Json Python I/O",
    author = "Eric Ng",
    author_email = "ericnjf@gmail.com",
    url = "https://github.com/zwodahs/jpio",
    keywords = ["json", "commandline"],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Programming Language :: Python :: 3 :: Only",
    ],
    entry_points = {
        "console_scripts": [
            "jpio=jpio.run_time:main",
        ]
    },
)

