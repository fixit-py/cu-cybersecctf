export default function RestrictedHome() {
  return (
    <main className="container">
      <h1>Internal Access</h1>
      <p>
        Welcome to the CrypTech Secure Systems
      </p>
      <ul>
        <li><a href="/restricted/flag">flag</a></li>
        <li><a href="/restricted/database">Database</a></li>
      </ul>
    </main>
  )
}