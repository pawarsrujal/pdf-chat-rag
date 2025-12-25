import { useEffect } from 'react'
import { useRouter } from 'next/router'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    // TEMP: bypass auth, always go to dashboard
    router.push('/chat')
  }, [router])

  return <div>Loading...</div>
}