// debug

export default function(req, res) {
  res.json({
    heaers: req.headers,
    cookies: req.cookies,
  })
}