from setuptools import setup, find_packages

setup(
    name="appoint_a_bot",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests==2.31.0",
        "pytz==2023.3",
    ],
    entry_points={
        "console_scripts": [
            "appoint-a-bot=src.appoint_a_bot.main:main",
        ],
    },
    author="Appoint-a-Bot Team",
    author_email="example@example.com",
    description="An appointment scheduling system with multiple components",
    keywords="appointment, scheduling, agent",
    python_requires=">=3.8",
) 