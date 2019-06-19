import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="enola_opencv_utils",
    version="0.0.1",
    author="Eduardo Sebastian Nola",
    author_email="edunola13@gmail.com",
    description="Utilities class and function to help with opencv",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/edunola13/opencv_utils",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
