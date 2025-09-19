const path = require('path')
const express = require('express')

const app = express()
const PORT = process.env.PORT || 3000

// Flag
const FLAG_VALUE = 'FLAG{sh0uldv3_k3pt_my_w0rd_0n_th3_t1p_0f_my_t0ngu3}'

// Serve static site from /public
app.use(express.static(path.join(__dirname, 'public')))

app.get('/flag.txt', (req, res) => {
    res.set('X-CTF-Flag', FLAG_VALUE)
    return res
      .status(200)
      .type('text/html')
      .send(`
          <h1> Here's the flag: **************************** </h1>
		  <p>If you can't see it give it a couple of hours</p>
        
      `)
  })

// Start server
app.listen(PORT, () => {
  console.log(`Running on http://localhost:${PORT}`)
})
