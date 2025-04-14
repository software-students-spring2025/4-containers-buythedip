![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)
![ML Client Build & Test](https://github.com/software-students-spring2025/4-containers-buythedip/actions/workflows/ml_client.yml/badge.svg)
![Web App Build & Test](https://github.com/software-students-spring2025/4-containers-buythedip/actions/workflows/web_app.yml/badge.svg)

# Documentation

This app allows users to capture images using a webcam. A separate ML client
identifies the fruit in the image and reads out the identification, assisting
visually impaired users or kids who are in the process of learning which fruits are what.

## Installation

### Running on Any Platform
Windows: Use PowerShell, ensure `pip` and `git` are installed. <br />
macOS: Use Terminal, ensure `brew` or `pip` is updated. <br />
Linux: Use `bash`, ensure `python3` and `pipenv` are installed.


## Usage Guide

### 1. Set Up a Virtual Environment
```
python3 -m venv buythedip
source buythedip/bin/activate
```

### 2. Install Dependencies
pip install all of these packages:
```
pip3 install opencv-python
pip3 install flask
pip3 install numpy
pip3 install pymongo
pip3 install mongomock
pip3 install tensorflow
pip3 install python-dotenv
python3 -m pip install coverage
pip3 install pytest
```

Copy the provided `env.example` file to `.env` in the project root, then register with the Merriam-Webster API and replace the `MW_API_KEY` with your actual key (or check the buythedip team channel on Discord for it). This ensures your secrets remain local and are not stored in version control.

To downlaod and setup docker:
```
brew install docker-compose         # download docker for macOS
sudo apt install docker-compose     # download docker for Windows

docker-compose up --build           # run the docker containers
```

### 3. Run Tests
Ensure everything works - make sure you are in the correct directories before running these commands:
```
# For tests:

pytest

# For coverage:

coverage run -m pytest
coverage report
```

## Team Members
[Mahmoud Shehata](https://github.com/MahmoudS1201) <br /> 
[Patrick Cao](https://github.com/Novrain7) <br />
[Chris Leu](https://github.com/cl3880) <br />
[Syed Naqvi](https://github.com/syed1naqvi)

## Task Board
[🔗 Click Here](https://github.com/orgs/software-students-spring2025/projects/202/views/1)

## License
This project is licensed under the GNU General Public License. See the [LICENSE](https://github.com/software-students-spring2025/4-containers-buythedip/blob/main/LICENSE) file for details.