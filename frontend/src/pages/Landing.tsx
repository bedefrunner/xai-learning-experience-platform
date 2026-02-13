interface LandingProps {
  onRoleSelect: (role: 'student' | 'educator') => void
}

export default function Landing({ onRoleSelect }: LandingProps) {
  return (
    <div className="landing-page">
      <div className="landing-container">
        <h1>XAI Learning Experience Platform</h1>
        <p className="subtitle">AI-Native Education for Everyone</p>

        <div className="role-selection">
          <h2>I am a...</h2>
          <div className="role-buttons">
            <button
              className="role-button student"
              onClick={() => onRoleSelect('student')}
            >
              <span className="role-icon">🎓</span>
              <span className="role-title">Student</span>
              <span className="role-desc">Access your learning path and progress</span>
            </button>

            <button
              className="role-button educator"
              onClick={() => onRoleSelect('educator')}
            >
              <span className="role-icon">👨‍🏫</span>
              <span className="role-title">Teacher</span>
              <span className="role-desc">Manage students and monitor progress</span>
            </button>
          </div>
        </div>

        <div className="demo-info">
          <p><strong>Demo Credentials:</strong></p>
          <p>Student: sarah.johnson@student.lxp.com / student123</p>
          <p>Teacher: mr.smith@teacher.lxp.com / teacher123</p>
        </div>
      </div>
    </div>
  )
}
