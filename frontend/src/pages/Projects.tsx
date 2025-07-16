import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { Link } from 'react-router-dom'
import { 
  Plus, 
  Search, 
  FolderOpen, 
  Calendar,
  User,
  TrendingUp,
  MoreHorizontal,
  Edit,
  Trash2
} from 'lucide-react'
import { projectsApi } from '../services/api'
import { Project } from '../types'
import toast from 'react-hot-toast'

const Projects: React.FC = () => {
  const queryClient = useQueryClient()
  const [searchTerm, setSearchTerm] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)

  const { data: projects, isLoading } = useQuery<Project[]>(
    'projects',
    projectsApi.getProjects
  )

  const createMutation = useMutation(projectsApi.createProject, {
    onSuccess: () => {
      queryClient.invalidateQueries('projects')
      setShowCreateModal(false)
      toast.success('Project created successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create project')
    }
  })

  const deleteMutation = useMutation(projectsApi.deleteProject, {
    onSuccess: () => {
      queryClient.invalidateQueries('projects')
      toast.success('Project deleted successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete project')
    }
  })

  const filteredProjects = projects?.filter(project =>
    project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    project.client_name.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  const handleCreateProject = (formData: any) => {
    createMutation.mutate(formData)
  }

  const handleDeleteProject = (projectId: number) => {
    if (window.confirm('Are you sure you want to delete this project?')) {
      deleteMutation.mutate(projectId)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'completed': return 'bg-blue-100 text-blue-800'
      case 'on_hold': return 'bg-yellow-100 text-yellow-800'
      case 'archived': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
          <p className="text-gray-600">Manage your QoE analysis projects</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn btn-primary"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Project
        </button>
      </div>

      {/* Search and filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search projects..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="form-input pl-10"
          />
        </div>
        <select className="form-input w-full sm:w-auto">
          <option>All Status</option>
          <option>Active</option>
          <option>Completed</option>
          <option>On Hold</option>
          <option>Archived</option>
        </select>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProjects.map((project) => (
          <div key={project.id} className="card hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <FolderOpen className="h-5 w-5 text-primary-600" />
                </div>
                <div>
                  <Link 
                    to={`/projects/${project.id}`}
                    className="text-lg font-medium text-gray-900 hover:text-primary-600"
                  >
                    {project.name}
                  </Link>
                  <p className="text-sm text-gray-500">{project.client_name}</p>
                </div>
              </div>
              <div className="relative">
                <button
                  onClick={() => setSelectedProject(project)}
                  className="p-1 rounded-md hover:bg-gray-100"
                >
                  <MoreHorizontal className="h-4 w-4 text-gray-400" />
                </button>
              </div>
            </div>

            <div className="mt-4">
              <div className="flex items-center justify-between mb-2">
                <span className={`badge ${getStatusColor(project.status)}`}>
                  {project.status.replace('_', ' ')}
                </span>
                <span className="text-sm text-gray-500">
                  {Math.round(project.completion_percentage)}% complete
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-primary-600 h-2 rounded-full" 
                  style={{ width: `${project.completion_percentage}%` }}
                ></div>
              </div>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center text-gray-500">
                <Calendar className="h-4 w-4 mr-2" />
                {new Date(project.created_at).toLocaleDateString()}
              </div>
              <div className="flex items-center text-gray-500">
                <User className="h-4 w-4 mr-2" />
                {project.total_documents} docs
              </div>
              <div className="flex items-center text-gray-500">
                <TrendingUp className="h-4 w-4 mr-2" />
                {project.total_adjustments} adjustments
              </div>
              <div className="flex items-center text-gray-500">
                <FolderOpen className="h-4 w-4 mr-2" />
                {project.reviewed_adjustments} reviewed
              </div>
            </div>

            <div className="mt-4 flex space-x-2">
              <Link
                to={`/projects/${project.id}`}
                className="btn btn-outline flex-1"
              >
                View Details
              </Link>
              <button
                onClick={() => handleDeleteProject(project.id)}
                className="btn btn-outline text-red-600 border-red-300 hover:bg-red-50"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredProjects.length === 0 && (
        <div className="text-center py-12">
          <FolderOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No projects found</h3>
          <p className="text-gray-500 mb-6">
            {searchTerm ? 'No projects match your search criteria.' : 'Get started by creating your first project.'}
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn btn-primary"
          >
            <Plus className="h-4 w-4 mr-2" />
            Create Project
          </button>
        </div>
      )}

      {/* Create Project Modal */}
      {showCreateModal && (
        <CreateProjectModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateProject}
          isLoading={createMutation.isLoading}
        />
      )}
    </div>
  )
}

// Create Project Modal Component
const CreateProjectModal: React.FC<{
  onClose: () => void
  onSubmit: (data: any) => void
  isLoading: boolean
}> = ({ onClose, onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    name: '',
    client_name: '',
    description: '',
    materiality_threshold: 1000,
    materiality_percentage: 0.03
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name.includes('materiality') ? Number(value) : value
    }))
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Create New Project</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="form-label">Project Name</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className="form-input"
              required
            />
          </div>

          <div>
            <label className="form-label">Client Name</label>
            <input
              type="text"
              name="client_name"
              value={formData.client_name}
              onChange={handleChange}
              className="form-input"
              required
            />
          </div>

          <div>
            <label className="form-label">Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              className="form-input"
              rows={3}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="form-label">Materiality Threshold ($)</label>
              <input
                type="number"
                name="materiality_threshold"
                value={formData.materiality_threshold}
                onChange={handleChange}
                className="form-input"
                min="0"
              />
            </div>
            <div>
              <label className="form-label">Materiality % (0-1)</label>
              <input
                type="number"
                name="materiality_percentage"
                value={formData.materiality_percentage}
                onChange={handleChange}
                className="form-input"
                min="0"
                max="1"
                step="0.01"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-outline"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="btn btn-primary"
            >
              {isLoading ? 'Creating...' : 'Create Project'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Projects