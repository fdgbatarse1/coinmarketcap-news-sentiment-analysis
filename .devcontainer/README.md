# Dev Container for CoinMarketCap News Sentiment Analysis

This directory contains configuration files for the development container used in this project.

## How to Use

- The dev container is pre-configured for Python development.
- To add new Python packages, include them in the `requirements.in` file (if present) or the main requirements file for the project.
- The environment will automatically install packages listed in the requirements file when the container is built.

## Adding Packages

1. Open the `requirements.in` file in the project root.
2. Add the desired package(s) and version(s) as needed.
3. Rebuild the dev container to install the new dependencies.

## Additional Notes

- For more information on dev containers, see the [VS Code documentation](https://code.visualstudio.com/docs/devcontainers/containers).
- If you encounter issues, ensure your requirements files are up to date and properly formatted.
