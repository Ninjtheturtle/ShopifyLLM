from setuptools import setup, find_packages

with open("docs/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="shopify-llm-store-creator",
    version="1.0.0",
    author="Ninjtheturtle",
    description="AI-powered Shopify store creator with web interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "flask>=2.0.0",
        "flask-cors>=3.0.0",
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
        "shopify-python-api>=12.0.0",
        "transformers>=4.20.0",
        "torch>=1.12.0",
        "datasets>=2.0.0",
        "peft>=0.3.0",
        "accelerate>=0.20.0",
        "bitsandbytes>=0.39.0",
        "trl>=0.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
        ],
    },
    entry_points={
        "console_scripts": [
            "shopify-llm=api.app:main",
        ],
    },
)
