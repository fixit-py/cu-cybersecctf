export async function getServerSideProps({res}) {
  res.setHeader("Content-Type", "text/plain")
  res.write("User-agent: *\nDisallow: /restricted")
  res.end()
  return { props: {} }
}

export default function Robots() {
  return null
}