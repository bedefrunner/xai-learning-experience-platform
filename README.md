# XAI Learning Experience Platform (LXP)

An AI-native Learning Experience Platform powered by **Grok AI** (xAI) that delivers personalized education through adaptive learning paths, real-time progress tracking, and intelligent mentoring.

## 🛠️ Technical Implementation

### Architecture
- **Backend:** Django + Django Ninja (REST API)
- **Frontend:** React 19 + TypeScript + Vite 7
- **Data Fetching:** TanStack Query (React Query) v5
- **AI Integration:** Grok via xAI API (OpenAI-compatible)
- **DevOps:** Docker Compose + Makefile (make up, make migrate, make shell)
- **Styling:** Custom CSS with responsive design
- **Type Safety:** Full TypeScript with auto-generated API client

### Code Quality Highlights
- ✅ **No `useEffect` overuse** - Uses React Query for all data fetching
- ✅ **Type-safe API client** - Auto-generated from OpenAPI schema
- ✅ **Zero `as any` casts** - Full TypeScript type safety
- ✅ **Proper schema naming** - `InputSchema` and `OutputSchema` conventions
- ✅ **Error boundaries** - Comprehensive error handling throughout
- ✅ **Responsive design** - Works on desktop and mobile

### API Documentation
- **Interactive docs:** http://localhost:8000/api/docs
- **OpenAPI schema:** http://localhost:8000/api/openapi.json
- Auto-generated TypeScript client from OpenAPI spec

## 🚦 Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- xAI API key (for Grok integration)

### Setup

1. **Set environment variable**
```bash
# Create backend/.env file
echo "XAI_API_KEY=your_xai_api_key_here" > backend/.env
```

2. **Start backend (Docker)**
```bash
cd backend
make up          # Start services
make migrate     # Run migrations
```

3. **Start frontend**
```bash
cd frontend
npm install
npm run generate-client  # Generate TypeScript API client
npm run dev
```

### Access the Application
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/docs

### Useful Commands
```bash
make down        # Stop services
make logs        # View logs
make shell       # Django shell
```

## 🎯 Demo Credentials

### Student Login
- Email: `john.doe@email.com`
- Password: `password123`

### Educator Login
- Email: `jane.smith@email.com`
- Password: `password123`

## 🧪 Testing the AI Features

### 1. Test Personalized Learning Path Creation (Educator)
1. Login as educator
2. Click "Create Learning Path"
3. Select student, subject, and difficulty
4. Notice AI-generated goals appear after creation
5. Goals are tailored to grade level and subject

### 2. Test Context-Aware AI Mentor (Student)
1. Login as student
2. Click "AI Mentor" button
3. Notice personalized greeting with your progress
4. Ask subject-specific questions
5. AI knows your learning context and mastery levels

**Try these prompts:**
- "Can you help me with the topics I'm struggling with?"
- "What should I focus on to improve my grade?"
- "Explain [difficult topic] in simple terms"

## 🌟 Key Features

### 1. **AI-Powered Personalized Learning Paths**
- Grok AI generates custom learning goals tailored to grade level, subject, and difficulty
- Educators create paths with AI-suggested objectives and recommended resources
- Automatic progress tracking with mastery level calculations

### 2. **Intelligent AI Mentor Chat** 🤖
Context-aware learning assistant with access to:
- Complete student learning profile and progress
- Mastery levels for each topic (strengths and weaknesses)
- Grade-appropriate, personalized explanations
- Focus on areas where student needs support

### 3. **Real-Time Progress Tracking**
- Mastery level and completion percentage for each content item
- Time spent monitoring and status tracking
- Visual progress indicators on dashboards
- Detailed analytics for educator intervention

### 4. **Dual Dashboard System**
**Students:** View learning paths, AI-generated goals, progress stats, and access AI Mentor
**Educators:** Monitor all students, create learning paths, assign content, view detailed analytics

## 🚀 Grok AI Integration

### Prompt Engineering Strategy

**1. Personalized Goals Generation**
- System: "You are an expert educational curriculum designer creating personalized learning goals."
- Generates 4 grade-appropriate, measurable goals based on student level, subject, and difficulty
- Validates response structure and falls back to sensible defaults if AI fails

**2. Context-Aware Mentoring**
- System: "You are an AI Learning Mentor helping students..."
- Includes student name, grade, subject, difficulty, and learning progress
- Provides personalized, grade-appropriate explanations
- Focuses on struggling areas while encouraging strengths

### Error Handling
- ✅ Input validation, timeout handling (15s), response validation
- ✅ Graceful fallbacks for all AI operations
- ✅ User-friendly error messages for different failure types
- ✅ Fallback goals and responses ensure system always works

## 📋 Minimum Features Implementation

### ✅ Student Enrollment & Authentication
- Create/update student records with demographics (grade, name, email)
- Login system for students and educators
- API endpoints: `POST/GET/PUT /students`

### ✅ Learning Path Assignment
- Create personalized paths with **AI-generated goals** (Grok)
- Assign content sequence with order and dates
- Auto-creates progress records for tracking
- API: `POST /learning-paths`

### ✅ Progress Tracking
- Real-time mastery level (0-100%) and completion percentage
- Status tracking (not started, in progress, completed)
- Time spent monitoring
- API: `GET/PUT /progress`

### ✅ Dual Dashboard System
**Students:** View paths, AI goals, progress stats, access AI Mentor
**Educators:** Monitor students, create paths, assign content, view analytics

### ✅ Educator Intervention
- View all students and their progress
- Detailed learning path breakdowns
- Identify struggling students via mastery metrics
- Access to AI-generated goals and recommended resources

## 🔧 Troubleshooting

### Common Issues

**AI Mentor not responding:**
- Verify `XAI_API_KEY` is set correctly
- Check backend console for error messages
- Ensure API key has valid credits

**Goals not generating:**
- Check xAI API status
- System uses fallback goals if AI fails
- Check Django logs for specific errors

**Frontend not loading data:**
- Verify backend is running on port 8000
- Check browser console for CORS errors
- Regenerate API client: `npm run generate-client`

## 📈 Future Enhancements

- Real-time AI-powered content recommendations
- Automated assessment generation
- Predictive analytics for at-risk students
- Multi-modal content support (video, audio)
- Collaborative learning features
- Parent/guardian dashboard

## 🏆 Evaluation Criteria Coverage

### ✅ Technical Implementation
- Clean, modular architecture
- Type-safe codebase with React Query
- RESTful API with OpenAPI documentation
- Responsive UI with modern design patterns

### ✅ Grok Integration
- **Context-aware prompting** with student progress data
- **Robust error handling** with graceful fallbacks
- **Response validation** ensures quality outputs
- **Multiple AI touchpoints:** goals generation + mentor chat

### ✅ User Experience
- Intuitive dashboards for students and educators
- Real-time progress visualization
- Seamless AI mentor integration
- Mobile-responsive design

### ✅ Feature Completeness
- All minimum features implemented
- Enhanced with AI-powered features
- Production-ready error handling
- Comprehensive progress tracking

### ✅ Documentation
- Complete README with setup instructions
- API documentation via OpenAPI
- Troubleshooting guide
- Demo credentials provided

### ✅ Presentation Points
- **AI Mentor** knows student's learning context and adapts responses
- **Personalized goals** generated by Grok for each learning path
- **Error resilience** ensures system works even if AI is unavailable
- **Data-driven insights** help educators identify intervention opportunities

---

**Built with ❤️ using Grok AI by xAI**
