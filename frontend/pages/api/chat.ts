import { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    try {
      const response = await fetch('http://localhost:8001/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(req.body),
      })

      const data = await response.json()
      res.status(response.status).json(data)
    } catch (error) {
      res.status(500).json({ error: 'Proxy error' })
    }
  } else {
    res.status(405).json({ message: 'Method not allowed' })
  }
}