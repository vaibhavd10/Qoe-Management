import React from 'react'
import { useQuery } from 'react-query'
import { Link } from 'react-router-dom'
import { 
  FolderOpen, 
  FileText, 
  CheckSquare, 
  TrendingUp,
  Clock,
  AlertCircle,
  Plus
} from 'lucide-react'
import { projectsApi } from '../services/api'
import { useAuthStore } from '../stores/authStore'
import { DashboardMetrics, Project } from '../types'

const Dashboard: React.FC = () => {
  const { user } = useAuthStore()

  const { data: metrics, isLoading: metricsLoading } = useQuery<DashboardMetrics>(
    'dashboard-metrics',
    projectsApi.getDashboardOverview
  )

  const { data: recentProjects, isLoading: projectsLoading } = useQuery<Project[]>(
    'recent-projects',
    () => projectsApi.getRecentProjects(5)
  )

  const statCards = [
    {
      name: 'Total Projects',
      value: metrics?.total_projects || 0,
      icon: FolderOpen,
      color: 'bg-blue-500',
      change: '+12%',
      changeType: 'positive'
    },
    {
      name: 'Documents Processed',
      value: `${metrics?.processed_documents || 0}/${metrics?.total_documents || 0}`,
      icon: FileText,
      color: 'bg-green-500',
      change: '+5%',
      changeType: 'positive'
    },
    {
      name: 'Adjustments Reviewed',
      value: `${metrics?.reviewed_adjustments || 0}/${metrics?.total_adjustments || 0}`,
      icon: CheckSquare,
      color: 'bg-yellow-500',
      change: '+8%',
      changeType: 'positive'
    },
    {
      name: 'Completion Rate',
      value: `${Math.round(metrics?.avg_completion_percentage || 0)}%`,
      icon: TrendingUp,
      color: 'bg-purple-500',
      change: '+3%',
      changeType: 'positive'
    }
  ]

  if (metricsLoading) {
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
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Welcome back, {user?.full_name}</p>
        </div>
        <Link
          to="/projects"
          className="btn btn-primary"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Project
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((item) => {
          const Icon = item.icon
          return (
            <div key={item.name} className="card">
              <div className="flex items-center">
                <div className={`flex-shrink-0 ${item.color} p-3 rounded-lg`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <div className="ml-4">
                  <div className="text-sm font-medium text-gray-500">{item.name}</div>
                  <div className="text-2xl font-bold text-gray-900">{item.value}</div>
                </div>
              </div>
              <div className="mt-4 flex items-center text-sm">
                <span className={`text-${item.changeType === 'positive' ? 'green' : 'red'}-600 flex items-center`}>
                  {item.change}
                </span>
                <span className="text-gray-500 ml-2">from last month</span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Recent Projects */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Projects</h3>
          {projectsLoading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            </div>
          ) : (
            <div className="space-y-3">
              {recentProjects?.map((project) => (
                <div key={project.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="h-8 w-8 bg-primary-100 rounded-lg flex items-center justify-center">
                      <FolderOpen className="h-4 w-4 text-primary-600" />
                    </div>
                    <div>
                      <Link 
                        to={`/projects/${project.id}`}
                        className="text-sm font-medium text-gray-900 hover:text-primary-600"
                      >
                        {project.name}
                      </Link>
                      <p className="text-xs text-gray-500">{project.client_name}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-900">
                      {Math.round(project.completion_percentage)}%
                    </div>
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-primary-600 h-2 rounded-full" 
                        style={{ width: `${project.completion_percentage}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
              {(!recentProjects || recentProjects.length === 0) && (
                <div className="text-center py-8 text-gray-500">
                  No recent projects found
                </div>
              )}
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <Link
              to="/projects"
              className="flex items-center p-3 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors"
            >
              <FolderOpen className="h-5 w-5 text-primary-600 mr-3" />
              <span className="text-sm font-medium text-primary-700">Create New Project</span>
            </Link>
            <Link
              to="/documents"
              className="flex items-center p-3 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
            >
              <FileText className="h-5 w-5 text-green-600 mr-3" />
              <span className="text-sm font-medium text-green-700">Upload Documents</span>
            </Link>
            <Link
              to="/adjustments"
              className="flex items-center p-3 bg-yellow-50 rounded-lg hover:bg-yellow-100 transition-colors"
            >
              <CheckSquare className="h-5 w-5 text-yellow-600 mr-3" />
              <span className="text-sm font-medium text-yellow-700">Review Adjustments</span>
            </Link>
            <Link
              to="/questions"
              className="flex items-center p-3 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
            >
              <AlertCircle className="h-5 w-5 text-purple-600 mr-3" />
              <span className="text-sm font-medium text-purple-700">Answer Questions</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Activity Feed */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          <div className="flex items-center space-x-3">
            <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
              <FileText className="h-4 w-4 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-900">New document uploaded to Project Alpha</p>
              <p className="text-xs text-gray-500">2 hours ago</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
              <CheckSquare className="h-4 w-4 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-900">5 adjustments reviewed in Project Beta</p>
              <p className="text-xs text-gray-500">4 hours ago</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="h-8 w-8 bg-yellow-100 rounded-full flex items-center justify-center">
              <Clock className="h-4 w-4 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-900">AI processing completed for Trial Balance</p>
              <p className="text-xs text-gray-500">6 hours ago</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard