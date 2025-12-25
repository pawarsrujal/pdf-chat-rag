import { NextApiRequest, NextApiResponse } from 'next'
import formidable from 'formidable'
import fs from 'fs'
import FormData from 'form-data'

export const config = {
  api: {
    bodyParser: false,
  },
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    const form = formidable({ multiples: false })

    form.parse(req, async (err, fields, files) => {
      if (err) {
        res.status(500).json({ error: 'Error parsing form' })
        return
      }

      const file = files.file as formidable.File
      if (!file) {
        res.status(400).json({ error: 'No file uploaded' })
        return
      }

      const formData = new FormData()
      formData.append('file', fs.createReadStream(file.filepath), {
        filename: file.originalFilename,
        contentType: file.mimetype,
      })

      try {
        const response = await fetch('http://localhost:8001/upload', {
          method: 'POST',
          body: formData,
          headers: {
            ...formData.getHeaders(),
          },
        })

        const data = await response.json()
        res.status(response.status).json(data)
      } catch (error) {
        res.status(500).json({ error: 'Proxy error' })
      }
    })
  } else {
    res.status(405).json({ message: 'Method not allowed' })
  }
}