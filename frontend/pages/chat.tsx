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
  isDocumentUploading: boolean
  isDocumentReady: boolean
}

export default function Chat() {
  const [state, setState] = useState<ChatState>({
    messages: [],
    input: '',
    isLoading: false,
    sessionId: null,
    role: 'researcher',
    error: null,
    isDocumentUploading: false,
    isDocumentReady: false
  })

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const router = useRouter()

  // auto scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [state.messages])

  const updateState = (updates: Partial<ChatState>) => {
    setState(prev => ({ ...prev, ...updates }))
  }

  const handleUploadStart = () => {
    updateState({ isDocumentUploading: true, isDocumentReady: false })
  }

  const handleUploadComplete = (success: boolean) => {
    updateState({ isDocumentUploading: false, isDocumentReady: success })
  }

  // ---------------- SEND MESSAGE ----------------
  const handleSend = async () => {
    if (!state.input.trim() || state.isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: state.input,
      timestamp: new Date()
    }

    // 🔒 capture messages ONCE (fixes disappearing bug)
    const updatedMessages = [...state.messages, userMessage]

    updateState({
      messages: updatedMessages,
      input: '',
      isLoading: true,
      error: null
    })

    try {
      const response = await api.post('/chat', {
        message: userMessage.content,
        session_id: state.sessionId,
        role: state.role
      })

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.response,
        sources: response.data.sources,
        timestamp: new Date()
      }

      updateState({
        messages: [...updatedMessages, assistantMessage],
        sessionId: response.data.session_id,
        isLoading: false
      })
    } catch (error: any) {
      updateState({
        error: error.response?.data?.detail || 'An error occurred',
        isLoading: false
      })
    }
  }

  // ---------------- RESET CHAT ----------------
  const handleResetChat = async () => {
    try {
      await fetch('/api/reset', { method: 'POST' })

      updateState({
        messages: [],
        input: '',
        sessionId: null,
        error: null,
        isDocumentReady: false
      })

      alert('Chat reset. You can upload a new document.')
    } catch {
      alert('Failed to reset chat')
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    router.push('/login')
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* HEADER */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">AI Research Assistant</h1>

          <div className="flex items-center gap-3">
            <select
              value={state.role}
              onChange={e => updateState({ role: e.target.value })}
              className="px-3 py-1 border rounded text-sm"
            >
              <option value="student">Student</option>
              <option value="researcher">Researcher</option>
              <option value="interview">Interview Prep</option>
            </select>

            <button
              onClick={handleResetChat}
              className="px-4 py-2 text-sm bg-red-600 text-white rounded hover:bg-red-700"
            >
              Reset Chat
            </button>

            <button
              onClick={handleLogout}
              className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* BODY */}
      <div className="flex flex-1 overflow-hidden">
        {/* CHAT AREA */}
        <div className="flex-1 flex flex-col">
          <div className="flex-1 overflow-y-auto p-4">
            <div className="max-w-4xl mx-auto space-y-4">
              {state.messages.map(msg => (
                <ChatMessage key={msg.id} message={msg} />
              ))}

              {state.isLoading && (
                <div className="text-gray-400">Thinking…</div>
              )}

              {state.error && (
                <div className="text-red-600 bg-red-100 p-2 rounded">
                  {state.error}
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* INPUT */}
          <div className="border-t bg-white p-4">
            <div className="max-w-4xl mx-auto flex gap-4">
              <input
                value={state.input}
                onChange={e => updateState({ input: e.target.value })}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
                placeholder="Ask a question about your documents..."
                className="flex-1 px-4 py-2 border rounded"
                disabled={state.isLoading || state.isDocumentUploading || !state.isDocumentReady}
              />
              <button
                onClick={handleSend}
                disabled={state.isLoading || state.isDocumentUploading || !state.isDocumentReady || !state.input.trim()}
                className="px-6 py-2 bg-indigo-600 text-white rounded disabled:opacity-50"
              >
                Send
              </button>
            </div>
            {!state.isDocumentReady && !state.isDocumentUploading && (
              <div className="text-gray-400 text-sm px-4">Please upload a document to start chatting.</div>
            )}
            {state.isDocumentUploading && (
              <div className="text-gray-400 text-sm px-4">Processing document, please wait...</div>
            )}
          </div>
        </div>

        {/* SIDEBAR */}
        <aside className="w-80 bg-white border-l p-4">
          <h2 className="text-lg font-semibold mb-4">Upload Documents</h2>
          <FileUpload onUploadStart={handleUploadStart} onUploadComplete={handleUploadComplete} />
        </aside>
      </div>
    </div>
  )
}
