import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { 
  HelpCircle, 
  Search, 
  MessageCircle,
  Clock,
  CheckCircle,
  AlertCircle,
  Plus,
  Send
} from 'lucide-react'
import { questionsApi } from '../services/api'
import { Question, Answer } from '../types'
import toast from 'react-hot-toast'

const Questions: React.FC = () => {
  const queryClient = useQueryClient()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedPriority, setSelectedPriority] = useState<string>('all')
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null)
  const [showAnswerModal, setShowAnswerModal] = useState(false)

  const { data: questions, isLoading } = useQuery<Question[]>(
    'questions',
    questionsApi.getQuestions
  )

  const answerMutation = useMutation(questionsApi.answerQuestion, {
    onSuccess: () => {
      queryClient.invalidateQueries('questions')
      setShowAnswerModal(false)
      toast.success('Answer submitted successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to submit answer')
    }
  })

  const filteredQuestions = questions?.filter(q => {
    const matchesSearch = q.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         q.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesPriority = selectedPriority === 'all' || q.priority === selectedPriority
    return matchesSearch && matchesPriority
  }) || []

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'answered': return 'bg-green-100 text-green-800'
      case 'clarification_needed': return 'bg-yellow-100 text-yellow-800'
      case 'closed': return 'bg-gray-100 text-gray-800'
      default: return 'bg-blue-100 text-blue-800'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-100 text-red-800'
      case 'high': return 'bg-orange-100 text-orange-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-green-100 text-green-800'
    }
  }

  const handleAnswerQuestion = (question: Question) => {
    setSelectedQuestion(question)
    setShowAnswerModal(true)
  }

  const handleSubmitAnswer = (answerData: any) => {
    if (selectedQuestion) {
      answerMutation.mutate({
        questionId: selectedQuestion.id,
        ...answerData
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
          <h1 className="text-2xl font-bold text-gray-900">Questions</h1>
          <p className="text-gray-600">Q&A for project clarifications</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-500">
            {questions?.filter(q => q.status === 'pending').length || 0} pending
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-blue-500 rounded-lg">
              <HelpCircle className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Pending</p>
              <p className="text-2xl font-bold text-gray-900">
                {questions?.filter(q => q.status === 'pending').length || 0}
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
              <p className="text-sm text-gray-500">Answered</p>
              <p className="text-2xl font-bold text-gray-900">
                {questions?.filter(q => q.status === 'answered').length || 0}
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
              <p className="text-sm text-gray-500">Critical</p>
              <p className="text-2xl font-bold text-gray-900">
                {questions?.filter(q => q.priority === 'critical').length || 0}
              </p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-purple-500 rounded-lg">
              <Clock className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Overdue</p>
              <p className="text-2xl font-bold text-gray-900">
                {questions?.filter(q => q.is_overdue).length || 0}
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
            placeholder="Search questions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="form-input pl-10"
          />
        </div>
        <select 
          className="form-input w-full sm:w-auto"
          value={selectedPriority}
          onChange={(e) => setSelectedPriority(e.target.value)}
        >
          <option value="all">All Priorities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      {/* Questions List */}
      <div className="space-y-4">
        {filteredQuestions.map((question) => (
          <div key={question.id} className="card hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <h3 className="text-lg font-medium text-gray-900">{question.title}</h3>
                  <span className={`badge ${getPriorityColor(question.priority)}`}>
                    {question.priority}
                  </span>
                  <span className={`badge ${getStatusColor(question.status)}`}>
                    {question.status.replace('_', ' ')}
                  </span>
                  {question.is_ai_generated && (
                    <span className="badge bg-purple-100 text-purple-800">AI</span>
                  )}
                </div>
                <p className="text-gray-600 mb-3">{question.description}</p>
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <div className="flex items-center">
                    <Clock className="h-4 w-4 mr-1" />
                    {new Date(question.created_at).toLocaleDateString()}
                  </div>
                  {question.due_date && (
                    <div className="flex items-center">
                      <AlertCircle className="h-4 w-4 mr-1" />
                      Due: {new Date(question.due_date).toLocaleDateString()}
                    </div>
                  )}
                  {question.confidence_score && (
                    <div className="flex items-center">
                      <span className="mr-1">Confidence:</span>
                      <span className="font-medium">{Math.round(question.confidence_score * 100)}%</span>
                    </div>
                  )}
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {question.status === 'pending' && (
                  <button
                    onClick={() => handleAnswerQuestion(question)}
                    className="btn btn-primary btn-sm"
                  >
                    <MessageCircle className="h-4 w-4 mr-1" />
                    Answer
                  </button>
                )}
                <button className="btn btn-outline btn-sm">
                  View Details
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredQuestions.length === 0 && (
        <div className="text-center py-12">
          <HelpCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No questions found</h3>
          <p className="text-gray-500">
            {searchTerm ? 'No questions match your search criteria.' : 'No questions have been generated yet.'}
          </p>
        </div>
      )}

      {/* Answer Modal */}
      {showAnswerModal && selectedQuestion && (
        <AnswerModal
          question={selectedQuestion}
          onClose={() => setShowAnswerModal(false)}
          onSubmit={handleSubmitAnswer}
          isLoading={answerMutation.isLoading}
        />
      )}
    </div>
  )
}

// Answer Modal Component
const AnswerModal: React.FC<{
  question: Question
  onClose: () => void
  onSubmit: (data: any) => void
  isLoading: boolean
}> = ({ question, onClose, onSubmit, isLoading }) => {
  const [answerData, setAnswerData] = useState({
    answer_text: '',
    answer_number: 0,
    answer_boolean: false,
    answer_date: '',
    notes: '',
    is_final: true
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(answerData)
  }

  const renderAnswerInput = () => {
    switch (question.question_type) {
      case 'text':
        return (
          <textarea
            value={answerData.answer_text}
            onChange={(e) => setAnswerData({ ...answerData, answer_text: e.target.value })}
            className="form-input"
            rows={4}
            placeholder="Enter your answer..."
            required
          />
        )
      case 'number':
        return (
          <input
            type="number"
            value={answerData.answer_number}
            onChange={(e) => setAnswerData({ ...answerData, answer_number: Number(e.target.value) })}
            className="form-input"
            placeholder="Enter a number..."
            required
          />
        )
      case 'yes_no':
        return (
          <div className="flex space-x-4">
            <label className="flex items-center">
              <input
                type="radio"
                name="answer_boolean"
                checked={answerData.answer_boolean === true}
                onChange={() => setAnswerData({ ...answerData, answer_boolean: true })}
                className="mr-2"
              />
              Yes
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="answer_boolean"
                checked={answerData.answer_boolean === false}
                onChange={() => setAnswerData({ ...answerData, answer_boolean: false })}
                className="mr-2"
              />
              No
            </label>
          </div>
        )
      case 'date':
        return (
          <input
            type="date"
            value={answerData.answer_date}
            onChange={(e) => setAnswerData({ ...answerData, answer_date: e.target.value })}
            className="form-input"
            required
          />
        )
      case 'multiple_choice':
        return (
          <div className="space-y-2">
            {question.options?.map((option, index) => (
              <label key={index} className="flex items-center">
                <input
                  type="radio"
                  name="answer_text"
                  value={option}
                  checked={answerData.answer_text === option}
                  onChange={(e) => setAnswerData({ ...answerData, answer_text: e.target.value })}
                  className="mr-2"
                />
                {option}
              </label>
            ))}
          </div>
        )
      default:
        return (
          <textarea
            value={answerData.answer_text}
            onChange={(e) => setAnswerData({ ...answerData, answer_text: e.target.value })}
            className="form-input"
            rows={4}
            placeholder="Enter your answer..."
          />
        )
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Answer Question</h2>
        
        <div className="space-y-4 mb-6">
          <div>
            <h3 className="font-medium text-gray-900">{question.title}</h3>
            <p className="text-sm text-gray-600 mt-1">{question.description}</p>
          </div>

          <div className="flex items-center space-x-2">
            <span className={`badge ${getPriorityColor(question.priority)}`}>
              {question.priority}
            </span>
            <span className="text-sm text-gray-500">
              Type: {question.question_type.replace('_', ' ')}
            </span>
          </div>

          {question.ai_context && (
            <div className="bg-blue-50 p-3 rounded-lg">
              <p className="text-sm font-medium text-blue-900">AI Context:</p>
              <p className="text-sm text-blue-800">{question.ai_context}</p>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="form-label">Answer</label>
            {renderAnswerInput()}
          </div>

          <div>
            <label className="form-label">Additional Notes</label>
            <textarea
              value={answerData.notes}
              onChange={(e) => setAnswerData({ ...answerData, notes: e.target.value })}
              className="form-input"
              rows={3}
              placeholder="Add any additional context or notes..."
            />
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_final"
              checked={answerData.is_final}
              onChange={(e) => setAnswerData({ ...answerData, is_final: e.target.checked })}
              className="mr-2"
            />
            <label htmlFor="is_final" className="text-sm text-gray-700">
              This is my final answer
            </label>
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
              {isLoading ? 'Submitting...' : 'Submit Answer'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'critical': return 'bg-red-100 text-red-800'
    case 'high': return 'bg-orange-100 text-orange-800'
    case 'medium': return 'bg-yellow-100 text-yellow-800'
    default: return 'bg-green-100 text-green-800'
  }
}

export default Questions