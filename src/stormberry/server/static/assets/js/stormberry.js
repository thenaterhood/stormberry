type = ['','info','success','warning','danger'];
weather_descriptions = {
        "extreme-heat": "Extremely hot. Avoid going outdoors for long periods.",
        "dangerous-heat": "Hot. Take precautious for being outdoors for extended periods.",
        "uncomfortable-heat": "Uncomfortably hot.",
        "hot": "Uncomfortable.",
        "comfortable": "It's nice out.",
        "cool": "Consider wearing a jacket.",
        "cold": "It's coat weather.",
        "uncomfortable-cold": "It's very cold. Minimize exposed skin.",
        "dangerous-cold": "Dangerous cold. Minimize time outside."
};
forecast_descriptions = {
        "fair": "Fair weather inbound.",
        "cloudy-and-warm": "Expect clouds and warmer weather.",
        "more-of-the-same": "Weather should be consistent.",
        "little-change": "Expect little change in conditions.",
        "precipitation-likely": "Precipitation is likely.",
        "clearing-and-cool": "Expect clouds to clear and a drop in temperature.",
        "precipitation": "Expect precipitation.",
        "storms": "Possible storms inbound."
};


stormberry = {

    ctof: function(celsius){
        return (celsius * 1.8) + 32;
    },

    displayLatestCondition: function(){
        $.getJSON('/weather/latest-reading', {}, function(data) {
            $('.current-temp').text(data.tempc.toFixed(1));
            $('.current-temp-f').text(stormberry.ctof(data.tempc).toFixed(1));
            $('.current-humidity').text(data.humidity);
            $('.current-pressure').text(data.inchesHg);
            $('.current-dewpoint').text(data.dewpointc.toFixed(1));
            $('.current-dewpoint-f').text(stormberry.ctof(data.dewpointc).toFixed(1));
            $('.latest-datapoint-time').text(data.timestr);
        });
    },

    displayLatestComfort: function(){
        $.getJSON('/comfort/now', {}, function(data) {
            if (weather_descriptions.hasOwnProperty(data.comfort_safety_str)) {
                    $('.current-comfort').text(weather_descriptions[data.comfort_safety_str]);
            } else {
                    $('.current-comfort').text(data.comfort_safety_str);
            }

            if (data.safe_to_run == "yes") {
                    $('.safe-to-run').text("It's currently safe to go running.");
            } else if (data.safe_to_run == "with-caution") {
                    $('.safe-to-run').text("You can go running, but with caution.");
            } else {
                    $('.safe-to-run').text("It's currently inadvisable to go running.");
            }

            $('.sc-method').text(data.method);
            $('.sc-value').text(data.comfort_safety_value.toFixed(1));
        });
    },

    displayBasicPrediction: function(){
        $.getJSON('/predict/basic', {}, function(data) {
            if (forecast_descriptions.hasOwnProperty(data.prediction)) {
                    $('.basic-prediction').text(forecast_descriptions[data.prediction]);
            } else {
                    $('.basic-prediction').text(data.prediction);
            }

            if (data.tempc_trend < 0) {
                    $('.basic-temp-trend').text("The temperature is falling.");
            } else if (data.tempc_trend == 0) {
                    $('.basic-temp-trend').text("The temperature is staying the same.");
            } else if (data.tempc_trend > 0) {
                    $('.basic-temp-trend').text("The temperature is rising.");
            }
        });
    },

    initPickColor: function(){
        $('.pick-class-label').click(function(){
            var new_class = $(this).attr('new-class');
            var old_class = $('#display-buttons').attr('data-class');
            var display_div = $('#display-buttons');
            if(display_div.length) {
                var display_buttons = display_div.find('.btn');
                display_buttons.removeClass(old_class);
                display_buttons.addClass(new_class);
                display_div.attr('data-class', new_class);
            }
        });
    },

    initFormExtendedDatetimepickers: function(){
        $('.datetimepicker').datetimepicker({
            icons: {
                time: "fa fa-clock-o",
                date: "fa fa-calendar",
                up: "fa fa-chevron-up",
                down: "fa fa-chevron-down",
                previous: 'fa fa-chevron-left',
                next: 'fa fa-chevron-right',
                today: 'fa fa-screenshot',
                clear: 'fa fa-trash',
                close: 'fa fa-remove'
            }
        });
    },

    initConditionCharts: function(){


        $.getJSON('/weather/past-day', {}, function(data) {
            var dewpointLabels = [];
            var dewpointValues = [];

            var tempLabels = [];
            var tempValues = [];

            var pressureLabels = [];
            var pressureValues = [];


            for (var i = 0, len = data.length; i < len; i++) {
                dewpointLabels.push(data[i].timestr);
                dewpointValues.push(parseFloat(data[i].dewpointc));

                tempLabels.push(data[i].timestr);
                tempValues.push(data[i].tempc);

                pressureLabels.push(data[i].timestr);
                pressureValues.push(data[i].inchesHg);
            }
            dewpointData = {
                    "x": dewpointLabels,
                    "y": dewpointValues,
                    "type": "scatter",
                    "name": "Dewpoint"
            };
            tempData = {
                    "x": tempLabels,
                    "y": tempValues,
                    "type": "scatter",
                    "name": "Temperature"
            };
            pressureData = {
                    "x": pressureLabels,
                    "y": pressureValues,
                    "type": "scatter",
                    "name": "Pressure"
            };
            Plotly.newPlot('hourlyDewpointChart', [dewpointData, tempData, pressureData]);

        });

    },

    displayWeeklyTrends: function(){
        $.getJSON('/weather/past-week/trend', {}, function(data) {
            temp_icon = 'trending_flat';
            if (data.tempc_trend < 0) {
                temp_icon = 'trending_down';
            } else if (data.tempc_trend > 0) {
                temp_icon = 'trending_up';
            }

            $('.week-temp-trend').text(temp_icon);

            pressure_icon = 'trending_flat';
            if (data.pressure_trend < 0) {
                pressure_icon = 'trending_down';
            } else if (data.pressure_trend > 0) {
                pressure_icon = 'trending_up';
            }

            $('.week-pressure-trend').text(pressure_icon);

            dewpoint_icon = 'trending_flat';
            if (data.dewpoint_trend < 0) {
                dewpoint_icon = 'trending_down';
            } else if (data.pressure_trend > 0) {
                dewpoint_icon = 'trending_up';
            }

            $('.week-dewpoint-trend').text(dewpoint_icon);
        });
    },

    displayWeeklyCharts: function(){


        $.getJSON('/weather/past-week', {}, function(data) {
            var dewpointLabels = [];
            var dewpointValues = [];

            var tempLabels = [];
            var tempValues = [];

            var pressureLabels = [];
            var pressureValues = [];


            for (var i = 0, len = data.length; i < len; i++) {
                dewpointLabels.push(data[i].datestr);
                dewpointValues.push(parseFloat(data[i].dewpointc));

                tempLabels.push(data[i].datestr);
                tempValues.push(data[i].tempc);

                pressureLabels.push(data[i].datestr);
                pressureValues.push(data[i].inchesHg);
            }

            chartOptions = {
                lineSmooth: Chartist.Interpolation.cardinal({
                    tension: 0
                }),
                //low: Math.min.apply(null, dewpointValues),
                //high: Math.max.apply(null, dewpointValues), // creative tim: we recommend you to set the high sa the biggest value + something for a better look
                chartPadding: { top: 0, right: 0, bottom: 0, left: 0},
                axisX: {
                    showLabel: false
                },
            }

            // ====== Dewpoint Chart =======
            dataWeeklyDewpointChart = {
                labels: dewpointLabels,
                series: [
                    dewpointValues
                ]
            };


            var weeklyDewpointChart = new Chartist.Line('#weeklyDewpointChart', dataWeeklyDewpointChart, chartOptions);


            // ====== Pressure Chart ======
            dataWeeklyPressureChart = {
                labels: pressureLabels,
                series: [
                    pressureValues
                ]
            };


            var weeklyPressureChart = new Chartist.Line('#weeklyPressureChart', dataWeeklyPressureChart, chartOptions);


            // ====== Temperature Chart ======
            dataWeeklyTempChart = {
                labels: tempLabels,
                series: [
                    tempValues
                ]
            };

            var weeklyTempChart = new Chartist.Line('#weeklyTempChart', dataWeeklyTempChart, chartOptions);

            // Run all the chart animations
            //md.startAnimationForLineChart(hourlyDewpointChart);
            //md.startAnimationForLineChart(hourlyPressureChart);
            //md.startAnimationForLineChart(hourlyTempChart);
        });

    },


    initDashboardPageCharts: function(){

        /* ----------==========     Daily Sales Chart initialization    ==========---------- */

        dataDailySalesChart = {
            labels: ['M', 'T', 'W', 'T', 'F', 'S', 'S'],
            series: [
                [12, 17, 7, 17, 23, 18, 38]
            ]
        };

        optionsDailySalesChart = {
            lineSmooth: Chartist.Interpolation.cardinal({
                tension: 0
            }),
            low: 0,
            high: 50, // creative tim: we recommend you to set the high sa the biggest value + something for a better look
            chartPadding: { top: 0, right: 0, bottom: 0, left: 0},
        }

        var dailySalesChart = new Chartist.Line('#dailySalesChart', dataDailySalesChart, optionsDailySalesChart);

        md.startAnimationForLineChart(dailySalesChart);



        /* ----------==========     Completed Tasks Chart initialization    ==========---------- */

        dataCompletedTasksChart = {
            labels: ['12am', '3pm', '6pm', '9pm', '12pm', '3am', '6am', '9am'],
            series: [
                [230, 750, 450, 300, 280, 240, 200, 190]
            ]
        };

        optionsCompletedTasksChart = {
            lineSmooth: Chartist.Interpolation.cardinal({
                tension: 0
            }),
            low: 0,
            high: 1000, // creative tim: we recommend you to set the high sa the biggest value + something for a better look
            chartPadding: { top: 0, right: 0, bottom: 0, left: 0}
        }

        var completedTasksChart = new Chartist.Line('#completedTasksChart', dataCompletedTasksChart, optionsCompletedTasksChart);

        // start animation for the Completed Tasks Chart - Line Chart
        md.startAnimationForLineChart(completedTasksChart);



        /* ----------==========     Emails Subscription Chart initialization    ==========---------- */

        var dataEmailsSubscriptionChart = {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            series: [
                [542, 443, 320, 780, 553, 453, 326, 434, 568, 610, 756, 895]

            ]
        };
        var optionsEmailsSubscriptionChart = {
            axisX: {
                showGrid: false
            },
            low: 0,
            high: 1000,
            chartPadding: { top: 0, right: 5, bottom: 0, left: 0}
        };
        var responsiveOptions = [
            ['screen and (max-width: 640px)', {
                seriesBarDistance: 5,
                axisX: {
                    labelInterpolationFnc: function (value) {
                        return value[0];
                    }
                }
            }]
        ];
        var emailsSubscriptionChart = Chartist.Bar('#emailsSubscriptionChart', dataEmailsSubscriptionChart, optionsEmailsSubscriptionChart, responsiveOptions);

        //start animation for the Emails Subscription Chart
        md.startAnimationForBarChart(emailsSubscriptionChart);

    },

    initGoogleMaps: function(){
        var myLatlng = new google.maps.LatLng(40.748817, -73.985428);
        var mapOptions = {
            zoom: 13,
            center: myLatlng,
            scrollwheel: false, //we disable de scroll over the map, it is a really annoing when you scroll through page
            styles: [{"featureType":"water","stylers":[{"saturation":43},{"lightness":-11},{"hue":"#0088ff"}]},{"featureType":"road","elementType":"geometry.fill","stylers":[{"hue":"#ff0000"},{"saturation":-100},{"lightness":99}]},{"featureType":"road","elementType":"geometry.stroke","stylers":[{"color":"#808080"},{"lightness":54}]},{"featureType":"landscape.man_made","elementType":"geometry.fill","stylers":[{"color":"#ece2d9"}]},{"featureType":"poi.park","elementType":"geometry.fill","stylers":[{"color":"#ccdca1"}]},{"featureType":"road","elementType":"labels.text.fill","stylers":[{"color":"#767676"}]},{"featureType":"road","elementType":"labels.text.stroke","stylers":[{"color":"#ffffff"}]},{"featureType":"poi","stylers":[{"visibility":"off"}]},{"featureType":"landscape.natural","elementType":"geometry.fill","stylers":[{"visibility":"on"},{"color":"#b8cb93"}]},{"featureType":"poi.park","stylers":[{"visibility":"on"}]},{"featureType":"poi.sports_complex","stylers":[{"visibility":"on"}]},{"featureType":"poi.medical","stylers":[{"visibility":"on"}]},{"featureType":"poi.business","stylers":[{"visibility":"simplified"}]}]

        }
        var map = new google.maps.Map(document.getElementById("map"), mapOptions);

        var marker = new google.maps.Marker({
            position: myLatlng,
            title:"Hello World!"
        });

        // To add the marker to the map, call setMap();
        marker.setMap(map);
    },

    showNotification: function(from, align){
        color = Math.floor((Math.random() * 4) + 1);

        $.notify({
            icon: "notifications",
            message: "Welcome to <b>Material Dashboard</b> - a beautiful freebie for every web developer."

        },{
            type: type[color],
            timer: 4000,
            placement: {
                from: from,
                align: align
            }
        });
    }
}
