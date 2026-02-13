import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { lxpApiListStudents, lxpApiListLearningPaths } from '../generated/sdk.gen'
import { client } from '../generated/client.gen'
import CreateLearningPathModal from '../components/CreateLearningPathModal'
import LearningPathDetailModal from '../components/LearningPathDetailModal'

interface User {
  userId: number
  email: string
  firstName: string
  lastName: string
  userType: string
  profileId: number
}

interface EducatorDashboardProps {
  user: User
  onLogout: () => void
}

export default function EducatorDashboard({ user, onLogout }: EducatorDashboardProps) {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedPathId, setSelectedPathId] = useState<number | null>(null)

  // Configure client
  client.setConfig({ baseUrl: 'http://localhost:8000' })

  // Fetch students
  const { data: studentsData, isLoading: studentsLoading } = useQuery({
    queryKey: ['students'],
    queryFn: async () => {
      const response = await lxpApiListStudents()
      return response.data?.items ?? []
    },
  })

  // Fetch learning paths
  const { data: learningPathsData, isLoading: pathsLoading, refetch: refetchPaths } = useQuery({
    queryKey: ['learning-paths'],
    queryFn: async () => {
      const response = await lxpApiListLearningPaths()
      return response.data ?? []
    },
  })

  const students = studentsData ?? []
  const learningPaths = learningPathsData ?? []
  const loading = studentsLoading || pathsLoading

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>Welcome, {user.firstName}!</h1>
          <p>Educator Dashboard</p>
        </div>
        <button className="logout-button" onClick={onLogout}>Logout</button>
      </header>

      <div className="dashboard-content">
        {loading ? (
          <div className="loading">Loading data...</div>
        ) : (
          <>
            <section className="dashboard-section">
              <h2>Students Overview</h2>
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-value">{students.length}</div>
                  <div className="stat-label">Total Students</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{students.filter((s: any) => s.is_active).length}</div>
                  <div className="stat-label">Active Students</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{learningPaths.length}</div>
                  <div className="stat-label">Learning Paths</div>
                </div>
              </div>

              <div className="students-table">
                <h3>Student List</h3>
                <table>
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Grade</th>
                      <th>Status</th>
                      <th>Learning Paths</th>
                    </tr>
                  </thead>
                  <tbody>
                    {students.map((student: any) => {
                      const studentPaths = learningPaths.filter(
                        (p: any) => p.student_id === student.id
                      )
                      return (
                        <tr key={student.id}>
                          <td>{student.first_name} {student.last_name}</td>
                          <td>{student.email}</td>
                          <td>Grade {student.grade_level}</td>
                          <td>
                            <span className={`status-badge ${student.is_active ? 'active' : 'inactive'}`}>
                              {student.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td>{studentPaths.length} path(s)</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </section>

            <section className="dashboard-section">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2 style={{ margin: 0 }}>Learning Paths</h2>
                <button className="create-path-button" onClick={() => setShowCreateModal(true)}>
                  ➕ Create Learning Path
                </button>
              </div>
              <div className="learning-paths-list">
                {learningPaths.map((path: any) => (
                  <div key={path.id} className="path-summary" onClick={() => setSelectedPathId(path.id)}>
                    <div className="path-header">
                      <h3>{path.title}</h3>
                      <span className="subject-badge">{path.subject_name}</span>
                    </div>
                    <div className="path-details">
                      <p>Student: {path.student_name}</p>
                      <p>Difficulty: {path.difficulty_level}</p>
                      <p>Progress: {Math.round(path.completion_percentage)}%</p>
                    </div>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{ width: `${path.completion_percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </>
        )}
      </div>

      {showCreateModal && (
        <CreateLearningPathModal
          students={students}
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            refetchPaths() // Refresh learning paths after creating
          }}
        />
      )}

      {selectedPathId && (
        <LearningPathDetailModal
          pathId={selectedPathId}
          onClose={() => setSelectedPathId(null)}
        />
      )}
    </div>
  )
}
