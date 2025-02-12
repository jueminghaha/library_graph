# library_graph

  We want to creat a graph for articles, which cited 'Spherical codes and designs', first we should have a .bib file to get the articles, then based on this bib file, using Python we can get the following graphics.
You can download this link. It's an HTML animated graphic I created. They use longitude as the dividing line for years. However, we can use the number of times these articles are cited as the radius size of the article on the sphere. It hasn't been updated yet.

[3d_citation_graph.html](https://github.com/jueminghaha/library_graph/blob/277a8fbba58fe55bf56557931b670cb66cc8ad03/3d_citation_graph.html)

1.we will use some tips to get bib files.

Frist we can use selenium to google scholar. Since you cannot request so fast, you should set a sleep time(30s), it is very important.

2.Create links between csv files.

We can use .csv files to connect with different files. Like (con_output.csv), you will get so many nodes (without years, we can use a little tip to handle this difficulty).

3.Set different weights for different documents

