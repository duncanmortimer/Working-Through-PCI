<html>
  <head>
    <title>Hierarchical Cluster Dendrogram</title>
    <script type="text/javascript" src="/js/protovis-r3.2.js"></script>
    <script type="text/javascript" src="/js/jquery-1.5.min.js"></script>
    <script type="text/javascript+protovis">
      var JSONdata = $.ajax({ type: "GET", url: "{{data_url}}",
      async: false }).responseText;
      var data = JSON.parse(JSONdata);
      var tree = data.tree;

      var vis = new pv.Panel()
      .canvas("fig")
      .width(700)
      .left(40)
      .right(260)
      .top(10)
      .bottom(10);

      var layout = vis.add(pv.Layout.Cluster)
      .nodes(pv.dom(tree)
      .root("tree")
      .sort(function(a, b) pv.naturalOrder(a.nodeName, b.nodeName))
      .nodes())
      .group(true)
      .orient("left");

      layout.link.add(pv.Line)
      .strokeStyle("#ccc")
      .lineWidth(1)
      .antialias(false);

      layout.node.add(pv.Dot)
      .fillStyle(function(n) n.firstChild ? "#aec7e8" : "#ff7f0e");

      layout.label.add(pv.Label)
      .text(function(d) d.nodeValue);

      vis.render();
    </script>
    <style type="text/css">
      body {
      margin: 0;
      font: 14px/134% Helvetica Neue, sans-serif;
      }

      #fig {
      height: 1600px;
      width: 1000px;
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
