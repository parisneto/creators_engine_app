## 6. Deployment & Environment

### Containerization with Docker

The application is designed to be deployed using **Docker**, ensuring consistency and reproducibility across different environments. This is evidenced by the presence of several Docker-related files within the project:

*   **`Dockerfile.dev` (located in `.devcontainer/` and `dev-ci/`) and `Dockerfile.prod` (located in `.devcontainer/`):** These files define the Docker image configurations tailored for development and production environments, respectively. This separation allows for environment-specific dependencies, tools, or settings. For instance, development containers might include debugging tools or different data mounting strategies, while production containers are optimized for performance and security. There is also a `Dockerfile copy.prod` in `.devcontainer/` which might be a backup or variant.
*   **`docker-compose.yml`:** This file is used to define and manage multi-container Docker applications. It simplifies the setup and orchestration of the application and any supporting services (like databases or other backend components, though not explicitly detailed for this application).
*   **`.dockerignore`:** This file specifies intentionally untracked files and directories that should be excluded from the Docker build context. This helps in creating smaller, more efficient Docker images by omitting unnecessary files like local development configurations, caches, or documentation.
*   **Cloud Build Configuration (`cloudbuild.yaml`):** The presence of `cloudbuild.yaml` suggests that Google Cloud Build is likely used as part of the CI/CD pipeline for building Docker images and potentially deploying the application, particularly in a Google Cloud environment. Specific Cloud Build configurations for development (`dev-ci/cloudbuild.dev-app.yaml`, `dev-ci/cloudbuild.dev-base.yaml`) further underscore a sophisticated, automated build process.

Containerization via Docker ensures that the application runs in a predictable and isolated environment, from a developer's machine to staging and production systems.

### Environment Configuration (`APPMODE`)

A crucial environment variable, **`APPMODE`**, plays a significant role in tailoring the application's behavior to the specific deployment context (development, production, etc.):

*   **`APPMODE = "DEV"`:** When this variable is set to "DEV", the application activates development-specific configurations. A key example, observed in `utils/dataloader.py`, is the adjustment of data loading paths to point to local development directories (e.g., `/app/data/` or a user-defined `DEV_DATA_DIR`). This mode is intended for local development, debugging, and testing.
*   **Production Mode (e.g., `APPMODE` not set to "DEV", or explicitly set to "PROD" or another value):** In a production or non-development setting, the application defaults to configurations suitable for a deployed environment. For data loading, this means using relative paths (e.g., `data/`) that are expected to be structured within the deployed application package or a mounted volume.

This `APPMODE` mechanism allows the same codebase to operate correctly across different environments without requiring code modifications. It externalizes environment-specific settings, ensuring that data sources, API endpoints, or feature flags can be managed appropriately for each stage of the deployment lifecycle. Other parts of the application may also key off this variable for different behaviors or settings. The `startup.sh` script likely plays a role in setting or utilizing this environment variable when the application starts.
