function getPastData(sy,sm,sd,ey,em,ed) {
    var spawn = require("child_process").spawn;
    var py = spawn('python',["fi.py", sy, sm, sd, ey, em, ed]);
    var data = []
    py.stdout.on('data', function (d){
        var s = d.toString().substring(1, d.length-1).split('], [')
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
        console.log(data);
       return data;
    });
}
console.log(getHistoricalData(2010,1,1,2010,1,9))
