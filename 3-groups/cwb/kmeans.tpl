<html>
  <head>
    <title>K-means Scatterplot</title>
    <script type="text/javascript" src="/js/protovis-r3.2.js"></script>
    <script type="text/javascript" src="/js/jquery-1.5.min.js"></script>
    <script type="text/javascript+protovis">
      var JSONdata = $.ajax({ type: "GET", url: "{{data_url}}",
      async: false }).responseText;
      var data = JSON.parse(JSONdata);
      var points = data.points,
          min = data.minimum,
          max = data.maximum;
      var x = pv.Scale.linear(min,max).range(0,400),
          y = pv.Scale.linear(min,max).range(0,400),
          color = pv.Colors.category20();

      var vis = new pv.Panel()
      .canvas("fig")
      .width(400)
      .height(400)
      .margin(20);

      vis.add(pv.Dot)
      .data(points)
      .left(function (d) x(d.x))
      .bottom(function (d) y(d.y))
      .fillStyle(function (d) color(d.cluster))
      .size(20);

      vis.render();
    </script>
    <style type="text/css">
      body {
      margin: 0;
      font: 14px/134% Helvetica Neue, sans-serif;
      }

      #fig {
      height: 440px;
      width: 440px;
      display: block !important;
      margin: auto;
      }
    </style>
  </head>
  <body>
    <div id="center"><div id="fig">
    </div></div>
  </body>
</html>
