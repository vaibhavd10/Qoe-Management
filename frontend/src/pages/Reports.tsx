import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { 
  FileOutput, 
  Search, 
  Download,
  Eye,
  Plus,
  File,
  FileText,
  FileSpreadsheet,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react'
import { reportsApi } from '../services/api'
import { Report } from '../types'
import toast from 'react-hot-toast'

const Reports: React.FC = () => {
  const queryClient = useQueryClient()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedType, setSelectedType] = useState<string>('all')
  const [showGenerateModal, setShowGenerateModal] = useState(false)

  const { data: reports, isLoading } = useQuery<Report[]>(
    'reports',
    reportsApi.getReports
  )

  const generateMutation = useMutation(reportsApi.generateReport, {
    onSuccess: () => {
      queryClient.invalidateQueries('reports')
      setShowGenerateModal(false)
      toast.success('Report generation started')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to generate report')
    }
  })

  const downloadMutation = useMutation(reportsApi.downloadReport, {
    onSuccess: (data, reportId) => {
      // Create blob and download
      const blob = new Blob([data], { type: 'application/octet-stream' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `report_${reportId}.zip`
      a.click()
      URL.revokeObjectURL(url)
      toast.success('Report downloaded successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to download report')
    }
  })

  const filteredReports = reports?.filter(report => {
    const matchesSearch = report.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         report.description?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = selectedType === 'all' || report.report_type === selectedType
    return matchesSearch && matchesType
  }) || []

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800'
      case 'generating': return 'bg-blue-100 text-blue-800'
      case 'error': return 'bg-red-100 text-red-800'
      default: return 'bg-yellow-100 text-yellow-800'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'excel_databook': return <FileSpreadsheet className="h-5 w-5" />
      case 'word_report': return <FileText className="h-5 w-5" />
      case 'pdf_report': return <File className="h-5 w-5" />
      default: return <FileOutput className="h-5 w-5" />
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const handleGenerateReport = (reportData: any) => {
    generateMutation.mutate(reportData)
  }

  const handleDownloadReport = (reportId: number) => {
    downloadMutation.mutate(reportId)
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
          <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
          <p className="text-gray-600">Generate and download analysis reports</p>
        </div>
        <button
          onClick={() => setShowGenerateModal(true)}
          className="btn btn-primary"
        >
          <Plus className="h-4 w-4 mr-2" />
          Generate Report
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-blue-500 rounded-lg">
              <FileOutput className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Total Reports</p>
              <p className="text-2xl font-bold text-gray-900">
                {reports?.length || 0}
              </p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-green-500 rounded-lg">
              <CheckCircle className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Completed</p>
              <p className="text-2xl font-bold text-gray-900">
                {reports?.filter(r => r.status === 'completed').length || 0}
              </p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-500 rounded-lg">
              <Clock className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Generating</p>
              <p className="text-2xl font-bold text-gray-900">
                {reports?.filter(r => r.status === 'generating').length || 0}
              </p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-red-500 rounded-lg">
              <AlertCircle className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Errors</p>
              <p className="text-2xl font-bold text-gray-900">
                {reports?.filter(r => r.status === 'error').length || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search reports..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="form-input pl-10"
          />
        </div>
        <select 
          className="form-input w-full sm:w-auto"
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
        >
          <option value="all">All Types</option>
          <option value="excel_databook">Excel Databook</option>
          <option value="word_report">Word Report</option>
          <option value="pdf_report">PDF Report</option>
          <option value="summary_report">Summary Report</option>
        </select>
      </div>

      {/* Reports Table */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Report
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Size
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Generated
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredReports.map((report) => (
                <tr key={report.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="text-gray-400 mr-3">
                        {getTypeIcon(report.report_type)}
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {report.title}
                        </div>
                        <div className="text-sm text-gray-500">
                          {report.description}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="badge bg-blue-100 text-blue-800">
                      {report.report_type.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {report.file_size ? formatFileSize(report.file_size) : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className={`badge ${getStatusColor(report.status)}`}>
                        {report.status}
                      </span>
                      {report.status === 'generating' && (
                        <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                          <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {report.generated_at ? new Date(report.generated_at).toLocaleDateString() : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex items-center space-x-2">
                      <button
                        className="text-blue-600 hover:text-blue-800"
                        title="View"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      {report.status === 'completed' && (
                        <button
                          onClick={() => handleDownloadReport(report.id)}
                          className="text-green-600 hover:text-green-800"
                          title="Download"
                          disabled={downloadMutation.isLoading}
                        >
                          <Download className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredReports.length === 0 && (
          <div className="text-center py-12">
            <FileOutput className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No reports found</h3>
            <p className="text-gray-500 mb-6">
              {searchTerm ? 'No reports match your search criteria.' : 'Generate your first report to get started.'}
            </p>
            <button
              onClick={() => setShowGenerateModal(true)}
              className="btn btn-primary"
            >
              <Plus className="h-4 w-4 mr-2" />
              Generate Report
            </button>
          </div>
        )}
      </div>

      {/* Generate Report Modal */}
      {showGenerateModal && (
        <GenerateReportModal
          onClose={() => setShowGenerateModal(false)}
          onSubmit={handleGenerateReport}
          isLoading={generateMutation.isLoading}
        />
      )}
    </div>
  )
}

// Generate Report Modal Component
const GenerateReportModal: React.FC<{
  onClose: () => void
  onSubmit: (data: any) => void
  isLoading: boolean
}> = ({ onClose, onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    report_type: 'excel_databook',
    project_id: '',
    include_adjustments: true,
    include_questions: true,
    include_documents: true
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }))
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Generate Report</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="form-label">Report Title</label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              className="form-input"
              required
              placeholder="Enter report title"
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
              placeholder="Describe this report"
            />
          </div>

          <div>
            <label className="form-label">Report Type</label>
            <select
              name="report_type"
              value={formData.report_type}
              onChange={handleChange}
              className="form-input"
            >
              <option value="excel_databook">Excel Databook</option>
              <option value="word_report">Word Report</option>
              <option value="pdf_report">PDF Report</option>
              <option value="summary_report">Summary Report</option>
            </select>
          </div>

          <div>
            <label className="form-label">Project</label>
            <select
              name="project_id"
              value={formData.project_id}
              onChange={handleChange}
              className="form-input"
              required
            >
              <option value="">Select a project</option>
              {/* Add project options here */}
            </select>
          </div>

          <div className="space-y-3">
            <label className="form-label">Include Sections</label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="include_adjustments"
                  checked={formData.include_adjustments}
                  onChange={handleChange}
                  className="mr-2"
                />
                Include Adjustments
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="include_questions"
                  checked={formData.include_questions}
                  onChange={handleChange}
                  className="mr-2"
                />
                Include Q&A
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="include_documents"
                  checked={formData.include_documents}
                  onChange={handleChange}
                  className="mr-2"
                />
                Include Document Summary
              </label>
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
              {isLoading ? 'Generating...' : 'Generate Report'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Reports