# JobFind

JobFind is a web application designed to facilitate job searching and networking. It provides features for job listings, direct messaging, notifications, and user profiles.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact Information](#contact-information)
- [Acknowledgments](#acknowledgments)

## Installation

To set up the project locally using Docker, follow these steps:

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd JobFind
   ```
3. Build and start the Docker containers:
   ```bash
   docker-compose up -d
   ```
   This command will build the Docker images and start the containers in detached mode.

4. Access the application:
   - The web application will be available at `http://localhost:5001`.
   - The MySQL database will be accessible on port `3307`.

## Usage

To stop the application, use the following command:

```bash
docker-compose down
```

This command will stop and remove the containers.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/YourFeature
   ```
3. Make your changes and commit them:
   ```bash
   git commit -m "Add your message"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/YourFeature
   ```
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact Information

For any inquiries, please contact [Erdison Malko](mailto:erdisonmalko@gmail.com).

## Acknowledgments

- Thanks to all contributors and open-source projects that made this project possible.
