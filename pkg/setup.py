import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="consistent_sampler",
    version="1.0.10",
    author="Ronald L. Rivest",
    author_email="rivest@mit.edu",
    description="Package for consistent sampling with or without replacement.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ron-rivest/consistent_sampler",
    # packages=setuptools.find_packages(),
    packages=['consistent_sampler'],
    license='MIT License',
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)

