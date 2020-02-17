import reverse_geocoder as rg
import geocoder
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import ssl
import folium
import pycountry
from folium.features import DivIcon

geolocator = Nominatim(user_agent="specify_your_app_name_here", timeout=100)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
ssl._create_default_https_context = ssl._create_unverified_context


def show_words(coordinates):
    """
    tuple -> tuple(set, string)
    Returns the town(village) and country from the coordinates
    >>> show_words((49.83826, 24.02324))
    ('Lviv', 'UA')
    """
    inf = rg.search(coordinates)
    dct = {}
    for i in inf[0]:
        dct[i] = inf[0][i]
    name = dct['name']
    country = dct['cc']
    name = name.replace("'", '')
    country = country.replace("'", '')
    return name, country


def read_file(file, year):
    """
    (), int -> list
    Reads the file and returns the list of films directed in the given year
    >>> read_file(locations5.list.txt, 2015)
    ["#15SecondScare", Coventry, West Midlands, England, UK]
    """
    ls = []
    fr_year = "({})".format(year)
    with open(file, encoding='utf-8', errors='ignore') as f:
        for line in f:
            if fr_year in line:
                line = line.replace('\t', '')
                line = line.replace(fr_year, ',')
                line = line.replace('}', ',')
                line = line.strip()
                line = line.split(',')
                verbose = True
                for el in range(len(line)):
                    if '{' in line[el]:
                        verbose = False
                    line[el] = line[el].strip(' ')
                if verbose:
                    ls.append(line)
    return ls


def file_search(st, ls):
    """
    str, list -> list
    Returns the list of films of specific countries
    >>> file_search(set(['UK', 'GB']),
    [['"2012 UEFA"', 'Arena Lviv', ' Lviv', ' Ukraine'],
    "#ATown", Spiderhouse Cafe, Austin, Texas, USA]])
    [['"2012 UEFA"', 'Arena Lviv', ' Lviv', ' Ukraine']]
    """
    ls2 = []
    for line in ls:
        if line[-1] in st:
            ls2.append(line)
    return ls2


def find_neighbours(coordinates, lst):
    """
    tuple(int, int), list -> list
    Returns the names of films within neighbouring coordinates
    >>> find_neighbours((40.730610, -73.935242), file_search(set(['USA']),
    read_file('locations5.list.txt', 2015)))
    {'Taino': (40.730610, -73.935242)}
    """
    places = {}
    st = set()
    rng = 1
    for line in lst:
        place = ','.join(line[-3::])
        try:
            if len(places) < 10:
                if place not in st:
                    st.add(place)
                    ag = "specify_your_app_name_here"
                    geolocator = Nominatim(user_agent=ag, timeout=100)
                    location = geolocator.geocode(place, timeout=100)
                    lat, lon = location.latitude, location.longitude
                    if coordinates[0] - rng <= lat <= coordinates[0] + rng and\
                       coordinates[1] - rng <= lon <= coordinates[1] + rng:
                        places[line[0]] = (lat, lon)
            else:
                break
        except AttributeError as error:
            continue
        except ValueError as error:
            continue
    return places


def show_map(dct, file, coordinates, country, c):
    """
    dict -> ()
    Given the coordinates, prints a map with all matches and layers
    """
    coordinates = [coordinates[0], coordinates[1]]
    fg = folium.FeatureGroup(name="Films_map")
    count = 0
    for key in dct:
        lat = dct[key][0]
        lon = dct[key][1]
        fg.add_child(folium.CircleMarker(location=[lat, lon],
                                         radius=10,
                                         popup=key,
                                         fill_color='blue',
                                         color='green',
                                         fill_opacity=0.5))
    map.add_child(fg)
    fc = folium.FeatureGroup(name="Genre_map")
    with open(file) as f:
        for line in f:
            if c in line:
                line = line.split(',')
                text = line[1]
                break
    path = 'properties'
    fc.add_child(folium.GeoJson(data=open('world.json', 'r',
                                encoding='utf-8-sig').read(),
                                style_function=lambda x: {'fillColor': 'green'
                                                          if x[path]['ISO2'] ==
                                                          country
                                                          else 'blue'}))
    folium.map.Marker(
        [coordinates[0] + 1, coordinates[1] + 1],
        icon=DivIcon(icon_size=(0, 0), icon_anchor=(0, 0),
                     html='<div style="font-size: 24pt">%s</div>'
                     % text,)).add_to(fc)

    map.add_child(fc)
    map.add_child(folium.LayerControl())

    map.save('Map.html')


if __name__ == "__main__":
    year = input("Please enter a year you would like to have a map for: ")
    coordinates = input("Please enter your location (format: lat, long): ")
    coordinates = eval(coordinates)
    place = show_words(coordinates)
    town = place[0]
    country = place[1]
    c = pycountry.countries.get(alpha_2=country)
    a = c.alpha_3
    b = c.name
    st = set([country, a, b])
    if country == 'GB':
        b = 'UK'
        st.add('UK')
    file = 'locations.list.txt'
    f = read_file(file, year)
    file = file_search(st, f)
    print("The program is searching for the films...")
    neighs = find_neighbours(coordinates, file)
    print("Data is collected. The program is generating the map.")
    map = folium.Map(location=[coordinates[0], coordinates[1]], zoom_start=8)
    show_map(neighs, 'result2.csv', coordinates, country, b)
    print("Please have look at the map Map.html")
