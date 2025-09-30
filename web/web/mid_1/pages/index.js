export default function Home() {
  return (
    <main className="container">
      <header>
        <h1>CrypTech Secure Systems</h1>
        <p className="tagline">Enterprise Windows Encryption Solutions</p>
      </header>

      <section>
        <h2>Our Mission</h2>
        <p>
          At CrypTech, we believe that data security should be simple, powerful,
          and seamless. Our encryption solutions are built to protect sensitive
          enterprise data at rest and in transit — without slowing down your business.
        </p>
      </section>

      <section>
        <h2>What We Offer</h2>
        <ul>
		  <li><strong>Open Source</strong> Encryption/Decryption solutions</li>
          <li>Full-disk encryption for Windows environments</li>
          <li>Centralized key management and recovery</li>
          <li>Transparent integration with enterprise workflows</li>
        </ul>
      </section>

      <section>
        <h2>What Our Clients Say</h2>
        <div className="reviews">
          <blockquote>
            <p>
              “Saved our company from an internal breach with their secure encryption/decryption utility”
            </p>
            <footer>— Alex, CEO of Glaze Inc.</footer>
          </blockquote>

          <blockquote>
            <p>
              “Amazing encryption solution that can keep everyone at ease!”
            </p>
            <footer>— Maria, CSO of CuCyberSec</footer>
          </blockquote>

          <blockquote>
            <p>
              “It's alright I guess. Maybe...” </p>
		  <div
              dangerouslySetInnerHTML={{
            __html: `<!--Note to devs, fix the portal-->`,
			}}
            />
		  <meta
          
        />
            
            <footer>— Sobbing, Developer at Next.js</footer>
          </blockquote>
        </div>
      </section>

      <footer style={{ marginTop: "2rem", fontSize: "0.9rem", color: "#94a3b8" }}>
        &copy; 2077 CrypTech Secure Systems. All rights reserved.
      </footer>
    </main>
  )
}
