"""The views of the predictions app"""

from django.shortcuts import render
from predictions.forms import addressForm, latlonForm
import requests


# Helper functions
def init_search_result():
    """A function to initialize the result Dictonary."""
    search_result = dict()
    search_result['api_data'] = ""
    search_result['query_url'] = ""
    search_result['spatialmos_api_url'] = ""
    search_result['error'] = ""
    search_result['licence'] = ""
    search_result['osm_data'] = dict()
    search_result['osm_data']['lat'] = ""
    search_result['osm_data']['lon'] = ""
    search_result['osm_data']['display_name'] = ""
    return search_result

def request_url(request_url):
    """A function which handles requests to an API interface."""
    error = ""
    data = None
    try:
        data_req = requests.get(request_url)
        if data_req.status_code == 200:
            data = data_req.json()
        else:
            error = f"Die API Schnittstelle '{request_url}' gab den Status {data_req.status_code} zurück."
        return data, error
    except:
        error = f"Die API Schnittstelle '{request_url}' konnte nicht abgefragt werden."
        return data, error


def nominatim_data(query_dict, reverse=False):
    """A Function to precess the API Call to nominatim.openstreetmap.org"""

    # Nominatim software is open source and licensed under GPLv2 license.
    # https://github.com/osm-search/Nominatim

    query_string = ""
    for key, value in query_dict.items():
        if value not in ['', 'None']:
            if query_string == "":
                query_string = f"{key}={value}"
            else:
                query_string = query_string + f"&{key}={value}"

    if reverse:
        nominatim_url = f"https://nominatim.openstreetmap.org/reverse.php?{query_string}&lang=de&polygon_geojson=0&format=jsonv2"
    else:
        nominatim_url = f"https://nominatim.openstreetmap.org/search.php?{query_string}&polygon_geojson=0&format=jsonv2"

    nominatim_json, error = request_url(nominatim_url)

    search_result = init_search_result()
    if error == "":
        try:
            if reverse:
                search_result['api_data'] = nominatim_json
            else:
                search_result['api_data'] = nominatim_json[0]
            display_name = search_result['api_data']['display_name']
            display_name = display_name.split(', ')
            state_matches = ['Tirol', 'Tyrol', 'Trentino-Alto Adige/Südtirol', 'South Tyrol', 'Südtirol']

            if any(state in display_name for state in state_matches):
                search_result['spatialmos_tmp_2m_api_url'] = f"/api/spatialmospoint/last/tmp_2m/{search_result['api_data']['lat']}/{search_result['api_data']['lon']}/"
                search_result['spatialmos_rh_2m_api_url'] = f"/api/spatialmospoint/last/rh_2m/{search_result['api_data']['lat']}/{search_result['api_data']['lon']}/"
                search_result['osm_data']['lon'] = float(search_result['api_data']['lon'])
                search_result['osm_data']['lat'] = float(search_result['api_data']['lat'])
                search_result['osm_data']['display_name'] = search_result['api_data']['display_name']
            else:
                error = f"Ihre Eingabe '{query_string}' führte zu einem Ergebnis außerhalb von Nord- und Südtirols."
        except:
            error = f"Ihre Suchanfrage '{query_string}' führte zu keinem brauchbaren Ergebnis."
    
    search_result['query_url'] = nominatim_url
    search_result['error'] = error
    search_result['licence'] = "Data Query from the © nominatim.openstreetmap.org API"
    return search_result


def photon_data(query_dict):
    """A Function to precess the API Call to photon.komoto.de"""

    # Photon software is open source and licensed under Apache License, Version 2.0.
    # https://github.com/komoot/photon

    query_list_filtered = []
    for key, value in query_dict.items():
        if value not in ['', 'None']:
            query_list_filtered.append(value)
    
    query_string = ' '.join(query_list_filtered)
    
    photon_url = f"http://photon.komoot.de/api/?q={query_string}&bbox=10,46.6,12.9,47.8&limit=1"
    photon_json, error = request_url(photon_url)

    spatialmos_api_url = ""
    photon_properties = ""
    if error == "":
        try:
            photon_properties = photon_json['features'][0]['properties']
            if photon_properties['state'] in ['Tyrol', 'Trentino-Alto Adige/Südtirol']:
                photon_coordinates = photon_json['features'][0]['geometry']['coordinates']
                spatialmos_api_url = f"/api/spatialmospoint/last/tmp_2m/{photon_coordinates[1]}/{photon_coordinates[0]}/"
            else:
                error = f"Ihre Eingabe '{query_string}' führte zu einem Ergebnis außerhalb von Nord- und Südtirols."
        except:
            error = f"Ihre Suchanfrage '{query_string}' führte zu keinem brauchbaren Ergebnis."
    
    search_result = init_search_result()
    search_result['api_data'] = photon_properties
    search_result['query_url'] = photon_url
    search_result['spatialmos_api_url'] = spatialmos_api_url
    search_result['error'] = error
    search_result['licence'] = "Data Query from the © photon.komoot.de API"
    return search_result

# Views
def addressprediction(request):
    """The function to display the spatialMOS predictions for a address."""
    search_result = init_search_result()

    if request.method == 'GET':
        address_form = addressForm(request.GET)
        if address_form.is_valid():
            query_dict = dict()
            query_dict['state'] = address_form.cleaned_data['state']
            query_dict['postcode'] = str(address_form.cleaned_data['postcode'])
            query_dict['city'] = address_form.cleaned_data['city']
            query_dict['street'] = address_form.cleaned_data['street']

            if query_dict['state'] == "Südtirol":
                query_dict['country'] = "Italy"
            else:
                query_dict['country'] = "Austria"

            search_result = nominatim_data(query_dict)
    else:
        address_form = addressForm()

    context = {
        'address_form': address_form,
        'search_result': search_result,
        'error': search_result['error']
    }
    return render(request, 'predictions/addressprediction.html', context)


def pointprediction(request):
    """The function to display the spatialMOS predictions for coordinates."""
    search_result = init_search_result()

    if request.method == 'GET':
        latlon_form = latlonForm(request.GET)

        if latlon_form.is_valid():
            query_dict = dict()
            query_dict['lat'] = latlon_form.cleaned_data['lat']
            query_dict['lon'] = latlon_form.cleaned_data['lon']

            search_result = nominatim_data(query_dict, reverse=True)
    else:
        latlon_form = latlonForm()

    context = {
        'latlon_form': latlon_form,
        'search_result': search_result,
        'error': search_result['error']
    }

    return render(request, 'predictions/pointprediction.html', context)


def predictions(request):
    """The function to display the spatialMOS plots."""

    return render(request, 'predictions/predictions.html')