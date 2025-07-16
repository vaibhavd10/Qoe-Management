# QoE Automation Platform - MVP

A comprehensive Quality of Earnings (QoE) automation platform built with FastAPI, React, and AI-powered document processing.

## 🚀 Quick Start - Local Development

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- Git

### 1. Clone and Setup

```bash
git clone <repository-url>
cd qoe-automation-platform
```

### 2. Environment Configuration

Create environment files:

```bash
# Backend environment
cp backend/.env.example backend/.env

# Frontend environment
cp frontend/.env.example frontend/.env
```

### 3. Start All Services

```bash
# Start all services with Docker Compose
docker-compose up --build

# Or start in detached mode
docker-compose up --build -d
```

This will start:
- PostgreSQL database (port 5432)
- Redis (port 6379)
- Backend API (port 8000)
- Frontend (port 3000)
- Celery worker
- Celery beat scheduler
- Flower (Celery monitoring) (port 5555)

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Flower (Celery)**: http://localhost:5555

### 5. Default Login Credentials

```
Admin User:
- Email: admin@qoe-platform.com
- Password: admin123

Analyst User:
- Email: analyst@qoe-platform.com
- Password: analyst123
```

## 📁 Project Structure

```
qoe-automation-platform/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── ai/                # AI workflows and LangGraph
│   │   │   └── adjustment_workflow.py
│   │   ├── core/              # Core configuration
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   └── deps.py
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── document.py
│   │   │   ├── adjustment.py
│   │   │   ├── question.py
│   │   │   └── report.py
│   │   ├── routers/           # FastAPI routers
│   │   │   ├── auth.py
│   │   │   ├── projects.py
│   │   │   ├── documents.py
│   │   │   ├── adjustments.py
│   │   │   ├── questions.py
│   │   │   └── reports.py
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   ├── tasks/             # Celery tasks
│   │   └── main.py
│   ├── alembic/               # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── Layout.tsx
│   │   │   ├── AuthLayout.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   ├── pages/             # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Login.tsx
│   │   │   ├── Projects.tsx
│   │   │   ├── Documents.tsx
│   │   │   ├── Adjustments.tsx
│   │   │   ├── Questions.tsx
│   │   │   ├── Reports.tsx
│   │   │   └── Settings.tsx
│   │   ├── services/          # API services
│   │   │   └── api.ts
│   │   ├── stores/            # State management
│   │   │   └── authStore.ts
│   │   ├── types/             # TypeScript types
│   │   │   └── index.ts
│   │   ├── utils/             # Utility functions
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔧 Development Commands

### Backend Development

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run Celery worker
celery -A app.tasks.document_tasks worker --loglevel=info

# Run Celery beat scheduler
celery -A app.tasks.document_tasks beat --loglevel=info
```

