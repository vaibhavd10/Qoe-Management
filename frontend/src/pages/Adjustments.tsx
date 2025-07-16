import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { 
  CheckSquare, 
  Search, 
  DollarSign,
  AlertCircle,
  TrendingUp,
  Eye,
  Check,
  X,
  Edit
} from 'lucide-react'
import { adjustmentsApi } from '../services/api'
import { Adjustment } from '../types'
import toast from 'react-hot-toast'

const Adjustments: React.FC = () => {
  const queryClient = useQueryClient()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedStatus, setSelectedStatus] = useState<string>('all')
  const [selectedAdjustment, setSelectedAdjustment] = useState<Adjustment | null>(null)
  const [showReviewModal, setShowReviewModal] = useState(false)

  const { data: adjustments, isLoading } = useQuery<Adjustment[]>(
    'adjustments',
    adjustmentsApi.getAdjustments
  )

  const reviewMutation = useMutation(adjustmentsApi.reviewAdjustment, {
    onSuccess: () => {
      queryClient.invalidateQueries('adjustments')
      setShowReviewModal(false)
      toast.success('Adjustment reviewed successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to review adjustment')
    }
  })

  const filteredAdjustments = adjustments?.filter(adj => {
    const matchesSearch = adj.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         adj.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = selectedStatus === 'all' || adj.status === selectedStatus
    return matchesSearch && matchesStatus
  }) || []

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'accepted': return 'bg-green-100 text-green-800'
      case 'rejected': return 'bg-red-100 text-red-800'
      case 'modified': return 'bg-blue-100 text-blue-800'
      default: return 'bg-yellow-100 text-yellow-800'
    }
  }

  const getAdjustmentTypeColor = (type: string) => {
    const colors = [
      'bg-purple-100 text-purple-800',
      'bg-pink-100 text-pink-800',
      'bg-indigo-100 text-indigo-800',
      'bg-teal-100 text-teal-800',
      'bg-orange-100 text-orange-800'
    ]
    return colors[Math.abs(type.split('').reduce((a, b) => a + b.charCodeAt(0), 0)) % colors.length]
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(amount)
  }

  const handleReview = (adjustment: Adjustment) => {
    setSelectedAdjustment(adjustment)
    setShowReviewModal(true)
  }

  const handleSubmitReview = (reviewData: any) => {
    if (selectedAdjustment) {
      reviewMutation.mutate({
        id: selectedAdjustment.id,
        ...reviewData
      })
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
          <h1 className="text-2xl font-bold text-gray-900">Adjustments</h1>
          <p className="text-gray-600">Review AI-generated adjustments</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-500">
            {adjustments?.filter(a => a.status === 'pending').length || 0} pending review
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-500 rounded-lg">
              <AlertCircle className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Pending</p>
              <p className="text-2xl font-bold text-gray-900">
                {adjustments?.filter(a => a.status === 'pending').length || 0}
              </p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-green-500 rounded-lg">
              <Check className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Accepted</p>
              <p className="text-2xl font-bold text-gray-900">
                {adjustments?.filter(a => a.status === 'accepted').length || 0}
              </p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-red-500 rounded-lg">
              <X className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Rejected</p>
              <p className="text-2xl font-bold text-gray-900">
                {adjustments?.filter(a => a.status === 'rejected').length || 0}
              </p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-purple-500 rounded-lg">
              <DollarSign className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Total Amount</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(adjustments?.reduce((sum, adj) => sum + Math.abs(adj.amount), 0) || 0)}
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
            placeholder="Search adjustments..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="form-input pl-10"
          />
        </div>
        <select 
          className="form-input w-full sm:w-auto"
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
        >
          <option value="all">All Status</option>
          <option value="pending">Pending</option>
          <option value="accepted">Accepted</option>
          <option value="rejected">Rejected</option>
          <option value="modified">Modified</option>
        </select>
      </div>

      {/* Adjustments Table */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Adjustment
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Confidence
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredAdjustments.map((adjustment) => (
                <tr key={adjustment.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {adjustment.title}
                      </div>
                      <div className="text-sm text-gray-500">
                        {adjustment.description}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`badge ${getAdjustmentTypeColor(adjustment.adjustment_type)}`}>
                      {adjustment.adjustment_type.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {formatCurrency(adjustment.amount)}
                    </div>
                    {adjustment.is_material && (
                      <div className="text-xs text-red-600 font-medium">
                        Material
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="text-sm text-gray-900 mr-2">
                        {Math.round(adjustment.confidence_score * 100)}%
                      </div>
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${
                            adjustment.confidence_score > 0.8 ? 'bg-green-500' :
                            adjustment.confidence_score > 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${adjustment.confidence_score * 100}%` }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`badge ${getStatusColor(adjustment.status)}`}>
                      {adjustment.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleReview(adjustment)}
                        className="text-blue-600 hover:text-blue-800"
                        title="Review"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      {adjustment.status === 'pending' && (
                        <>
                          <button
                            onClick={() => handleSubmitReview({ status: 'accepted' })}
                            className="text-green-600 hover:text-green-800"
                            title="Accept"
                          >
                            <Check className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleSubmitReview({ status: 'rejected' })}
                            className="text-red-600 hover:text-red-800"
                            title="Reject"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredAdjustments.length === 0 && (
          <div className="text-center py-12">
            <CheckSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No adjustments found</h3>
            <p className="text-gray-500">
              {searchTerm ? 'No adjustments match your search criteria.' : 'No adjustments have been generated yet.'}
            </p>
          </div>
        )}
      </div>

      {/* Review Modal */}
      {showReviewModal && selectedAdjustment && (
        <ReviewModal
          adjustment={selectedAdjustment}
          onClose={() => setShowReviewModal(false)}
          onSubmit={handleSubmitReview}
          isLoading={reviewMutation.isLoading}
        />
      )}
    </div>
  )
}

// Review Modal Component
const ReviewModal: React.FC<{
  adjustment: Adjustment
  onClose: () => void
  onSubmit: (data: any) => void
  isLoading: boolean
}> = ({ adjustment, onClose, onSubmit, isLoading }) => {
  const [reviewData, setReviewData] = useState({
    status: adjustment.status,
    reviewer_notes: '',
    amount: adjustment.amount
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(reviewData)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Review Adjustment</h2>
        
        <div className="space-y-4 mb-6">
          <div>
            <h3 className="font-medium text-gray-900">{adjustment.title}</h3>
            <p className="text-sm text-gray-600">{adjustment.description}</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700">Type</label>
              <p className="text-sm text-gray-900">{adjustment.adjustment_type.replace('_', ' ')}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Amount</label>
              <p className="text-sm text-gray-900">{new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(adjustment.amount)}</p>
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-700">AI Narrative</label>
            <p className="text-sm text-gray-900 bg-gray-50 p-3 rounded-lg">{adjustment.narrative}</p>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-700">Confidence Score</label>
            <div className="flex items-center mt-1">
              <span className="text-sm text-gray-900 mr-2">{Math.round(adjustment.confidence_score * 100)}%</span>
              <div className="w-32 bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${
                    adjustment.confidence_score > 0.8 ? 'bg-green-500' :
                    adjustment.confidence_score > 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${adjustment.confidence_score * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="form-label">Review Status</label>
            <select
              value={reviewData.status}
              onChange={(e) => setReviewData({ ...reviewData, status: e.target.value })}
              className="form-input"
            >
              <option value="pending">Pending</option>
              <option value="accepted">Accepted</option>
              <option value="rejected">Rejected</option>
              <option value="modified">Modified</option>
            </select>
          </div>

          {reviewData.status === 'modified' && (
            <div>
              <label className="form-label">Adjusted Amount</label>
              <input
                type="number"
                value={reviewData.amount}
                onChange={(e) => setReviewData({ ...reviewData, amount: Number(e.target.value) })}
                className="form-input"
                step="0.01"
              />
            </div>
          )}

          <div>
            <label className="form-label">Reviewer Notes</label>
            <textarea
              value={reviewData.reviewer_notes}
              onChange={(e) => setReviewData({ ...reviewData, reviewer_notes: e.target.value })}
              className="form-input"
              rows={3}
              placeholder="Add your review notes..."
            />
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
              {isLoading ? 'Submitting...' : 'Submit Review'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Adjustments