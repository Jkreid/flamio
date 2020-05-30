module.exports = {
  entry: __dirname+'/src/app.tsx',
  output: {
    path: __dirname+'/src',
    filename: 'app.bundle.js'
  },
  module: {
    rules: [
      { test: /\.(ts|tsx)$/, loader: 'awesome-typescript-loader' }
    ]
  }
};
