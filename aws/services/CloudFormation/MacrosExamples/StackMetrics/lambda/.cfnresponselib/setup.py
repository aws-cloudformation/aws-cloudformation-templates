import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cfnresponse",
    version="1.1.2",
    author="Amazon Web Services",
    description="Send a response object to a custom resource by way of an Amazon S3 presigned URL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gene1wood/cfnresponse",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    install_requires=[
        'urllib3'
    ],
)
