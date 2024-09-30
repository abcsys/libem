const HtmlWebpackPlugin = require('html-webpack-plugin');
const path = require('path');
const webpack = require('webpack');
const dotenv = require('dotenv');

module.exports = () => {
  // call dotenv and it will return an Object with a parsed key 
  const env = dotenv.config({path: `${__dirname}/../arena.env`}).parsed;
  
  // reduce it to a nice object, the same as before
  const envKeys = Object.keys(env).reduce((prev, next) => {
    prev[`process.env.${next}`] = JSON.stringify(env[next]);
    return prev;
  }, {});

  return {
    entry: './index.js',
    mode: 'production',
    output: {
      path: path.resolve(__dirname, './dist'),
      filename: 'index_bundle.js',
      publicPath: '/',
    },
    target: 'web',
    devServer: {
      port: '5000',
      static: {
        directory: path.join(__dirname, 'public')
      },
      open: true,
      hot: true,
      liveReload: true,
      historyApiFallback: true,
    },
    resolve: {
      extensions: ['.js', '.jsx', '.json'],
    },
    module: {
      rules: [
        {
          test: /\.(js|jsx)$/, 
          exclude: /node_modules/, 
          use: 'babel-loader', 
        },
        {
          test: /\.css$/i,
          use: ["style-loader", "css-loader"],
        },
        {
          test: /\.(png|jpe?g|gif)$/i,
          use: [
            {
              loader: 'file-loader',
            },
          ],
        },
      ],
    },
    plugins: [
      new HtmlWebpackPlugin({
        template: path.join(__dirname, 'public', 'index.html'),
        favicon: "./public/favicon.ico"
      }),
      new webpack.DefinePlugin(envKeys)
    ]
  }
};
