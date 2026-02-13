import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { lxpApiListSubjects, lxpApiListContent, lxpApiCreateLearningPath } from '../generated/sdk.gen'
import { client } from '../generated/client.gen'

interface CreateLearningPathModalProps {
  students: any[]
  onClose: () => void
  onSuccess: () => void
}

export default function CreateLearningPathModal({ students, onClose, onSuccess }: CreateLearningPathModalProps) {
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [createdPath, setCreatedPath] = useState<any>(null)

  // Form data
  const [studentId, setStudentId] = useState('')
  const [subjectId, setSubjectId] = useState('')
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [difficulty, setDifficulty] = useState('intermediate')
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0])
  const [endDate, setEndDate] = useState(
    new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  )
  const [selectedContent, setSelectedContent] = useState<number[]>([])

  // Configure client
  client.setConfig({ baseUrl: 'http://localhost:8000' })

  // Fetch subjects
  const { data: subjectsData } = useQuery({
    queryKey: ['subjects'],
    queryFn: async () => {
      const response = await lxpApiListSubjects()
      return response.data ?? []
    },
  })

  // Fetch content when subjectId changes
  const { data: contentData } = useQuery({
    queryKey: ['content', subjectId],
    queryFn: async () => {
      const response = await lxpApiListContent({
        query: { subject_id: parseInt(subjectId) }
      })
      return response.data?.items ?? response.data ?? []
    },
    enabled: !!subjectId, // Only run when subjectId is set
  })

  const subjects = subjectsData ?? []
  const content = contentData ?? []

  const handleContentToggle = (contentId: number) => {
    setSelectedContent(prev =>
      prev.includes(contentId)
        ? prev.filter(id => id !== contentId)
        : [...prev, contentId]
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (selectedContent.length === 0) {
      setError('Please select at least one content item')
      return
    }

    setLoading(true)
    setError('')

    try {
      client.setConfig({ baseUrl: 'http://localhost:8000' })

      const response = await lxpApiCreateLearningPath({
        body: {
          student_id: parseInt(studentId),
          subject_id: parseInt(subjectId),
          title,
          description,
          difficulty_level: difficulty,
          start_date: startDate,
          target_completion_date: endDate,
          content_ids: selectedContent,
        }
      })

      if (response.data) {
        setCreatedPath(response.data)
        setStep(3) // Show success screen with AI-generated goals
      } else if (response.error) {
        setError('Failed to create learning path')
      }
    } catch (err) {
      setError('Network error. Please try again.')
      console.error('Create path error:', err)
    } finally {
      setLoading(false)
    }
  }

  const selectedStudent = students.find(s => s.id === parseInt(studentId))
  const selectedSubject = subjects.find(s => s.id === parseInt(subjectId))

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>✨ Create Learning Path</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        {step === 1 && (
          <form onSubmit={(e) => { e.preventDefault(); setStep(2); }} className="modal-body">
            <div className="form-group">
              <label>Student *</label>
              <select value={studentId} onChange={(e) => setStudentId(e.target.value)} required>
                <option value="">Select a student</option>
                {students.map(student => (
                  <option key={student.id} value={student.id}>
                    {student.first_name} {student.last_name} (Grade {student.grade_level})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Subject *</label>
              <select value={subjectId} onChange={(e) => setSubjectId(e.target.value)} required>
                <option value="">Select a subject</option>
                {subjects.map(subject => (
                  <option key={subject.id} value={subject.id}>
                    {subject.name} ({subject.code})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Learning Path Title *</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Introduction to Algebra"
                required
              />
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe what the student will learn..."
                rows={3}
              />
            </div>

            <div className="form-group">
              <label>Difficulty Level *</label>
              <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)} required>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Start Date *</label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label>Target End Date *</label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  required
                />
              </div>
            </div>

            {error && <div className="error-message">{error}</div>}

            <div className="modal-footer">
              <button type="button" className="button-secondary" onClick={onClose}>
                Cancel
              </button>
              <button type="submit" className="button-primary">
                Next: Select Content →
              </button>
            </div>
          </form>
        )}

        {step === 2 && (
          <form onSubmit={handleSubmit} className="modal-body">
            <div className="selected-info">
              <p><strong>Student:</strong> {selectedStudent?.first_name} {selectedStudent?.last_name}</p>
              <p><strong>Subject:</strong> {selectedSubject?.name}</p>
              <p><strong>Difficulty:</strong> {difficulty}</p>
            </div>

            <div className="form-group">
              <label>Select Content Items *</label>
              <div className="content-list">
                {content.length === 0 ? (
                  <p className="empty-state">No content available for this subject</p>
                ) : (
                  content.map(item => (
                    <label key={item.id} className="content-checkbox">
                      <input
                        type="checkbox"
                        checked={selectedContent.includes(item.id)}
                        onChange={() => handleContentToggle(item.id)}
                      />
                      <div className="content-item-info">
                        <strong>{item.title}</strong>
                        <span className="content-meta">
                          {item.content_type} • {item.difficulty_level} • {item.estimated_duration_minutes} min
                        </span>
                      </div>
                    </label>
                  ))
                )}
              </div>
              <p className="help-text">Selected: {selectedContent.length} items</p>
            </div>

            {error && <div className="error-message">{error}</div>}

            <div className="modal-footer">
              <button type="button" className="button-secondary" onClick={() => setStep(1)}>
                ← Back
              </button>
              <button type="submit" className="button-primary" disabled={loading || selectedContent.length === 0}>
                {loading ? '🤖 Generating Goals with Grok AI...' : '✨ Create Path (AI will generate goals)'}
              </button>
            </div>
          </form>
        )}

        {step === 3 && createdPath && (
          <div className="modal-body success-screen">
            <div className="success-icon">✅</div>
            <h3>Learning Path Created!</h3>

            <div className="ai-goals-section">
              <h4>🤖 AI-Generated Personalized Goals:</h4>
              <ul className="ai-goals-list">
                {createdPath.personalized_goals?.map((goal: string, i: number) => (
                  <li key={i}>{goal}</li>
                ))}
              </ul>
              <p className="ai-note">Generated by Grok AI based on student grade, subject, and difficulty</p>
            </div>

            <div className="path-summary">
              <p><strong>Student:</strong> {createdPath.student_name}</p>
              <p><strong>Subject:</strong> {createdPath.subject_name}</p>
              <p><strong>Duration:</strong> {startDate} to {endDate}</p>
              <p><strong>Content Items:</strong> {selectedContent.length}</p>
            </div>

            <button
              className="button-primary"
              onClick={() => {
                onSuccess()
                onClose()
              }}
              style={{ marginTop: '2rem' }}
            >
              Done - Return to Dashboard
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
