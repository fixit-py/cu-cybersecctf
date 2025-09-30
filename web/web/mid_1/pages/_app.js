import '../styles.css'
import Link from 'next/link'

export default function MyApp({ Component, pageProps }) {
  return (
    <>
      <nav className="navbar">
        <Link href="/"> Home &ensp;|</Link>
        <Link href="/about">&ensp; About &ensp;</Link>
        <Link href="/fix">|&ensp; Portal &ensp;</Link>
      </nav>
      <Component {...pageProps} />
    </>
  )
}