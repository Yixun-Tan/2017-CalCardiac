'use strict';

const webshot = require('webshot');
const fs = require('fs');

const sourceDir = 'alarms';
const destDir = 'alarm_images';

if (!fs.existsSync(sourceDir)) {
  console.log('Source directory does not exist');
  process.exit(1);
}

if (!fs.existsSync(destDir)) {
  fs.mkdirSync(destDir);
}

let strips = fs.readdirSync(sourceDir);
let canvasjs = fs.readFileSync('canvasjs.min.js', 'utf8');

//function to organize data points in a format that canvasjs accepts
function organizeDataPoints(data) {
  let pointsPerSek = 0;
  let highestDataPoint = 0;
  let smallestDataPoint = 0;
  let array = [];
  for (let i=0; i< data.length; i++) {
    pointsPerSek = pointsPerSek + 1/240;

    highestDataPoint =
      (parseInt(data[i], 10)*0.001*2.44 > highestDataPoint)
      ? parseInt(data[i], 10)*0.001*2.44
      : highestDataPoint;

    smallestDataPoint =
      (parseInt(data[i], 10)*0.001*2.44 < smallestDataPoint)
      ? parseInt(data[i], 10)*0.001*2.44
      : smallestDataPoint;

    array.push({x: pointsPerSek, y: parseInt(data[i], 10)*0.001*2.44});
  }
  let interval =
    ((highestDataPoint > 0)
      ? highestDataPoint
      : -highestDataPoint) + ((smallestDataPoint > 0) ? smallestDataPoint : -smallestDataPoint);

  return [array, interval, highestDataPoint, smallestDataPoint];
};

let startTime = new Date();
let numStripsProcessing = 0;

//generate images
for (let i=0; i<strips.length; i++) {
  numStripsProcessing++;
  let s = fs.readFileSync(`${sourceDir}/${strips[i]}`, 'utf8');

  let waveforms = JSON.parse(s); //.WaveformData
  let organizedData = [];
  let labels = [];

  for (let i=0; i<waveforms.length; i++) {
    //put data in format canvasjs will accept
    let data = organizeDataPoints(waveforms[i].Text.split(','));
    organizedData.push(data);
    labels.push(waveforms[i].Label);
  }

  //render images using webshot
  webshot(
    `
<html><head><script>
var waveforms = JSON.parse('${JSON.stringify(organizedData)}');
var labels = JSON.parse('${JSON.stringify(labels)}');

window.onload = function() {
  for (var i=0; i<waveforms.length; i++) {
    var div = document.createElement('div');
    div.style.height = '100px';
    div.id = 'div'+i;
    document.body.appendChild(div);

    var data = waveforms[i];
    var chart = new CanvasJS.Chart('div'+i, {
      zoomEnabled: false,
      animationEnabled: false,
      title: {
      },
      axisY: {
        title: labels[i],
        titleFontSize: 12,
        titleFontColor: 'black',
        titleFontFamily: 'verdana',
        labelFontColor: '#',
        maximum: data[2]*1.01,
        minimum: data[3],
        gridThickness: 0,
        gridColor: '#EF9A9A',
        lineThickness: 1,
        lineColor: '#EF9A9A',
        tickThickness: 0,
        margin: 0,
        tickLength: 0,
        includeZero: false,
        labelMaxWidth: 0,
        valueFormatString: ' ',
        stripLines: [
          {
            value: data[3]+data[1]/3,
            color: '#EF9A9A',
            thickness: 1
          },
          {
            value: data[3]+data[1]/3*2,
            color: '#EF9A9A',
            thickness: 1
          },
          {
            value: data[3]+data[1]/3*3,
            color: '#EF9A9A',
            thickness: 1
          }
        ]
      },
      axisX: {
        labelFontSize: 12,
        labelFontColor: 'black',
        gridThickness: 1,
        gridColor: '#EF9A9A',
        lineThickness: 1,
        lineColor: '#EF9A9A',
        tickThickness: 0,
        margin: -10,
        interval: 0.2,
        valueFormatString: ' '
      },
      toolTip: {
        shared: true
      },
      legend: {
        verticalAlign: 'top',
        horizontalAlign: 'right',
        cursor: 'pointer'
      },
      data: [{
        type: 'line',
        lineThickness: 1,
        color: '#2980b9',
        name: labels[i],
        dataPoints: data[0]
      }]
    });
    chart.render();
  }
};

</script></head>
<body>
<script>
${canvasjs}
</script>
</body>
</html>
    `,
    `${destDir}/${strips[i].slice(0, strips[i].indexOf('.'))}.png`,
    {
      siteType: 'html',
      errorIfJSException: true,
      windowSize: {width: 1920},
      shotSize: {width: 'window', height: 'all'},
    },
    function (err) {
      if (err) console.log(err);
      numStripsProcessing--;
      if (numStripsProcessing === 0) {
        let endTime = new Date();
        console.log(endTime - startTime);
      }
    }
  );
}
