import React from 'react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: any[]
  timestamp?: Date
}

interface ChatMessageProps {
  message: Message
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
        isUser
          ? 'bg-indigo-600 text-white'
          : 'bg-white text-gray-900 shadow-sm'
      }`}>
        <p className="whitespace-pre-wrap">{message.content}</p>
      </div>
    </div>
  )
}