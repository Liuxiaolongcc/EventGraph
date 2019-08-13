# coding: utf-8
'''构造显示图谱'''


class CreatePage:
    def __init__(self):
        self.base = '''
    <html>
    <head>
      <script type="text/javascript" src="VIS/dist/vis.js"></script>
      <link href="VIS/dist/vis.css" rel="stylesheet" type="text/css">
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    </head>
    <body>

    <div id="VIS_draw"></div>
    <script type="text/javascript">
      var nodes = data_nodes;
      var edges = data_edges;

      var container = document.getElementById("VIS_draw");

      var data = {
        nodes: nodes,
        edges: edges
      };

      var options = {
          nodes: {
              shape: 'dot',
              size: 25,
              font: {
                  size: 14
              }
          },
          edges: {
              font: {
                  size: 14,
                  align: 'middle'
              },
              color: 'gray',
              arrows: {
                  to: {enabled: true, scaleFactor: 0.5}
              },
              smooth: {enabled: false}
          },
          physics: {
              enabled: true
          }
      };

      var network = new vis.Network(container, data, options);

    </script>
    </body>
    </html>
    '''

    '''生成数据'''

    def collect_data(self, nodes, edges):
        node_dict = {node: index for index, node in enumerate(nodes)}
        data_nodes = []
        data_edges = []
        for node, id in node_dict.items():
            data = {}
            data["group"] = 'Event'
            data["id"] = id
            data["label"] = node
            data_nodes.append(data)

        for edge in edges:
            data = {}
            data['from'] = node_dict.get(edge[0])
            data['label'] = edge[1]
            data['to'] = node_dict.get(edge[2])
            data_edges.append(data)
        return data_nodes, data_edges

    '''生成html文件'''

    def create_html(self, data_nodes, data_edges):
        f = open('event_graph.html', 'w+')
        html = self.base.replace('data_nodes', str(data_nodes)).replace(
            'data_edges', str(data_edges))
        f.write(html)
        f.close()

if __name__ == '__main__':
    nodes = []
    edges = []
    with open('./triple.txt') as f:
        for line in f:
            triple = line.strip()[1:-1]
            triple = ''.join(triple.split(' '))
            triple = triple.split(',')
            nodes.append(triple[0])
            nodes.append(triple[2])
            edges.append(triple)

    handler = CreatePage()
    data_nodes, data_edges = handler.collect_data(nodes, edges)
    handler.create_html(data_nodes, data_edges)
