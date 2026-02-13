import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { lxpApiListLearningPaths, lxpApiListProgress } from '../generated/sdk.gen'
import { client } from '../generated/client.gen'
import AIMentorChat from '../components/AIMentorChat'

interface User {
  userId: number
  email: string
  firstName: string
  lastName: string
  userType: string
  profileId: number
}

interface StudentDashboardProps {
  user: User
  onLogout: () => void
  onNavigateToLearningPath: (pathId: number) => void
}

export default function StudentDashboard({ user, onLogout, onNavigateToLearningPath }: StudentDashboardProps) {
  const [showChat, setShowChat] = useState(false)

  // Configure client
  client.setConfig({ baseUrl: 'http://localhost:8000' })

  // Fetch learning paths for this student
  const { data: learningPathsData, isLoading: pathsLoading } = useQuery({
    queryKey: ['learning-paths', user.profileId],
    queryFn: async () => {
      const response = await lxpApiListLearningPaths({
        query: { student_id: user.profileId },
      })
      return response.data ?? []
    },
  })

  // Fetch progress for this student
  const { data: progressData, isLoading: progressLoading } = useQuery({
    queryKey: ['progress', user.profileId],
    queryFn: async () => {
      const response = await lxpApiListProgress({
        query: { student_id: user.profileId },
      })
      return response.data ?? []
    },
  })

  const learningPaths = learningPathsData ?? []
  const progress = progressData ?? []
  const loading = pathsLoading || progressLoading

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>Welcome, {user.firstName}!</h1>
          <p>Student Dashboard</p>
        </div>
        <div className="header-actions">
          <button className="ai-chat-button" onClick={() => setShowChat(!showChat)}>
            {showChat ? 'Close' : '💬 AI Mentor'}
          </button>
          <button className="logout-button" onClick={onLogout}>Logout</button>
        </div>
      </header>

      {showChat && (
        <div className="ai-chat-overlay">
          <AIMentorChat
            studentId={user.profileId}
            studentName={user.firstName}
            learningPaths={learningPaths}
            progress={progress}
            onClose={() => setShowChat(false)}
          />
        </div>
      )}

      <div className="dashboard-content">
        {loading ? (
          <div className="loading">Loading your data...</div>
        ) : (
          <>
            <section className="dashboard-section">
              <h2>My Learning Paths</h2>
              {learningPaths.length === 0 ? (
                <div className="empty-state">
                  <p>No learning paths assigned yet.</p>
                  <p>Contact your teacher to get started!</p>
                </div>
              ) : (
                <div className="learning-paths-grid">
                  {learningPaths.map((path: any) => (
                    <div key={path.id} className="learning-path-card" onClick={() => onNavigateToLearningPath(path.id)}>
                      <h3>{path.title}</h3>
                      <p className="subject-badge">{path.subject_name}</p>
                      <p>{path.description}</p>
                      <div className="path-meta">
                        <span className="difficulty-badge">{path.difficulty_level}</span>
                        <span className="completion">
                          {Math.round(path.completion_percentage)}% Complete
                        </span>
                      </div>
                      <div className="progress-bar">
                        <div
                          className="progress-fill"
                          style={{ width: `${path.completion_percentage}%` }}
                        />
                      </div>
                      {path.personalized_goals && path.personalized_goals.length > 0 && (
                        <div className="goals">
                          <strong>Your Goals:</strong>
                          <ul>
                            {path.personalized_goals.slice(0, 3).map((goal: string, i: number) => (
                              <li key={i}>{goal}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </section>

            <section className="dashboard-section">
              <h2>Recent Progress</h2>
              {progress.length === 0 ? (
                <div className="empty-state">
                  <p>No progress recorded yet. Start learning to see your progress here!</p>
                </div>
              ) : (
                <div className="progress-list">
                  {progress.slice(0, 5).map((item: any) => (
                    <div key={item.id} className="progress-item">
                      <div className="progress-info">
                        <h4>{item.content_title}</h4>
                        <span className={`status-badge ${item.status}`}>{item.status}</span>
                      </div>
                      <div className="progress-stats">
                        <span>Mastery: {Math.round(item.mastery_level)}%</span>
                        <span>Time: {item.time_spent_minutes} min</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </div>
  )
}
