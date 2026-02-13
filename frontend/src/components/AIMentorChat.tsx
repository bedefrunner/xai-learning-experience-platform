import { useState } from 'react'
import { lxpApiChatWithAiMentor } from '../generated/sdk.gen'
import { client } from '../generated/client.gen'

interface AIMentorChatProps {
  studentId: number
  studentName: string
  learningPaths: any[]
  progress: any[]
  onClose: () => void
}

interface Message {
  type: 'user' | 'ai'
  text: string
  timestamp: Date
}

export default function AIMentorChat({ studentId, studentName, learningPaths, progress, onClose }: AIMentorChatProps) {
  // Build context-aware greeting
  const buildGreeting = () => {
    if (learningPaths.length === 0) {
      return `Hello ${studentName}! I'm your AI Learning Mentor powered by Grok. Once you're assigned a learning path, I can provide personalized help tailored to your studies. What would you like to know?`
    }

    const activePaths = learningPaths.filter((p: any) => p.is_active)
    const avgProgress = learningPaths.reduce((sum: number, p: any) => sum + p.completion_percentage, 0) / learningPaths.length

    let greeting = `Hello ${studentName}! I'm your AI Learning Mentor powered by Grok. `

    if (activePaths.length > 0) {
      greeting += `I see you're working on ${activePaths.length} learning path${activePaths.length > 1 ? 's' : ''}. `
      if (avgProgress > 0) {
        greeting += `You're ${Math.round(avgProgress)}% through your studies - great progress! `
      }
    }

    greeting += `I'm here to help with any questions about your coursework. What would you like to work on today?`
    return greeting
  }

  const [messages, setMessages] = useState<Message[]>([
    {
      type: 'ai',
      text: buildGreeting(),
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')

    // Add user message
    setMessages((prev) => [
      ...prev,
      { type: 'user', text: userMessage, timestamp: new Date() },
    ])

    setLoading(true)

    try {
      client.setConfig({ baseUrl: 'http://localhost:8000' })

      // Find the most relevant active learning path
      const activePath = learningPaths.find((p: any) => p.is_active) || learningPaths[0]

      const response = await lxpApiChatWithAiMentor({
        body: {
          student_id: studentId,
          session_type: 'help',
          query: userMessage,
          learning_path_id: activePath?.id,
        },
      })

      if (response.data?.response) {
        // Validate response is not empty
        const responseText = response.data.response.trim()
        if (!responseText) {
          throw new Error('Empty response from AI')
        }

        setMessages((prev) => [
          ...prev,
          {
            type: 'ai',
            text: responseText,
            timestamp: new Date(),
          },
        ])
      } else {
        throw new Error('Invalid response structure')
      }
    } catch (error: any) {
      console.error('Chat error:', error)

      // Provide context-specific error messages
      let errorMessage = 'Sorry, I encountered an error. '

      if (error.message?.includes('network') || error.message?.includes('fetch')) {
        errorMessage += 'Please check your internet connection and try again.'
      } else if (error.message?.includes('timeout')) {
        errorMessage += 'The request timed out. Please try again.'
      } else {
        errorMessage += 'Please try rephrasing your question or try again in a moment.'
      }

      setMessages((prev) => [
        ...prev,
        {
          type: 'ai',
          text: errorMessage,
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
      sendMessage()
    }
  }

  return (
    <div className="ai-chat-panel">
      <div className="chat-header">
        <h3>🤖 AI Learning Mentor (Powered by Grok)</h3>
        <button className="close-button" onClick={onClose}>×</button>
      </div>

      <div className="chat-messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.type}`}>
            <div className="message-avatar">
              {message.type === 'ai' ? '🤖' : '👤'}
            </div>
            <div className="message-content">
              <p>{message.text}</p>
              <span className="message-time">
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>
          </div>
        ))}
        {loading && (
          <div className="message ai">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <p className="typing-indicator">Thinking...</p>
            </div>
          </div>
        )}
      </div>

      <div className="chat-input">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me anything about your studies..."
          rows={2}
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          disabled={!input.trim() || loading}
          className="send-button"
        >
          Send
        </button>
      </div>
    </div>
  )
}
