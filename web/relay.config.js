module.exports = {
  // Configuration options accepted by the `relay-compiler` command-line tool and `babel-plugin-relay`.
  src: "./",
  schema: "./schema.graphql",
  artifactDirectory: "./.relay",
  exclude: [
    "**/node_modules/**",
    "**/.next/**",
    "**/__mocks__/**",
    "**/__generated__/**",
 ],
}