### Frontend Development

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Database Commands

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Reset database
docker-compose down -v
docker-compose up -d postgres redis
```

## 🧪 Testing the System

### 1. Create a Project

1. Login with admin credentials
2. Navigate to Projects → Create New Project
3. Fill in project details and save

### 2. Upload Documents

1. Go to Documents page
2. Drag and drop or browse files (Excel, CSV, PDF, Word)
3. Files will be automatically processed

### 3. Review AI Adjustments

1. Navigate to Adjustments page
2. Review AI-generated adjustments
3. Accept, reject, or modify adjustments

### 4. Answer Questions

1. Go to Questions page
2. Answer AI-generated questions
3. Provide context and clarifications

### 5. Generate Reports

1. Navigate to Reports page
2. Generate Excel, Word, or PDF reports
3. Download completed reports

## 🎯 Key Features

### AI-Powered Analysis
- **LangGraph Workflow**: 28+ adjustment rules with AI narrative generation
- **Document Classification**: Automatic document type detection
- **Confidence Scoring**: AI confidence levels for all adjustments
- **Question Generation**: Smart Q&A based on document analysis

### Document Processing
- **Multi-format Support**: Excel, CSV, PDF, Word documents
- **Async Processing**: Celery-based background processing
- **Progress Tracking**: Real-time processing status
- **Metadata Extraction**: Automatic row/column counting

### Review Canvas
- **Adjustment Review**: Accept, reject, or modify AI suggestions
- **Comments & Notes**: Add reviewer comments and context
- **Materiality Analysis**: Automatic materiality flagging
- **Audit Trail**: Complete history of all changes

### Role-Based Access
- **Admin Role**: Full system access and user management
- **Analyst Role**: Project work and review capabilities
- **Authentication**: JWT-based secure authentication
- **Permissions**: Granular access control

### Report Generation
- **Multiple Formats**: Excel databooks, Word reports, PDF exports
- **Customizable**: Include/exclude sections as needed
- **Professional**: Formatted reports ready for client delivery
- **Download**: Secure file download with proper headers

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Primary database
- **Redis**: Caching and Celery broker
- **Celery**: Background task processing
- **LangChain**: AI framework integration
- **LangGraph**: AI workflow orchestration
- **OpenAI**: Large language model integration

### Frontend
- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe development
- **TailwindCSS**: Utility-first styling
- **Zustand**: State management
- **React Query**: Data fetching and caching
- **React Router**: Client-side routing
- **Lucide React**: Icon library

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy (production)
- **Alembic**: Database migrations

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Current user info
- `POST /api/auth/refresh` - Refresh token

### Projects
- `GET /api/projects` - List projects
- `POST /api/projects` - Create project
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

### Documents
- `GET /api/documents` - List documents
- `POST /api/documents/upload` - Upload document
- `GET /api/documents/{id}` - Get document details
- `GET /api/documents/{id}/download` - Download document
- `POST /api/documents/{id}/process` - Process document

### Adjustments
- `GET /api/adjustments` - List adjustments
- `POST /api/adjustments` - Create adjustment
- `GET /api/adjustments/{id}` - Get adjustment details
- `POST /api/adjustments/{id}/review` - Review adjustment
- `PUT /api/adjustments/{id}` - Update adjustment

### Questions
- `GET /api/questions` - List questions
- `POST /api/questions` - Create question
- `POST /api/questions/{id}/answer` - Answer question
- `GET /api/questions/{id}` - Get question details

### Reports
- `GET /api/reports` - List reports
- `POST /api/reports/generate` - Generate report
- `GET /api/reports/{id}/download` - Download report

## 🔄 Workflow Overview

1. **Document Upload**: Users upload financial documents
2. **AI Processing**: LangGraph workflow analyzes documents
3. **Adjustment Generation**: AI creates potential adjustments
4. **Human Review**: Analysts review and validate adjustments
5. **Q&A Generation**: AI generates clarifying questions
6. **Report Creation**: System generates final reports

## 🎨 UI Features

### Dashboard
- KPI widgets with real-time metrics
- Recent projects and activity feed
- Quick action buttons
- Progress indicators

### Document Management
- Drag-and-drop file upload
- Real-time processing status
- Document type classification
- File size and metadata display

### Adjustment Review
- Tabular view with filtering
- Confidence score indicators
- Review status tracking
- Bulk operations

### Q&A Interface
- Question prioritization
- Multiple answer types
- Context preservation
- Due date tracking

### Report Generation
- Template selection
- Section customization
- Progress tracking
- Download management

## 🚀 Next Steps

This MVP provides a solid foundation for QoE automation. Key areas for enhancement:

1. **Advanced AI**: More sophisticated adjustment rules and patterns
2. **Integration**: Connect with accounting systems and data sources
3. **Collaboration**: Team features and workflow approvals
4. **Analytics**: Advanced reporting and dashboard insights
5. **Security**: Enhanced security features and compliance
6. **Mobile**: Responsive design improvements

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For questions and support, please contact the development team. 
