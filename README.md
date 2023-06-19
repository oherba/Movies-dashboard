# IMDB-Movies-dashboard
Scrapping movie data from imdb, and then plotting it through charts in a web app by plotly
IMDb top 250 sorted by Metascore from: https://www.imdb.com/list/ls041970465/?sort=list_order,asc&st_dt=&mode=detail&page=
the scrapping iterates through the pages to access the full list, by adding page number at the end of the link.
Each movie block is inside a div with class "lister-item mode-detail", from there we can get all the wanted data.
The scrapping code is inside the jupyter notebook,
The resulting file from that scrapping is films.csv.
the python file creates a dashboards with 3 charts: score data by decade, top k movies and worst k movies.
