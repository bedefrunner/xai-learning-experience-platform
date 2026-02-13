import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './App.css'
import Landing from './pages/Landing'
import Login from './pages/Login'
import StudentDashboard from './pages/StudentDashboard'
import EducatorDashboard from './pages/EducatorDashboard'
import LearningPathDetailPage from './pages/LearningPathDetailPage'
import ContentViewerPage from './pages/ContentViewerPage'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

type Page = 'landing' | 'login' | 'student-dashboard' | 'educator-dashboard' | 'learning-path-detail' | 'content-viewer'

interface User {
  userId: number
  email: string
  firstName: string
  lastName: string
  userType: 'student' | 'educator'
  profileId: number
}

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('landing')
  const [selectedUserType, setSelectedUserType] = useState<'student' | 'educator' | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [selectedPathId, setSelectedPathId] = useState<number | null>(null)
  const [selectedContentId, setSelectedContentId] = useState<number | null>(null)
  const [progressId, setProgressId] = useState<number | undefined>(undefined)

  const handleRoleSelect = (role: 'student' | 'educator') => {
    setSelectedUserType(role)
    setCurrentPage('login')
  }

  const handleLoginSuccess = (userData: User) => {
    setUser(userData)
    if (userData.userType === 'student') {
      setCurrentPage('student-dashboard')
    } else {
      setCurrentPage('educator-dashboard')
    }
  }

  const handleLogout = () => {
    setUser(null)
    setSelectedUserType(null)
    setCurrentPage('landing')
  }

  const handleNavigateToLearningPath = (pathId: number) => {
    setSelectedPathId(pathId)
    setCurrentPage('learning-path-detail')
  }

  const handleNavigateToContent = (contentId: number, pathId: number, progressId?: number) => {
    setSelectedContentId(contentId)
    setSelectedPathId(pathId)
    setProgressId(progressId)
    setCurrentPage('content-viewer')
  }

  const handleBackToStudentDashboard = () => {
    setSelectedPathId(null)
    setSelectedContentId(null)
    setProgressId(undefined)
    setCurrentPage('student-dashboard')
  }

  const handleBackToLearningPath = () => {
    setSelectedContentId(null)
    setProgressId(undefined)
    setCurrentPage('learning-path-detail')
  }

  return (
    <QueryClientProvider client={queryClient}>
      <div className="app">
        {currentPage === 'landing' && (
          <Landing onRoleSelect={handleRoleSelect} />
        )}

        {currentPage === 'login' && selectedUserType && (
          <Login
            userType={selectedUserType}
            onLoginSuccess={handleLoginSuccess}
            onBack={() => setCurrentPage('landing')}
          />
        )}

        {currentPage === 'student-dashboard' && user && user.userType === 'student' && (
          <StudentDashboard
            user={user}
            onLogout={handleLogout}
            onNavigateToLearningPath={handleNavigateToLearningPath}
          />
        )}

        {currentPage === 'educator-dashboard' && user && user.userType === 'educator' && (
          <EducatorDashboard
            user={user}
            onLogout={handleLogout}
          />
        )}

        {currentPage === 'learning-path-detail' && user && selectedPathId && (
          <LearningPathDetailPage
            pathId={selectedPathId}
            onBack={handleBackToStudentDashboard}
            onNavigateToContent={handleNavigateToContent}
          />
        )}

        {currentPage === 'content-viewer' && user && selectedContentId && selectedPathId && (
          <ContentViewerPage
            contentId={selectedContentId}
            studentId={user.profileId}
            learningPathId={selectedPathId}
            progressId={progressId}
            onBack={handleBackToLearningPath}
          />
        )}
      </div>
    </QueryClientProvider>
  )
}

export default App
