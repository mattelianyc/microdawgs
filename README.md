# AI Image Generation Microservices

A scalable microservices architecture for AI-powered image generation, supporting icons and splash images with style transfer and layout control.

## Architecture Overview

The system consists of the following main components:

- **Gateway Service**: API gateway handling request routing and authentication
- **Icon Service**: Specialized service for icon generation
- **Splash Service**: Service for splash image generation with layout control
- **Training Pipeline**: Model training and fine-tuning infrastructure
- **Frontend**: React-based user interface

## Services

### Gateway Service
- Request routing and load balancing
- Authentication and rate limiting
- Request validation and preprocessing

### Icon Service
- Icon generation using SDXL
- Style transfer capabilities
- Layout control for consistent icon design

### Splash Service
- Splash image generation
- IP-Adapter for reference-based generation
- Layout and composition control
- Style influence management

### Training Pipeline
- Model fine-tuning infrastructure
- Data preprocessing and augmentation
- Model evaluation and metrics tracking

## Setup and Installation

1. Clone the repository: 

## Troubleshooting

If you encounter a "Connection refused" error when the gateway service tries to connect to the icon service, try the following:

1. Verify that the icon service is running and healthy. Check the service logs for any errors during startup or operation.

2. Ensure the icon service is accessible at the expected `icon-service:8001` host and port. Confirm the service name matches the Docker Compose service definition.

3. Check the gateway service configuration to make sure it's using the correct URL for the icon service. Look for any discrepancies in the host, port or protocol.

4. Inspect the Docker network to verify the services are attached and can communicate. Run `docker network inspect <network-name>` and look for both services in the output.

5. Temporarily disable SSL/TLS if enabled for the connection. Test with an insecure connection to isolate any certificate or encryption issues.

If the problem persists, enable debug logging in the gateway and icon services to gather more detailed information about the connection attempt and error. Refer to the service-specific documentation for instructions on adjusting log levels.