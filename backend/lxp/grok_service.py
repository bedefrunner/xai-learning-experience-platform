"""
Grok AI Service - Integration with xAI's Grok API
"""
import os
from openai import OpenAI


class GrokService:
    """Service for interacting with Grok AI via xAI API."""

    def __init__(self):
        api_key = os.getenv('XAI_API_KEY', 'your_xai_api_key_here')

        # xAI API is compatible with OpenAI's format
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )
        self.model = "grok-4-latest"  # Use latest Grok model

    def chat(self, user_message: str, system_context: str = None, student_context: dict = None) -> str:
        """
        Send a message to Grok and get a response with comprehensive error handling.

        Args:
            user_message: The student's question/message
            system_context: System context about the student's learning
            student_context: Additional context (grade, subject, etc.)

        Returns:
            Grok's response as a string
        """
        # Validate input
        if not user_message or not user_message.strip():
            return "I didn't receive a question. What would you like to know?"

        # Build system message with context
        system_message = "You are an AI Learning Mentor helping students with their studies. "
        system_message += "You should be encouraging, patient, and provide clear explanations tailored to the student's level. "
        system_message += "Keep responses concise (2-3 paragraphs) and actionable. "

        if student_context:
            if 'student_name' in student_context:
                system_message += f"Address the student as {student_context['student_name']}. "
            if 'student_grade' in student_context:
                system_message += f"The student is in grade {student_context['student_grade']}. "
            if 'subject' in student_context:
                system_message += f"They are currently studying {student_context['subject']}. "
            if 'difficulty' in student_context:
                system_message += f"The difficulty level is {student_context['difficulty']}. "

        if system_context:
            system_message += f"\n\nCurrent learning context: {system_context}"

        try:
            # Call Grok API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=500,
                timeout=15.0,  # 15 second timeout
            )

            # Validate response
            if not completion.choices or len(completion.choices) == 0:
                raise ValueError("No response choices returned from API")

            response_content = completion.choices[0].message.content

            if not response_content or not response_content.strip():
                raise ValueError("Empty response content from API")

            # Check for inappropriate or error responses
            response_lower = response_content.lower()
            if any(phrase in response_lower for phrase in ['i cannot', 'i\'m unable to', 'against my programming']):
                print(f"Grok refused to answer: {response_content}")
                return "I'd be happy to help with your studies! Could you rephrase your question or ask about a specific topic you're learning?"

            return response_content.strip()

        except Exception as e:
            # Log the specific error
            error_type = type(e).__name__
            print(f"Grok API Error ({error_type}): {str(e)}")

            # Provide context-specific fallback responses
            if 'timeout' in str(e).lower():
                return "I'm taking a bit longer to think. Could you try asking your question again?"
            elif 'api_key' in str(e).lower() or 'authentication' in str(e).lower():
                return "I'm having trouble connecting to my knowledge base. Please let your teacher know."
            elif 'rate_limit' in str(e).lower():
                return "I'm getting too many questions right now. Please wait a moment and try again."
            else:
                return f"I encountered an issue, but I'm here to help! Could you try rephrasing your question?"

    def generate_personalized_goals(self, student_grade: int, subject: str, difficulty: str) -> list:
        """
        Generate personalized learning goals using Grok with validation.

        Args:
            student_grade: Student's grade level
            subject: Subject being studied
            difficulty: Difficulty level (beginner, intermediate, advanced)

        Returns:
            List of 3-5 personalized learning goals
        """
        # Validate inputs
        if not subject or not isinstance(student_grade, int) or student_grade < 1:
            return self._get_fallback_goals(subject, difficulty)

        prompt = f"""Generate exactly 4 specific, measurable, and achievable learning goals for a grade {student_grade} student
studying {subject} at a {difficulty} level. Each goal should be:
- One clear sentence
- Grade-appropriate
- Focused on mastery and understanding
- Actionable for the student

Format: Return ONLY a bulleted list with exactly 4 goals, each starting with a dash (-)."""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert educational curriculum designer creating personalized learning goals."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=400,
                timeout=10.0,
            )

            # Validate response structure
            if not completion.choices or len(completion.choices) == 0:
                raise ValueError("No response from API")

            response = completion.choices[0].message.content

            if not response or not response.strip():
                raise ValueError("Empty response from API")

            # Parse bullet points into list with validation
            lines = response.split('\n')
            goals = []

            for line in lines:
                line = line.strip()
                # Handle various bullet formats: -, *, •, 1., etc.
                if line and (line.startswith('-') or line.startswith('*') or line.startswith('•') or (line[0].isdigit() and '.' in line[:3])):
                    # Clean up the goal text
                    goal = line.lstrip('-*•0123456789. ').strip()
                    if goal and len(goal) > 10:  # Ensure meaningful content
                        goals.append(goal)

            # Validate we got enough goals
            if len(goals) >= 3:
                return goals[:5]  # Return max 5 goals
            else:
                print(f"Grok returned insufficient goals ({len(goals)}): {goals}")
                return self._get_fallback_goals(subject, difficulty)

        except Exception as e:
            error_type = type(e).__name__
            print(f"Grok API Error in generate_personalized_goals ({error_type}): {str(e)}")
            return self._get_fallback_goals(subject, difficulty)

    def _get_fallback_goals(self, subject: str, difficulty: str) -> list:
        """Generate fallback goals when AI is unavailable."""
        subject_name = subject if subject else "the subject"
        return [
            f"Understand and master core concepts in {subject_name}",
            f"Complete all assigned content at {difficulty} level with 80%+ accuracy",
            f"Apply {subject_name} knowledge to solve real-world problems",
            "Demonstrate mastery through assessments and projects"
        ]

    def generate_assessment_feedback(self, score: float, subject: str, questions_missed: list = None) -> str:
        """Generate personalized feedback for an assessment."""
        prompt = f"""A student scored {score}% on a {subject} assessment. """
        if questions_missed:
            prompt += f"They struggled with: {', '.join(questions_missed)}. "
        prompt += "Provide encouraging, specific feedback (2-3 sentences) on how to improve."

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200,
            )

            return completion.choices[0].message.content
        except Exception as e:
            print(f"Grok API Error: {e}")
            # Fallback feedback
            if score >= 80:
                return f"Great job! You scored {score}% which shows strong understanding. Keep up the excellent work!"
            elif score >= 60:
                return f"You scored {score}%. You're on the right track! Review the areas you found challenging and try some practice problems."
            else:
                return f"You scored {score}%. Don't worry - learning takes time! Let's focus on understanding the fundamentals. I'm here to help if you have questions."


# Singleton instance
grok_service = GrokService()
