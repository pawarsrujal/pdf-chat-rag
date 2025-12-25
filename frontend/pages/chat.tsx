import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/router'
import api from '@/services/api'
import ChatMessage from '@/components/ChatMessage'
import FileUpload from '@/components/FileUpload'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: any[]
  timestamp: Date
}

interface ChatState {
  messages: Message[]
  input: string
  isLoading: boolean
  sessionId: string | null
  role: string
  error: string | null
}

export default function Chat() {
  const [state, setState] = useState<ChatState>({
    messages: [],
    input: '',
    isLoading: false,
    sessionId: null,
    role: 'researcher',
    error: null
  })
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const router = useRouter()

  useEffect(() => {
    // TEMP: bypass auth check
    // const token = localStorage.getItem('token')
    // if (!token) {
    //   router.push('/login')
    // }
  }, [router])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [state.messages])

  const updateState = (updates: Partial<ChatState>) => {
    setState(prev => ({ ...prev, ...updates }))
  }

  const handleSend = async () => {
    if (!state.input.trim() || state.isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: state.input,
      timestamp: new Date()
    }

    updateState({
      messages: [...state.messages, userMessage],
      input: '',
      isLoading: true,
      error: null
    })

    try {
      const response = await api.post('/chat', {
        message: state.input,
        session_id: state.sessionId,
        role: state.role,
        top_k: 5,
        similarity_threshold: 0.5
      })

      const data = response.data

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        sources: response.data.sources,
        timestamp: new Date()
      }

      updateState({
        messages: [...state.messages, userMessage, assistantMessage],
        sessionId: response.data.session_id,
        isLoading: false
      })
    } catch (error: any) {
      updateState({
        error: error.response?.data?.detail || 'An error occurred. Please try again.',
        isLoading: false
      })
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    router.push('/login')
  }

  const handleRoleChange = (newRole: string) => {
    updateState({ role: newRole })
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <h1 className="text-2xl font-bold text-gray-900">AI Research Assistant</h1>
            <div className="flex items-center space-x-4">
              <select
                value={state.role}
                onChange={(e) => handleRoleChange(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded-md text-sm"
              >
                <option value="student">Student</option>
                <option value="researcher">Researcher</option>
                <option value="interview">Interview Prep</option>
              </select>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex flex-col">
          <div className="flex-1 overflow-y-auto p-4">
            <div className="max-w-4xl mx-auto space-y-4">
              {state.messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {state.isLoading && (
                <div className="flex justify-start">
                  <div className="bg-white rounded-lg p-4 shadow-sm">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                  </div>
                </div>
              )}
              {state.error && (
                <div className="flex justify-center">
                  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    {state.error}
                  </div>
                </div>
              )}
            </div>
            <div ref={messagesEndRef} />
          </div>

          <div className="border-t bg-white p-4">
            <div className="max-w-4xl mx-auto">
              <div className="flex space-x-4">
                <input
                  type="text"
                  value={state.input}
                  onChange={(e) => updateState({ input: e.target.value })}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Ask a question about your documents..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  disabled={state.isLoading}
                />
                <button
                  onClick={handleSend}
                  disabled={state.isLoading || !state.input.trim()}
                  className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {state.isLoading ? 'Sending...' : 'Send'}
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="w-80 bg-white border-l shadow-sm">
          <div className="p-4">
            <h2 className="text-lg font-semibold mb-4">Upload Documents</h2>
            <FileUpload />
          </div>
        </div>
      </div>
    </div>
  )
}