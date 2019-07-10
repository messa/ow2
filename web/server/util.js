export function stripSlash(s) {
  return s.replace(/[/]$/, '')
}

export function asyncWrapper(f) {
  return (req, res, next) => f(req, res, next).catch(err => {
    console.error(err)
    res.statusCode = 500
    res.end('Internal Server Error')
  })
}
