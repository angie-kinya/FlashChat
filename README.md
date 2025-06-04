# FlashChat
This is a real-time chat application backend built with Flask, Socket.IO, and Docker.

# Getting Started
1. Clone and Initialize Project
```bash
git clone https://github.com/angie-kinya/FlashChat.git
cd flashchat
```

2. Setup Environment
```bash
cp .env.example .env
# Edit .env with your configurations
```

3. Install Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt # tailored for tests
```

4. Initialize Database
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. Run Development Server
```bash
python run.py
```

6. Run with Docker
```bash
docker-compose up --build
```

# Next Steps
Tests are currently ongoing for this project. Once complete, they will be added to the project.

CI/CD workflow will be added when tests are complete and production build is ready.

Feel free to reach out for collaborations and contributions to this project.

# License
This project is licensed under the [MIT License](LICENSE).