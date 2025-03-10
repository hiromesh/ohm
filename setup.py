import subprocess
from pathlib import Path

from setuptools import Command, find_packages, setup


class InstallMermaidCLI(Command):
    description = "install mermaid-cli"
    user_options = []

    def run(self):
        try:
            subprocess.check_call(["npm", "install", "-g", "@mermaid-js/mermaid-cli"])
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e.output}")


here = Path(__file__).resolve().parent
long_description = (here / "README.md").read_text(encoding="utf-8")
requirements = (here / "requirements.txt").read_text(encoding="utf-8").splitlines()


extras_require = {
    "selenium": ["selenium>4", "webdriver_manager", "beautifulsoup4"],
    "search-google": ["google-api-python-client==2.94.0"],
    "search-ddg": ["duckduckgo-search~=4.1.1"],
}


setup(
    name="ohm",
    version="0.1.0",
    description="The Multi-Agent Framework for game development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hiro/ohm",
    author="Hiro",
    author_email="hiromesh@qq.com",
    license="Apache-2.0",
    keywords="ohm game development",
    packages=find_packages(exclude=["contrib", "docs", "examples", "tests*"]),
    python_requires=">=3.9, <3.12",
    install_requires=requirements,
    extras_require=extras_require,
    cmdclass={
        "install_mermaid": InstallMermaidCLI,
    },
    entry_points={
        "console_scripts": [
            "ohm=ohm.software_company:app",
        ],
    },
    include_package_data=True,
)
