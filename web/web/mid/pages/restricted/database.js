import path from "path";
import { promises as fs } from "fs";

export async function getServerSideProps({ res }) {
  try {
    const dbPath = path.join(process.cwd(), "pages/api/restricted", "key.db");
    const buf = await fs.readFile(dbPath);
    res.setHeader("Content-Disposition", "attachment; filename=key.db");
    res.setHeader("Content-Type", "application/octet-stream");
    res.end(buf);
  } catch (e) {
    console.error(e);
    res.statusCode = 500;
    res.end("Error reading database file");
  }
  return { props: {} };
}

export default function DownloadDB() { return null; }
