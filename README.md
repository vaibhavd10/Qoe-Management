# QoE Automation Platform - MVP

A comprehensive Quality of Earnings automation platform built with FastAPI, React, and LangGraph for AI-powered financial analysis.

## Project Structure

```
qoe-automation-platform/
├── backend/                 # Python FastAPI backend
│   ├── app/                # Main application code
│   ├── alembic/            # Database migrations
│   ├── tests/              # Backend tests
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Backend container
├── frontend/              # React frontend
│   ├── src/               # Source code
│   ├── public/            # Static assets
│   ├── package.json       # Node dependencies
│   └── Dockerfile         # Frontend container
├── docker-compose.yml     # Local development setup
├── .env.example          # Environment variables template
├── .github/              # CI/CD workflows
└── docs/                 # Documentation
```

## Features

- **Document Ingestion**: Upload and process Excel, CSV, DOCX, PDF files
- **AI-Powered Adjustments**: 28+ rule-based adjustments with LangGraph workflows
- **Review Canvas**: Interactive adjustment review and approval
- **Questionnaire System**: Dynamic Q&A generation and management
- **Report Generation**: Excel Data Books and Word/PDF reports
- **Role-Based Access**: Admin and Analyst user roles
- **Project Workspace**: Comprehensive dashboard and navigation

## Quick Start

1. Copy environment variables: `cp .env.example .env`
2. Start services: `docker-compose up -d`
3. Run migrations: `docker-compose exec backend alembic upgrade head`
4. Access the app: http://localhost:3000

See the full [RUNBOOK](docs/RUNBOOK.md) for detailed setup instructions. 
