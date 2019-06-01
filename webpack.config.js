const path = require('path');
const css_extract = require('mini-css-extract-plugin');
const copy_plugin = require('copy-webpack-plugin');

const dev_mode = process.env.NODE_ENV === 'development';

module.exports = {
    plugins: [
        new css_extract({
            // Options similar to the same options in webpackOptions.output
            // both options are optional
            filename: '[name].css',
            chunkFilename: '[id].css',
        }),
        new copy_plugin([
            { from: './assets/img/favicon.ico' },
        ])
    ],

    entry: {
        main: './assets/js/main.js',
    },
    output: {
        publicPath: '/static/',
        path: path.resolve(__dirname, 'mcarch/static'),
        filename: '[name].js'
    },
    mode: dev_mode ? 'development' : 'production',

    module: {
        rules: [
            {
                test: /\.scss$/,
                use: [
                    {
                        loader: css_extract.loader,
                        options: {
                            hmr: dev_mode,
                        },
                    },
                    "css-loader",
                    "sass-loader"
                ],
            },
            {
                test: /\.(png|svg|jpg|gif)$/,
                use: [
                    'file-loader'
                ]
            },
        ],
    },
};

