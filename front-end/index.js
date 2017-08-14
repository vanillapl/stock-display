// - get command line arguments
var argv = require('minimist')(process.argv.slice(2));
var port = argv['port'];
var redis_host = argv['redis_host'];
var redis_port = argv['redis_port'];
var subscribe_topic = argv['subscribe_topic'];
// - setup dependency instances
var express = require('express');
var app = express();
var server = require('http').createServer(app);
var io = require('socket.io')(server);

// - setup redis client
var redis = require('redis');
console.log('Creating a redis client');
var redisclient = redis.createClient(redis_port, redis_host);
redisclient.subscribe(subscribe_topic);
console.log('Subscribing to redis topic %s', subscribe_topic);
redisclient.on('message', function (channel, message) {
    if (channel == subscribe_topic) {
        // console.log('message received %s', message);
        io.sockets.emit('data', message);
    }
});

// - setup webapp routing
app.use(express.static(__dirname + '/public'));
app.use('/jquery', express.static(__dirname + '/node_modules/jquery/dist/'));
app.use('/d3', express.static(__dirname + '/node_modules/d3/build/'));
app.use('/nvd3', express.static(__dirname + '/node_modules/nvd3/build/'));
app.use('/bootstrap', express.static(__dirname + '/node_modules/bootstrap/dist'));

server.listen(port, function () {
    console.log('Server started at port %d.', port);
});

io.on('connect', function(socket){
    socket.on('initpastdata', function(symbol, dateperiod) {
        // console.log("received time period"+dateperiod);
        getHistoricalData(symbol, dateperiod, function(data) {
            // console.log(data);
            socket.emit('databack', data);
        });
    })
});

function getHistoricalData(symbol, dateperiod, callback) {
    var [sy, sm, sd, ey, em, ed] = dateperiod;
    var spawn = require("child_process").spawn;
    var py = spawn('python',["fi.py", symbol, sy, sm, sd, ey, em, ed]);
    var data = []
    py.stdout.on('data', function(d){
        var s = d.toString().substring(1, d.length-1).split('], [')
        // console.log(s[0])
        s[0] = s[0].substring(1)
        s[s.length-1] = s[s.length-1].slice(0,-1)
        for(var i = 0; i < s.length; i++){
            var ss = s[i].split(',')
            tmp = []
            for(var j = 0; j < ss.length; j++){
                tmp.push(parseFloat(ss[j]));
            }
            data.push(tmp)
        }
    });
    py.stdout.on('end', function(){
        // console.log(data);
        callback(data)
    });
}

// - setup shutdown hooks
var shutdown_hook = function () {
    console.log('Quitting redis client');
    redisclient.quit();
    console.log('Shutting down app');
    process.exit();
};

process.on('SIGTERM', shutdown_hook);
process.on('SIGINT', shutdown_hook);
process.on('exit', shutdown_hook);
