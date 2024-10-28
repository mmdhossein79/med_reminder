

var options = {
    series: [{
        name: 'مرد',
        data: [300, 250, 548, 440, 550, 570, 560, 610, 580, 630, 600, 660]
    }, {
        name: 'زن',
        data: [256, 480, 560, 760, 850, 1010, 980, 870, 1050, 910, 1140, 940]
    }, {
        name: 'کودک',
        data: [480, 223, 256, 350, 410, 360, 260, 450, 480, 520, 530, 410]
    }],
    chart: {
        fontFamily: 'iransans', 
        type: 'bar',
        height: 350,
        toolbar: {
            show: false,
        },
    },
    grid: {
        borderColor: '#e9ecef',
    },
    plotOptions: {
        bar: {
            horizontal: false,
            columnWidth: '40%',
            endingShape: 'rounded'
        },
    },
    dataLabels: {
        enabled: false
    },
    stroke: {
        show: true,
        width: 2,
        colors: ['transparent']
    },
    colors: ['#396cf0', '#53c797', '#f1b561'],
    xaxis: {
        categories: ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'],
    },
    yaxis: {
        title: {
            text: 'بیماران',

            style: {
                colors: ['#8492a6'],
                fontSize: '13px',
                fontFamily: 'Inter, sans-serif',
                fontWeight: 500,
            },
        },
    },
    fill: {
        opacity: 1,
    },
    tooltip: {
        y: {
            formatter: function (val) {
                return val + " بیمار"
            }
        }
    }
};

var chart = new ApexCharts(document.querySelector("#dashboard"), options);
chart.render();


//department
var options = {
    series: [55, 65, 75, 85],
    chart: {
        fontFamily: 'iransans', 
        height: 370,
        type: 'radialBar',
    },    
    colors: ['#396cf0', '#53c797', '#f1b561', '#f0735a'],
    plotOptions: {
        radialBar: {
            hollow: {
                // size: '70%',
            },
            dataLabels: {
                name: {
                    fontSize: '22px',
                },
                value: {
                    fontSize: '16px',
                    formatter: function (val) {
                        return val + ' ' + 'بیمار'
                    }
                },
                total: {
                    show: true,
                    label: 'کل',
                    formatter: function (w) {
                        return 280 + ' ' + 'بیمار'
                    }
                }
            }
        }
    },
    stroke: {
        lineCap: 'round',
    },
    labels: ['قلب', 'کلیه', 'دندان', 'اعصاب'],
};

var chart = new ApexCharts(document.querySelector("#department"), options);
chart.render();
