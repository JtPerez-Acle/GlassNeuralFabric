from setuptools import setup, find_packages

setup(
    name="neurospace-bridge",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "torch>=1.13.0",
        "requests>=2.28.0",
    ],
    author="NeuroSpark Team",
    author_email="team@neurospark.ai",
    description="Bridge for capturing neural network state during training",
    keywords="neural network, visualization, monitoring",
    url="https://github.com/neurospark/neurospace-time",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
)
