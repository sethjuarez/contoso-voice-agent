from setuptools import setup, find_packages

setup(
    name="realtime_chat",
    version="0.1.0",
    description="Realtime chat API with voice capabilities",
    author="Azure AI",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "azure-core",
        "python-dotenv",
        "jinja2",
        "pydantic",
        "opentelemetry-instrumentation",
        "opentelemetry-instrumentation-fastapi",
        "prompty", # Add specific version once known
        "rtclient" # Add specific version once known
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'pytest-asyncio>=0.21.0',
            'black>=24.0.0',
            'mypy>=1.8.0',  
            'isort>=5.13.0',
            'flake8>=7.0.0'
        ],
        'test': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'pytest-asyncio>=0.21.0'
        ]
    },
    package_data={
        'realtime_chat': [
            'config/*.json',
            'chat/*.prompty',
            'chat/*.json',
            'chat/*.jpg',
            'suggestions/*.prompty',
            'suggestions/*.json',
            'call/*.jinja2'
        ],
    }
)