$(function() {
    var socket = io.connect();
    var data_points = [];
    var symbol_list = [];
    // - Whenever the server emits 'data', update the flow graph
    socket.on('data', function(data) {
    	newDataCallback(data);
    });

    $('#chart-options').change(function() {
        var option = $(this).val();
        if(option == 1) {
            $('#add-field').show();
            $('#stock-list a').removeClass('active');
            $('#k-container').hide('slow');
            $('#r-container svg').show('slow');
        }
        else if (option == 2) {
            $('#add-field').hide();
            $('#r-container svg').hide('slow');
            $('#k-container').show('slow');
            if(symbol_list.length > 0) {
                var symbol = symbol_list[0];
                // console.log(symbol);
                $('a:contains(' + symbol + ')').addClass('active');
                var dateperiod = [2017,1,1,2017,1,9];
                socket.emit('initpastdata', symbol, dateperiod);
                socket.on('databack', function(data) {
                    // console.log(data);
                    showHistoricalData(symbol, data);
                });
            } else {
                $('#k-container').text('NO DATA')
            }
        }
    });

    function showHistoricalData(symbol, data) {
        // split the data set into ohlc and volume
        var ohlc = [],
            volume = [],
            dataLength = data.length,
            // set the allowed units for data grouping
            groupingUnits = [[
                'week',                         // unit name
                [1]                             // allowed multiples
            ], [
                'month',
                [1, 2, 3, 4, 6]
            ]],

            i = 0;

        for (i; i < dataLength; i += 1) {
            ohlc.push([
                data[i][0], // the date
                data[i][1], // open
                data[i][2], // high
                data[i][3], // low
                data[i][4] // close
            ]);

            volume.push([
                data[i][0], // the date
                data[i][5] // the volume
            ]);
        }

        // create the chart
        Highcharts.stockChart('k-container', {

            rangeSelector: {
                selected: 1
            },

            title: {
                text: symbol + ' Historical'
            },

            yAxis: [{
                labels: {
                    align: 'right',
                    x: -3
                },
                title: {
                    text: 'OHLC'
                },
                height: '60%',
                lineWidth: 2
            }, {
                labels: {
                    align: 'right',
                    x: -3
                },
                title: {
                    text: 'Volume'
                },
                top: '65%',
                height: '35%',
                offset: 0,
                lineWidth: 2
            }],

            tooltip: {
                split: true
            },

            series: [{
                type: 'candlestick',
                name: symbol,
                data: ohlc,
                dataGrouping: {
                    units: groupingUnits
                }
            }, {
                type: 'column',
                name: 'Volume',
                data: volume,
                yAxis: 1,
                dataGrouping: {
                    units: groupingUnits
                }
            }]
        });
    }

    function newDataCallback(message) {
        "use strict";
        var parsed = JSON.parse(message);
        var timestamp = parsed['timestamp'];
        var average = parsed['average'];
        var symbol = parsed['symbol'];
        var point = {};
        point.x = timestamp;
        point.y = average;

        // console.log(point);

        var i = getSymbolIndex(symbol, data_points);

        data_points[i].values.push(point);
        if (data_points[i].values.length > 100) {
            data_points[i].values.shift();
        }
        loadGraph();
    }

    function formatDateTick(time) {
        "use strict";
        var date = new Date(time * 1000);
        return d3.time.format('%H:%M:%S')(date);
    }

    $("#chart").height($(window).height() - $("#header").height() * 2);

    $(document.body).on('click', '.stock-label', function () {
        var option = $('#chart-options').val();
        if(option == 1) {
            var symbol = $(this).text();
            $.ajax({
                url: 'http://localhost:5000/' + symbol,
                type: 'DELETE'
            });

            $(this).remove();
            var index = symbol_list.indexOf(symbol);
            if (index > -1) {
                symbol_list.splice(index, 1);
            }
            var i = getSymbolIndex(symbol, data_points);
            data_points.splice(i, 1);
        }
        if(option == 2) {
            $(this).addClass('active').siblings().removeClass('active');
            var symbol = $(this).text();
            var dateperiod = [2017,1,1,2017,1,9];
            socket.emit('initpastdata', symbol, dateperiod);
            socket.on('databack', function(data) {
                // console.log(data);
                showHistoricalData(symbol, data);
            });
        }
    });

    $("#add-stock-button").click(function () {
        "use strict";
        var symbol = $("#stock-symbol").val();

        $.ajax({
            url: 'http://localhost:5000/' + symbol,
            type: 'POST'
        });

        $("#stock-symbol").val("");
        data_points.push({
            values: [],
            key: symbol
        });

        $("#stock-list").append(
            "<a class='stock-label list-group-item small'>" + symbol + "</a>"
        );
        symbol_list.push(symbol)
        // console.log(data_points);
    });

    var chart = nv.models.lineChart()
        .interpolate('monotone')
        .margin({
            bottom: 100
        })
        .useInteractiveGuideline(true)
        .showLegend(true)
        .color(d3.scale.category10().range());

    chart.xAxis
        .axisLabel('Time')
        .tickFormat(formatDateTick);

    chart.yAxis
        .axisLabel('Price');

    // window.setInterval(nv.addGraph(loadGraph), 5000);
    nv.addGraph(loadGraph);
    function loadGraph() {
        "use strict";
        d3.select('#r-container svg')
            .datum(data_points)
            .transition()
            .duration(5)
            .call(chart);
        if($('#chart-options').val() == 1) {
            nv.utils.windowResize(chart.update);
        }
        // console.log(chart);
        return chart;
    }

    function getSymbolIndex(symbol, array) {
        "use strict";
        for (var i = 0; i < array.length; i++) {
            if (array[i].key == symbol) {
                return i;
            }
        }
        return -1;
    }
});
