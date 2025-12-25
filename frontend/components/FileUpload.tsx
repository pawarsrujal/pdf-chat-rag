import { useState } from 'react'
import api from '@/services/api'

export default function FileUpload() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0])
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setMessage('')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const formData = new FormData()
      formData.append('file', file)
      console.log('Calling upload URL:', api.defaults.baseURL + '/upload')
      const response = await api.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      console.log('Response status:', response.status)
      console.log('Response data:', response.data)
      setMessage(`Successfully uploaded ${response.data.filename}`)
      setFile(null)
    } catch (error: any) {
      console.log('Error status:', error.response?.status)
      console.log('Error data:', error.response?.data)
      console.log('Error message:', error.message)
      setMessage(error.response?.data?.detail || error.message || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-4">
      <input
        type="file"
        accept=".pdf,.txt,.docx,.doc"
        onChange={handleFileChange}
        className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
      />
      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {uploading ? 'Uploading...' : 'Upload'}
      </button>
      {message && (
        <p className={`text-sm ${message.includes('Successfully') ? 'text-green-600' : 'text-red-600'}`}>
          {message}
        </p>
      )}
    </div>
  )
}