module.exports = {
  entry: __dirname+'/src/app/app.tsx',
  output: {
    path: __dirname+'/src/app',
    filename: 'app.bundle.js'
  },
  module: {
    rules: [
      { test: /\.(ts|tsx)$/, loader: 'awesome-typescript-loader' }
    ]
  }
};
