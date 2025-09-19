export default function Fix() {
  return (
    <main className="container">
      <h1 style={{ color: "#f87171" }}>⚠️ Security Notice ⚠️</h1>
      <p>
        Our team has identified an issue with the <code>/restricted</code> portal.
      </p>
      <p>
        Until further notice, customers should not attempt to access restricted
        resources as it exposes sensitive information and is currently under
        review by our security engineers.
      </p>
      <p>
        We appreciate your patience while we work to resolve this issue and
        release an update. A patch is scheduled for deployment shortly.
      </p>

      <div style={{ marginTop: "2rem", padding: "1rem", background: "#1e293b", borderRadius: "7px" }}>
        <strong>Reminder:</strong> Please await until further notice
      </div>
    </main>
  )
}
