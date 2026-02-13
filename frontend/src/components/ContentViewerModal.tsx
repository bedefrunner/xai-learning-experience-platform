import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { lxpApiGetContent, lxpApiChatWithAiMentor, lxpApiUpdateProgress } from '../generated/sdk.gen'
import { client } from '../generated/client.gen'

interface ContentViewerModalProps {
  contentId: number
  studentId: number
  learningPathId: number
  progressId?: number
  onClose: () => void
}

interface Message {
  type: 'user' | 'ai'
  text: string
  timestamp: Date
}

export default function ContentViewerModal({ contentId, studentId, learningPathId, progressId, onClose }: ContentViewerModalProps) {
  const [showAIHelp, setShowAIHelp] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const queryClient = useQueryClient()

  // Configure client
  client.setConfig({ baseUrl: 'http://localhost:8000' })

  // Fetch content details
  const { data: content, isLoading: contentLoading } = useQuery({
    queryKey: ['content', contentId],
    queryFn: async () => {
      const response = await lxpApiGetContent({ path: { content_id: contentId } })
      return response.data
    },
  })

  // Mark as complete mutation
  const markCompleteMutation = useMutation({
    mutationFn: async () => {
      if (!progressId) {
        throw new Error('No progress record found')
      }
      const response = await lxpApiUpdateProgress({
        path: { progress_id: progressId },
        body: {
          status: 'completed',
          completion_percentage: 100,
          mastery_level: 85,
        },
      })
      return response.data
    },
    onSuccess: () => {
      // Invalidate progress queries to refresh the UI
      queryClient.invalidateQueries({ queryKey: ['progress'] })
      queryClient.invalidateQueries({ queryKey: ['learning-paths'] })
      alert('Great job! Content marked as complete. 🎉')
      onClose()
    },
    onError: (error: any) => {
      console.error('Error marking complete:', error)
      alert('Failed to mark content as complete. Please try again.')
    },
  })

  const sendAIMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')

    setMessages((prev) => [
      ...prev,
      { type: 'user', text: userMessage, timestamp: new Date() },
    ])

    setLoading(true)

    try {
      const response = await lxpApiChatWithAiMentor({
        body: {
          student_id: studentId,
          session_type: 'help',
          query: userMessage,
          learning_path_id: learningPathId,
          content_id: contentId,
        },
      })

      if (response.data?.response) {
        setMessages((prev) => [
          ...prev,
          {
            type: 'ai',
            text: response.data.response.trim(),
            timestamp: new Date(),
          },
        ])
      } else {
        throw new Error('Invalid response')
      }
    } catch (error: any) {
      console.error('AI Help error:', error)
      setMessages((prev) => [
        ...prev,
        {
          type: 'ai',
          text: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date(),
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendAIMessage()
    }
  }

  if (contentLoading) {
    return (
      <div className="modal-overlay" onClick={onClose} style={{ zIndex: 3000 }}>
        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
          <div className="modal-body">
            <div className="loading">Loading content...</div>
          </div>
        </div>
      </div>
    )
  }

  if (!content) {
    return null
  }

  return (
    <div className="modal-overlay" onClick={onClose} style={{ zIndex: 3000 }}>
      <div className="modal-content learning-path-detail-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h2>📖 {content.title}</h2>
            <span className="subject-badge" style={{ marginTop: '0.5rem' }}>{content.content_type}</span>
          </div>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          {/* Content Material */}
          <div className="path-detail-section">
            <h3>📝 Learning Material</h3>
            <div className="description-box">
              <p style={{ whiteSpace: 'pre-wrap', lineHeight: '1.8' }}>{content.description}</p>
            </div>
          </div>

          {/* AI Help Section */}
          <div className="path-detail-section">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3>🤖 AI Learning Assistant</h3>
              <button
                className="button-secondary"
                onClick={() => {
                  setShowAIHelp(!showAIHelp)
                  if (!showAIHelp && messages.length === 0) {
                    setMessages([{
                      type: 'ai',
                      text: `Hi! I'm here to help you understand "${content.title}". What questions do you have about this content?`,
                      timestamp: new Date(),
                    }])
                  }
                }}
              >
                {showAIHelp ? 'Hide AI Help' : 'Ask AI for Help'}
              </button>
            </div>

            {showAIHelp && (
              <div style={{ border: '2px solid #667eea', borderRadius: '12px', padding: '1rem', background: '#f8f9ff' }}>
                <div style={{ maxHeight: '300px', overflowY: 'auto', marginBottom: '1rem' }}>
                  {messages.map((message, index) => (
                    <div
                      key={index}
                      style={{
                        marginBottom: '1rem',
                        padding: '0.75rem',
                        background: message.type === 'ai' ? '#e8f0ff' : '#fff',
                        borderRadius: '8px',
                        borderLeft: `4px solid ${message.type === 'ai' ? '#667eea' : '#764ba2'}`,
                      }}
                    >
                      <div style={{ fontWeight: 600, marginBottom: '0.25rem', color: '#1a1a1a' }}>
                        {message.type === 'ai' ? '🤖 AI Mentor' : '👤 You'}
                      </div>
                      <p style={{ margin: 0, color: '#2c2c2c' }}>{message.text}</p>
                    </div>
                  ))}
                  {loading && (
                    <div style={{ padding: '0.75rem', background: '#e8f0ff', borderRadius: '8px' }}>
                      <p style={{ margin: 0, color: '#667eea', fontStyle: 'italic' }}>AI is thinking...</p>
                    </div>
                  )}
                </div>

                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask a question about this content..."
                    rows={2}
                    disabled={loading}
                    style={{
                      flex: 1,
                      padding: '0.75rem',
                      borderRadius: '8px',
                      border: '2px solid #e0e0e0',
                      fontSize: '0.95rem',
                      fontFamily: 'inherit',
                    }}
                  />
                  <button
                    onClick={sendAIMessage}
                    disabled={!input.trim() || loading}
                    className="button-primary"
                    style={{ alignSelf: 'flex-end' }}
                  >
                    Send
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="modal-footer">
          <button className="button-secondary" onClick={onClose}>
            Close
          </button>
          <button
            className="button-primary"
            onClick={() => markCompleteMutation.mutate()}
            disabled={!progressId || markCompleteMutation.isPending}
          >
            {markCompleteMutation.isPending ? 'Marking Complete...' : '✓ Mark as Complete'}
          </button>
        </div>
      </div>
    </div>
  )
}
