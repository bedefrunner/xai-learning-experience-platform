import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { lxpApiGetContent, lxpApiChatWithAiMentor, lxpApiUpdateProgress, lxpApiListProgress } from '../generated/sdk.gen'
import { client } from '../generated/client.gen'

interface ContentViewerPageProps {
  contentId: number
  studentId: number
  learningPathId: number
  progressId?: number
  onBack: () => void
}

interface Message {
  type: 'user' | 'ai'
  text: string
  timestamp: Date
}

export default function ContentViewerPage({ contentId, studentId, learningPathId, progressId, onBack }: ContentViewerPageProps) {
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

  // Fetch progress record to check current status
  const { data: progressData, isLoading: progressLoading } = useQuery({
    queryKey: ['progress', 'content', contentId, learningPathId],
    queryFn: async () => {
      const response = await lxpApiListProgress({
        query: {
          learning_path_id: learningPathId,
          student_id: studentId,
        },
      })
      const allProgress = response.data ?? []
      return allProgress.find((p: any) => p.content_id === contentId)
    },
    enabled: !!progressId,
  })

  const currentProgress = progressData
  const isCompleted = currentProgress?.status === 'completed'

  // Toggle completion status mutation
  const toggleCompletionMutation = useMutation({
    mutationFn: async () => {
      if (!progressId) {
        throw new Error('No progress record found')
      }
      const response = await lxpApiUpdateProgress({
        path: { progress_id: progressId },
        body: isCompleted
          ? {
              status: 'in_progress',
              completion_percentage: currentProgress?.completion_percentage || 50,
              mastery_level: currentProgress?.mastery_level || 50,
            }
          : {
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
      if (isCompleted) {
        alert('Content marked as in progress. Keep learning! 📚')
      } else {
        alert('Great job! Content marked as complete. 🎉')
      }
    },
    onError: (error: any) => {
      console.error('Error updating progress:', error)
      alert('Failed to update progress. Please try again.')
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

  if (contentLoading || progressLoading) {
    return (
      <div className="dashboard">
        <div className="dashboard-content">
          <div className="loading">Loading content...</div>
        </div>
      </div>
    )
  }

  if (!content) {
    return null
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>📖 {content.title}</h1>
          <span className="subject-badge">{content.content_type}</span>
        </div>
        <div className="header-actions">
          <button className="button-secondary" onClick={onBack}>← Back</button>
          <button
            className={isCompleted ? "button-secondary" : "button-primary"}
            onClick={() => toggleCompletionMutation.mutate()}
            disabled={!progressId || toggleCompletionMutation.isPending}
          >
            {toggleCompletionMutation.isPending
              ? 'Updating...'
              : isCompleted
              ? '↺ Mark as Incomplete'
              : '✓ Mark as Complete'}
          </button>
        </div>
      </header>

      <div className="dashboard-content">
        {/* Content Material */}
        <div className="path-detail-section">
          <h3>📝 Learning Material</h3>
          <div className="description-box" style={{
            background: 'white',
            borderRadius: '12px',
            padding: '2.5rem',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            fontSize: '1.05rem',
            lineHeight: '1.9',
            color: '#2c3e50',
          }}>
            <div style={{ whiteSpace: 'pre-wrap' }}>
              {content.content_body || content.description}
            </div>
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
    </div>
  )
}
