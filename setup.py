from setuptools import setup, find_packages
setup(
    name="Mechgram",
    version="1.1",
    description="Unique library for creating Telegram bots with fluent interface ",
    author="MEMozki",
    author_email="memerz@list.ru",
    packages=find_packages(),
    install_requires=[
        "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
