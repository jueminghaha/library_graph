import bibtexparser
import networkx as nx
import plotly.graph_objects as go
import numpy as np
import re


def clean_title(title):
    return re.sub(r'[^a-zA-Z0-9\s]', '', title).strip().replace(' ', '_')


def parse_bib_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as bibtex_file:
        content = bibtex_file.read()
        entries1 = content.split('@')[1:]

    entries = []
    for entry in entries1:
        s = entry[entry.find('title = {') + 9:entry.rfind('}')]
        title = entry[entry.find('title = {') + 9: entry.find('title = {') + 9 + s.find('}')]
        title = clean_title(title)
        if entry.find('year = {') == -1:
            year = 'none'
        else:
            s2 = entry[entry.find('year = {') + 8:entry.rfind('}')]
            year = entry[entry.find('year = {') + 8: entry.find('year = {') + 8 + s2.find('}')]
        entries.append({
            'id': title,
            'year': int(year) if year and year.isdigit() else None,
        })
    return entries


def build_directed_graph(entries, center_article_id, center_article_year):
    G = nx.DiGraph()
    for entry in entries:
        entry_id = entry['id']
        G.add_node(entry_id, year=entry['year'])
        if entry_id != center_article_id:
            G.add_edge(entry_id, center_article_id)

    G.add_node(center_article_id, year=center_article_year)
    return G


def spherical_layout(G, center_article_id, radius=1, start_year=1977, end_year=2024):
    pos = {}
    non_center_nodes = [node for node in G.nodes() if node != center_article_id]
    n = len(non_center_nodes)

    
    pos[center_article_id] = (0, 0, 0)

    total_years = end_year - start_year + 1
    degrees_per_year = 360 / total_years

    for node in non_center_nodes:
        year = G.nodes[node].get('year')
        if year is not None:
            # 计算经度
            theta = (year - start_year) * degrees_per_year * (np.pi / 180)


            phi = np.random.uniform(-np.pi / 2, np.pi / 2)

            x = radius * np.cos(phi) * np.cos(theta)
            y = radius * np.cos(phi) * np.sin(theta)
            z = radius * np.sin(phi)
            pos[node] = (x, y, z)
        else:
            
            index = non_center_nodes.index(node)
            phi = (1 + np.sqrt(5)) / 2  # 黄金比例
            y_coord = 1 - (index / (n - 1)) * 2
            r = np.sqrt(1 - y_coord * y_coord)
            theta = 2 * np.pi * index / phi
            x = r * np.cos(theta)
            z = r * np.sin(theta)
            pos[node] = (radius * x, radius * y_coord, radius * z)

    return pos


def visualize_3d_graph(G, center_article_id):
    # 生成球状布局
    pos = spherical_layout(G, center_article_id)

    node_x = []
    node_y = []
    node_z = []
    node_text = []
    for node in G.nodes():
        x, y, z = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        year = G.nodes[node].get('year')
        if year is not None:
            node_text.append(f"Title: {node}\nYear: {year}")
        else:
            node_text.append(f"Title: {node}\nYear: Unknown")

    edge_x = []
    edge_y = []
    edge_z = []
    for edge in G.edges():
        x0, y0, z0 = pos[edge[0]]
        x1, y1, z1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_z.extend([z0, z1, None])

    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        line=dict(color='gray', width=0.1),
        hoverinfo='none',
        mode='lines')

    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers',
        hovertext=node_text,
        marker=dict(
            size=3,
            color='lightblue',
            line_width=0.2))

    # 绘制每 30 度的经线
    radius = 1
    meridian_traces = []
    for theta_deg in range(0, 360, 30):
        theta = theta_deg * np.pi / 180
        phi_values = np.linspace(-np.pi / 2, np.pi / 2, 100)
        x_meridian = radius * np.cos(phi_values) * np.cos(theta)
        y_meridian = radius * np.cos(phi_values) * np.sin(theta)
        z_meridian = radius * np.sin(phi_values)

        meridian_trace = go.Scatter3d(
            x=x_meridian,
            y=y_meridian,
            z=z_meridian,
            mode='lines',
            line=dict(color='red', width=1),
            hoverinfo='none'
        )
        meridian_traces.append(meridian_trace)

    fig = go.Figure(data=[edge_trace, node_trace] + meridian_traces)
    fig.update_layout(title='3D Spherical Article Citation Graph with Center Article in the Middle',
                      scene=dict(xaxis_title='X',
                                 yaxis_title='Y',
                                 zaxis_title='Z'))
    
    html_filename = '3d_citation_graph.html'
    fig.write_html(html_filename)
    print(f"图形已保存为 {html_filename}")
    fig.show()


if __name__ == "__main__":
    bib_file_path = '/Users/hanyufeng/downloads/library.bib'
    center_article_title = "Spherical codes and designs"
    center_article_id = clean_title(center_article_title)
    center_article_year = 1977
    entries = parse_bib_file(bib_file_path)
    graph = build_directed_graph(entries, center_article_id, center_article_year)
    visualize_3d_graph(graph, center_article_id)
