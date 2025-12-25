import { useEffect } from 'react'
import { useRouter } from 'next/router'

export default function Login() {
  const router = useRouter()

  useEffect(() => {
    // TEMP: bypass auth, redirect to dashboard
    router.push('/chat')
  }, [router])

  return <div>Redirecting to dashboard...</div>
}