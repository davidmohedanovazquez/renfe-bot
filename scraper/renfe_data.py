from calmjs.parse import es5
from calmjs.parse.unparsers.extractor import ast_to_dict

import os
import requests
import string

URL_STATIONS = "https://www.renfe.com/content/dam/renfe/es/General/buscadores"\
               "/javascript/estacionesEstaticas.js"


class RenfeData:
    def __init__(self, date_go: str, date_back: str,
                 origin: str, destination: str):
        """
        format for date: dd/mm/yyyy
        date for back can be an empty string

        examples:
            origin: SEVILLA-SANTA JUSTA
            destination: CÓRDOBA

        this class depends on the station list at URL_STATIONS,
        if it doesn't exist it will be downloaded and parsed
        with calmjs. I didn't use CURL for portabily reasons
        """

        STATIONS_LIST = self.get_stations_list()
        origin = self.find_station(STATIONS_LIST, origin)
        destination = self.find_station(STATIONS_LIST, destination)
        if origin is None or destination is None:
            raise Exception("Origin or destination not found")
        self.date_go = date_go
        self.date_back = date_back
        self.origin_code = origin[0]
        self.destination_code = destination[0]
        self.origin = origin[1]
        self.destination = destination[1]
        self.data = {
            "tipoBusqueda": "autocomplete",
            "currenLocation": "menuBusqueda",
            "vengoderenfecom": "SI",
            "cdgoOrigen": self.origin_code,
            "cdgoDestino": self.destination_code,
            "idiomaBusqueda": "ES",
            "FechaIdaSel": self.date_go,
            "FechaVueltaSel": self.date_back,
            "desOrigen": self.origin,
            "desDestino": self.destination,
            "_fechaIdaVisual": self.date_go,
            "_fechaVueltaVisual": self.date_back,
            "adultos_": "1",
            "ninos_": "0",
            "ninosMenores": "0",
            "numJoven": "",
            "numDorada": "",
            "codPromocional": "",
            "plazaH": "false",
            "Idioma": "es",
            "Pais": "ES"
        }

    def get_post_data(self):
        return self.data

    def get_stations_list(self):
        filename = "estacionesEstaticas.js"
        if not os.path.exists(filename):
            print("Downloading stations list...")
            response = requests.get(URL_STATIONS)
            if response.status_code != 200:
                print(f"The resource at {URL_STATIONS} is not available")
                return None
            with open(filename, "w+") as f:
                f.write(response.text)
                print("Done!")
                f.close()

        with open(filename, "r") as f:
            file_content = f.read()
            stations = es5(file_content)
            stations_dict = ast_to_dict(stations)

        if "estacionesEstatico" in stations_dict:
            return stations_dict["estacionesEstatico"]
        return None

    def find_station(self, stations: list, station_name: str):
        for station in stations:
            if station["desgEstacion"] == station_name:
                return (station["clave"], station["desgEstacion"])
        return None