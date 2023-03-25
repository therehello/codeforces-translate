import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="codeforces_translate",
    version="0.1.2",
    author="Therehello",
    author_email="therehello@qq.com",
    description="codeforces 翻译",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/therehello/codeforces-translate",
    packages=setuptools.find_packages(),
    install_requires=[
        'markdownify',
        'pygtrans',
        'bs4',
        'requests',
        'lxml'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'cf-translate = codeforces_translate.cf_translate:main'
        ]
    }
)