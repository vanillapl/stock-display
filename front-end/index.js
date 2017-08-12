/**
 * Created by xuenanli on 8/11/17.
 */

var express = require('express');
var app = express();
var server = require('http').createServer(app);
var redis = require('redis');

app.use(express.static(__dirname + 'public'));
app.use('/jquery', express.static(__dirname + '/node_modules/jquery/dist/'));

// - get command-line args
argv = require('minimist')(process.argv.slice(2));
var redis_host = argv['redis_host'];
var redis_port = argv['redis_port'];
var sub_channel = argv['channel'];

var redis_client = redis.createClient(redis_port, redis_host);
redis_client.subscribe(sub_channel);
redis_client.on('message', function (channel, message) {
    if (channel == sub_channel) {
        console.log('receive %s', message)
    }
});



// - set up shutdown_hook


server.listen(8080, function () {
    console.log('server start at port 8080')
});