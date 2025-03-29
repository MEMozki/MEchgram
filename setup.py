from setuptools import setup, find_packages
setup(
    name="MEchgram",
    version="2.0.1",
    description="Telegram bot api via requests",
    url="https://github.com/MEMozki/MEchgram",
    author="MEMozki",
    author_email="memerz@list.ru",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "requests",
        "asyncio"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
