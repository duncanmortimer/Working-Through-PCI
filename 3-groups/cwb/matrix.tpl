<html>
  <head>
    <title>Word counts for blogs</title>
    <script type="text/javascript" src="/js/protovis-r3.2.js"></script>
    <script type="text/javascript" src="/js/jquery-1.5.min.js"></script>
    <script type="text/javascript+protovis">
      var JSONdata = $.ajax({ type: "GET", url: "{{data_url}}",
      async: false }).responseText;
      var data = JSON.parse(JSONdata);
      var wordcount = data.counts;
      var cols = data.cols;

      /* Color scale */
      var c = pv.Scale.linear(0,10).range("white", "steelblue");

      /* The cell dimensions. */
      var w = 10, h = 10;

      var vis = new pv.Panel()
      .canvas("fig")
      .width(cols.length * w)
      .height(wordcount.length * h)
      .top(50)
      .left(130);

      vis.add(pv.Panel)
      .data(cols)
      .left(function() this.index * w)
      .width(w)
      .add(pv.Panel)
      .data(wordcount)
      .top(function() this.index * h)
      .height(h)
      .fillStyle(function(d, f) c(d[f]))
      .strokeStyle("white")
      .lineWidth(1)
      .antialias(false)
      .title(function(d, f) d.Blog + "'s " + f + ": " + d[f]);

      vis.add(pv.Label)
      .data(cols)
      .left(function() this.index * w + w / 2)
      .textAngle(-Math.PI / 2)
      .textBaseline("middle");

      vis.add(pv.Label)
      .data(wordcount)
      .top(function() this.index * h + h / 2)
      .textAlign("right")
      .textBaseline("middle")
      .text(function(d) d.Blog);

      vis.render();
    </script>
    <style type="text/css">
      body {
      margin: 0;
      font: 14px/134% Helvetica Neue, sans-serif;
      }

      #fig {
      height: 800px;
      width: 800px;
      display: block !important;
      }
    </style>
  </head>
  <body>
    <div id="center"><div id="fig">
    </div></div>
  </body>
</html>
