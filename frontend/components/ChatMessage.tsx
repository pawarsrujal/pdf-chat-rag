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
        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 p-3 bg-gray-50 rounded-md">
            <p className="text-sm font-semibold text-gray-700 mb-2">Sources:</p>
            <div className="space-y-2">
              {message.sources.map((source, index) => (
                <div key={index} className="text-sm text-gray-600">
                  <div className="flex justify-between items-start">
                    <span className="font-medium">{source.document_name}</span>
                    <span className="text-xs text-gray-500">Score: {source.score}</span>
                  </div>
                  {source.page_number && (
                    <p className="text-xs text-gray-500">Page {source.page_number}</p>
                  )}
                  <p className="mt-1 text-xs italic">"{source.content}"</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}