# Application Setup

## Prerequisites

Before running the application, make sure you have the following installed:

- [Git LFS](https://git-lfs.com/)  
- [Docker](https://docs.docker.com/get-docker/)  
- [Docker Compose](https://docs.docker.com/compose/install/)  

## Installation

1. **Initialize Git LFS**  
   Git LFS is required to download large files needed for the application to work correctly. Its only 60 mb file
   ```bash
   git lfs install
   
2. **Clone the repository**
   ```bash
   git clone git@github.com:m-lejwoda/recruitment_task.git
   cd recruitment_task
3. **Run application**
    ```bash
    docker-compose -f local.yml up --build
