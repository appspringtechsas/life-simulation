"""Package configuration."""
from setuptools import setup, find_packages

setup(
    name="life-simulation",
    version="1.0.0",
    description="Autonomous agents life simulation with LLM and MCP tools",
    author="Development Team",
    author_email="dev@example.com",
    url="https://github.com/appspringtechsas/life-simulation",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": ["pytest>=6.0", "pytest-cov"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Artificial Life",
    ],
)
