import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt

# Задаем начальную и конечную точки маршрута
point_a = (61.3256, 73.2211)
point_b = (62.4051, 72.7813)

# Получаем граф дорожной сети из OpenStreetMap на основе координат начальной точки
graph = ox.graph_from_place('Сургут, Россия', network_type='all')

# Находим ближайшие узлы графа к начальной и конечной точкам
node_a = ox.distance.nearest_nodes(graph, point_a[1], point_a[0])
node_b = ox.distance.nearest_nodes(graph, point_b[1], point_b[0])

# Находим оптимальный маршрут между узлами графа
optimal_route = nx.shortest_path(graph, node_a, node_b, weight='length')

route_points = [(graph.nodes[i]['y'], graph.nodes[i]['x']) for i in optimal_route]

total_length = sum(ox.utils_graph.get_route_edge_attributes(graph, optimal_route, 'length'))
print(f'Total length: {total_length} meters')

# Визуализируем граф и оптимальный маршрут на карте
fig, ax = ox.plot_graph_route(graph, optimal_route, route_linewidth=6, node_size=0, bgcolor='k', show=False, close=False)

# Отображение точек на карте
ax.scatter([point_a[1], point_b[1]], [point_a[0], point_b[0]], c='r', edgecolor='none', s=50)
ax.plot([p[1] for p in route_points], [p[0] for p in route_points], c='g', linewidth=3)
ax.set_xlim([min([p[1] for p in route_points])-0.01, max([p[1] for p in route_points])+0.01])
ax.set_ylim([min([p[0] for p in route_points])-0.01, max([p[0] for p in route_points])+0.01])

# Отображение карты
plt.show()

