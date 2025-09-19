const path = require('path')
const express = require('express')

const app = express()
const PORT = process.env.PORT || 3000

// Flag
const FLAG_VALUE = 'FLAG{l1f3_15_4b0ut_w1Nn1ng_50_50s}'

// The only accepted cookie value for TRACKING for flag
const EXPECTED_TRACKING = '6uNd3r_C0nTRol7'

// parse Cookie header
function parseCookie(header) {
  const out = {}
  if (!header) return out
  header.split(/;\s*/).forEach(kv => {
    const idx = kv.indexOf('=')
    if (idx > -1) out[kv.slice(0, idx)] = decodeURIComponent(kv.slice(idx + 1))
  })
  return out
}

// Serve static site from /public
app.use(express.static(path.join(__dirname, 'public')))

app.get('/flag.txt', (req, res) => {
  const cookies = parseCookie(req.headers.cookie || '')
  const tracking = cookies['TRACKING'] || ''

  if (tracking === EXPECTED_TRACKING) {
    // Correct cookie: send flag in header only
    res.set('X-CTF-Flag', FLAG_VALUE)
    return res
      .status(200)
      .type('text/html')
      .send(`
          <h1>I guess it is that simple</h1>
		  <p>I wasn't familiar with your game, here you go: <br><br></p>
          <p>
            Oh, I wish you'd stop and talk to me<br>
            How I wish you gone and walk away<br>
            Oh, I wish you'd stop and talk to me<br>
            Oh, I wish you'd stop and walk with me<br>
            Oh, where'd you go? I wanna know<br>
            Don't leave me stranded, leave me cold<br>
            Soul to be sold<br>
            Soul to be sold<br>
            Let me know, it's getting old<br>
            Who have we told? I don't know<br>
            Under control<br>
            Under control
          </p>

          <p>
            Oh, I wish you'd stop and talk to me<br>
            How I wish you gone and walk away<br>
            Oh, I wish you'd stop and talk to me<br>
            Oh, I wish you'd stop and walk with me<br>
            Oh, where'd you go? I wanna know<br>
            Don't leave me stranded, leave me cold<br>
            Soul to be sold<br>
            Soul to be sold<br>
            Let me know, it's getting old<br>
            Who have we told? I don't know<br>
            Under control<br>
            Under control<br><br>

            We don't need a reason<br>
            You part of the reason<br>
            That I can't feel it anymore<br>
            Body on the floor<br>
            There's blood on the floor<br>
            And you at my door<br>
            Something can't ignore
          </p>

          <p>
            Walk away<br>
            I don't wanna talk today<br>
            I can't do this every day<br>
            I don't wanna go insane<br>
            I don't wanna go insane<br>
            But the second that you talk to me<br>
            Is the second that I entertain<br>
            Is the second that I entertain
          </p>

          <p>
            Oh, I wish you'd stop and talk to me<br>
            How I wish you gone and walk away<br>
            Oh, I wish you'd stop and talk to me<br>
            Oh, I wish you'd stop and walk with me.
          </p>
        
      `)
  } else {
    // Wrong cookie do not include the flag header
    return res
      .status(200)
      .type('text/html')
      .send(`
          <h1>Not that simple, start digging twin</h1>
          <p>
			Since you're seeing this, you are probably lost. <br>
			Do you have everything under control? <br><br>
			
            Oh, I wish you'd stop and talk to me<br>
            How I wish you gone and walk away<br>
            Oh, I wish you'd stop and talk to me<br>
            Oh, I wish you'd stop and walk with me<br>
            Oh, where'd you go? I wanna know<br>
            Don't leave me stranded, leave me cold<br>
            Soul to be sold<br>
            Soul to be sold<br>
            Let me know, it's getting old<br>
            Who have we told? I don't know<br>
            Under control<br>
            Under control
          </p>

          
        
      `)
  }
})

// Start server
app.listen(PORT, () => {
  console.log(`Running on http://localhost:${PORT}`)
})
