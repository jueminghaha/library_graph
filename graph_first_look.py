import bibtexparser
import networkx as nx
import plotly.graph_objects as go
import numpy as np
import re


def clean_title(title):
    """
    清理标题，去除特殊字符，只保留字母、数字和空格
    """
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

    # 明确为中心文章节点添加年份信息
    G.add_node(center_article_id, year=center_article_year)
    return G


def spherical_layout(G, center_article_id, radius=1):
    pos = {}
    non_center_nodes = [node for node in G.nodes() if node != center_article_id]
    n = len(non_center_nodes)
    # 中心文章放在原点
    pos[center_article_id] = (0, 0, 0)
    phi = (1 + np.sqrt(5)) / 2  # 黄金比例
    for i, node in enumerate(non_center_nodes):
        # Fibonacci 格点法
        y = 1 - (i / (n - 1)) * 2
        r = np.sqrt(1 - y * y)
        theta = 2 * np.pi * i / phi
        x = r * np.cos(theta)
        z = r * np.sin(theta)
        pos[node] = (radius * x, radius * y, radius * z)
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
            size=5,
            color='lightblue',
            line_width=0.5))

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(title='3D Spherical Article Citation Graph with Center Article in the Middle',
                      scene=dict(xaxis_title='X',
                                 yaxis_title='Y',
                                 zaxis_title='Z'))
    # 保存为 HTML 文件，包含 plotly.js 库
    html_filename = '3d_citation_graph.html'
    fig.write_html(html_filename)
    print(f"图形已保存为 {html_filename}")
    fig.show()


if __name__ == "__main__":
    # 替换为你的 BibTeX 文件路径
    bib_file_path = 'path'
    # 假设中心文章的标题，需清理后作为 ID
    center_article_title = "Spherical codes and designs"
    center_article_id = clean_title(center_article_title)
    center_article_year = 1977  # 中心文章的年份
    entries = parse_bib_file(bib_file_path)
    graph = build_directed_graph(entries, center_article_id, center_article_year)
    visualize_3d_graph(graph, center_article_id)
