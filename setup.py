from setuptools import setup, find_packages
setup(
    name="mechgram",
    version="1.2.2",
    description="Telegram bot api via requests",
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
