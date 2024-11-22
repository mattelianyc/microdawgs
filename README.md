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