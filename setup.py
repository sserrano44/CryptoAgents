"""
Setup script for the CryptoAgents package.
"""

from setuptools import setup, find_packages

setup(
    name="cryptoagents",
    version="0.1.0",
    description="Multi-Agents LLM Financial Trading Framework",
    author="Sebastian Serrano",
    author_email="sebastian@ripio.com",
    url="https://github.com/sserrano44/CryptoAgents.git",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.1.0",
        "langchain-openai>=0.0.2",
        "langchain-experimental>=0.0.40",
        "langgraph>=0.0.20",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "praw>=7.7.0",
        "stockstats>=0.5.4",
        "yfinance>=0.2.31",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "questionary>=2.0.1",
        "chromadb>=1.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "cryptoagents=cli.main:app",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Trading Industry",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
)
