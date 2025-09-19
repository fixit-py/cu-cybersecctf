import path from "path"
import { promises as fs } from "fs"

export default async function handler(req, res) {
  const filePath = path.join(process.cwd(), "pages/api", "CrypTechUtility.py")
  try {
    const fileBuffer = await fs.readFile(filePath)

    res.setHeader("Content-Disposition", "attachment; filename=CrypTechUtility.py")
    res.setHeader("Content-Type", "application/octet-stream")
    res.send(fileBuffer)
  } catch (err) {
    console.error(err)
    res.status(500).send("Error Downloading File")
  }
}