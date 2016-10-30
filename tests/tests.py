# coding: utf-8

from __future__ import unicode_literals, absolute_import, division, print_function

from datetime import datetime as dt
from datetime import timedelta as delta
from unittest import TestCase

import core
from core import DateInterval
from core import DateConstraint
from core import BackendRequest
from core import Flight as F
from core import Edge as E


def make_flight(orig='A', dest='B', date0=dt(2016, 1, 1, 10, 30), date1=dt(2016, 1, 1, 13, 30), price=100, flight_number='abc'):
    return F(**locals())


class Tests(TestCase):

    data = {
        "airports": [
            {
                "routes": [
                    "region:SICILY",
                    "airport:STN",
                    "airport:CAG",
                    "country:it",
                    "country:gb",
                    "airport:TPS",
                    "city:TRAPANI",
                    "region:SARDINIA",
                    "city:CAGLIARI",
                    "city:LONDON",
                    "region:GREATER_LONDON"
                ],
                "iataCode": "PMF",
                "categories": [
                    "FAM",
                    "SPR",
                    "FST",
                    "CTY",
                    "CUL",
                    "OUT"
                ],
                "name": "Parma",
                "cityCode": "PARMA",
                "countryCode": "it",
                "seoName": "parma",
                "regionCode": "EMILIA-ROMAGNA",
                "coordinates": {
                    "latitude": 44.8245,
                    "longitude": 10.2964
                },
                "priority": 115,
                "seasonalRoutes": [],
                "currencyCode": "EUR",
                "base": False
            },
            {
                "routes": [
                    "airport:VLC",
                    "airport:LPA",
                    "city:TENERIFE",
                    "region:CANARY_ISLES",
                    "country:gr",
                    "airport:WMI",
                    "airport:BGY",
                    "airport:FCO",
                    "airport:MAD",
                    "city:GRAN_CANARIA",
                    "airport:PMI",
                    "airport:AGP",
                    "airport:SOF",
                    "city:MILAN",
                    "city:WARSAW",
                    "city:BERLIN",
                    "region:COSTA_DE_SOL",
                    "city:BARCELONA",
                    "city:SOFIA",
                    "country:dk",
                    "country:pt",
                    "city:ROME",
                    "country:lv",
                    "region:COSTA_BRAVA",
                    "country:pl",
                    "city:VALENCIA",
                    "airport:DUB",
                    "airport:CFU",
                    "country:de",
                    "airport:STN",
                    "airport:OPO",
                    "city:CORFU",
                    "city:PORTO",
                    "country:es",
                    "city:BENIDORM",
                    "airport:SXF",
                    "airport:RIX",
                    "airport:MLA",
                    "country:mt",
                    "city:PALMA",
                    "airport:CPH",
                    "city:MALAGA",
                    "country:it",
                    "region:IONIAN_ISLANDS_GREEK_ISLANDS",
                    "airport:ALC",
                    "country:ie",
                    "airport:FAO",
                    "city:ALGARVE",
                    "city:LONDON",
                    "airport:BCN",
                    "country:gb",
                    "airport:TFS",
                    "city:DUBLIN",
                    "city:MADRID",
                    "city:MALTA",
                    "airport:CIA",
                    "country:bg",
                    "city:COPENHAGEN",
                    "city:RIGA",
                    "region:COSTA_BLANCA",
                    "region:GREATER_LONDON"
                ],
                "iataCode": "CGN",
                "categories": [
                    "FAM",
                    "SPR",
                    "FST",
                    "CTY",
                    "CUL",
                    "OUT",
                    "XMS"
                ],
                "name": "Cologne",
                "cityCode": "COLOGNE",
                "countryCode": "de",
                "seoName": "cologne-bonn",
                "regionCode": "NORTH_RHINE-WESTPHALIA",
                "coordinates": {
                    "latitude": 50.8659,
                    "longitude": 7.14274
                },
                "priority": 80,
                "seasonalRoutes": [],
                "currencyCode": "EUR",
                "base": True
            }
        ]
    }

    def test_1(self):
        result = core.get_connections_from_stations_data(self.data)

        expected = {
            'CGN': {
                'VLC',
                'LPA',
                'WMI',
                'BGY',
                'FCO',
                'MAD',
                'PMI',
                'AGP',
                'SOF',
                'DUB',
                'CFU',
                'STN',
                'OPO',
                'SXF',
                'RIX',
                'MLA',
                'CPH',
                'ALC',
                'FAO',
                'BCN',
                'TFS',
                'CIA',
            },

            'PMF': {
                'STN',
                'CAG',
                'TPS',
            }

        }

        self.assertEqual(expected, result)

    def test_2(self):
        result = core.get_airport_names_from_raw_data(self.data)
        expected = {
            'PMF': 'Parma',
            'CGN': 'Cologne',
        }

        self.assertEqual(result, expected)

    network = {
        'A': {'B', 'C', 'D'},
        'B': {'A', 'F'},
        'C': {'A', 'F', 'E'},
        'D': {'A', 'E'},
        'E': {'D', 'C', 'F'},
        'F': {'B', 'C', 'E'},
    }

    def test_3(self):
        """
        If enough depth is allowed, all the possible paths are discovered

        """
        res = set(map(tuple, core.find_paths(['A'], ['F'], self.network, max_flights=1000000)))
        expected = {
            (('A', 'B'), ('B', 'F')),
            (('A', 'C'), ('C', 'F')),
            (('A', 'C'), ('C', 'E'), ('E', 'F')),
            (('A', 'D'), ('D', 'E'), ('E', 'F')),
            (('A', 'D'), ('D', 'E'), ('E', 'C'), ('C', 'F')),
        }

        self.assertEqual(expected, res)

    def test_3b(self):
        expected = {
            (('A', 'B'), ('B', 'F')),
            (('A', 'C'), ('C', 'F')),
        }

        res = set(map(tuple, core.find_paths(['A'], ['F'], self.network, max_flights=2)))
        self.assertEqual(expected, res)

    def test_3c(self):
        """
        From multiple starts to multiple destinations

        """
        res = set(map(tuple, core.find_paths(['A', 'B'], ['F', 'E'], self.network, max_flights=1000000)))
        expected = {
            (('B', 'F'), ),
            (('A', 'C'), ('C', 'F')),
            (('A', 'C'), ('C', 'E')),
            (('A', 'D'), ('D', 'E')),
        }
        self.assertEqual(expected, res)

    def test_6(self):
        paths = [[E('A', 'B'), E('B', 'C')], [E('D', 'E')]]
        dates_to = core.DateInterval(dt(2016, 10, 10), dt(2016, 10, 20))
        result = core.calculate_needed_requests(paths, dates_to)

        self.assertEqual({
            BackendRequest('A', 'B', dt(2016, 10, 10), None),
            BackendRequest('A', 'B', dt(2016, 10, 17), None),
            BackendRequest('B', 'C', dt(2016, 10, 10), None),
            BackendRequest('B', 'C', dt(2016, 10, 17), None),
            BackendRequest('D', 'E', dt(2016, 10, 10), None),
            BackendRequest('D', 'E', dt(2016, 10, 17), None),
        }, result)

    def test_7(self):
        """
        When start and end date are the same, we still query once

        """
        paths = [[E('A', 'B'), E('B', 'C')], [E('D', 'E')]]
        dates_to = core.DateInterval(dt(2016, 10, 10), dt(2016, 10, 10))
        result = core.calculate_needed_requests(paths, dates_to)

        self.assertEqual({
            BackendRequest('A', 'B', dt(2016, 10, 10), None),
            BackendRequest('B', 'C', dt(2016, 10, 10), None),
            BackendRequest('D', 'E', dt(2016, 10, 10), None),
        }, result)

    def test_8(self):
        """
        Query calculator works fine over longer time periods

        """
        paths = [[E('A', 'B')]]
        dates_to = core.DateInterval(dt(2016, 10, 1), dt(2016, 11, 15))
        result = core.calculate_needed_requests(paths, dates_to)

        self.assertEqual({
            BackendRequest('A', 'B', dt(2016, 10, 1), None),
            BackendRequest('A', 'B', dt(2016, 10, 8), None),
            BackendRequest('A', 'B', dt(2016, 10, 15), None),
            BackendRequest('A', 'B', dt(2016, 10, 22), None),
            BackendRequest('A', 'B', dt(2016, 10, 29), None),
            BackendRequest('A', 'B', dt(2016, 11, 5), None),
            BackendRequest('A', 'B', dt(2016, 11, 12), None),
        }, result)

    def test_9(self):
        """
        are_flights_compatible: positive single flight

        """
        flights = [make_flight()]
        constraint = DateConstraint(
            earliest_out=dt(2016, 1, 1),
            latest_in=dt(2016, 1, 1, 23, 59, 59),
            latest_out=dt(2016, 1, 1, 23, 59, 59),
            min_between_flights=delta(hours=1),
            max_between_flights=delta(hours=5),
        )

        self.assertTrue(core.are_flights_compatible(flights, constraint))

    def test_10(self):
        """
        are_flights_compatible: negative single flight - arrives too late

        """
        flight = make_flight()

        constraint = DateConstraint(
            earliest_out=dt(2016, 1, 1),
            latest_out=dt(2016, 1, 1, 23, 59, 59),
            latest_in=flight.date1 - delta(hours=1),  # Failing constraint
            min_between_flights=delta(hours=1),
            max_between_flights=delta(hours=5),
        )

        self.assertFalse(core.are_flights_compatible([flight], constraint))

    def test_11(self):
        """
        are_flights_compatible: negative single flight - departs too late

        """
        flight = make_flight()

        constraint = DateConstraint(
            earliest_out=dt(2016, 1, 1),
            latest_out=flight.date0 - delta(hours=1),  # Failing condition
            latest_in=dt(2016, 1, 1, 23, 59, 59),
            min_between_flights=delta(hours=1),
            max_between_flights=delta(hours=5),
        )

        self.assertFalse(core.are_flights_compatible([flight], constraint))

    def test_12(self):
        """
        are_flights_compatible: negative single flight - departs too early

        """
        flight = make_flight()

        constraint = DateConstraint(
            earliest_out=flight.date0 + delta(hours=1),
            latest_out=dt(2016, 1, 1, 23, 59, 59),
            latest_in=dt(2016, 1, 1, 23, 59, 59),
            min_between_flights=delta(hours=1),
            max_between_flights=delta(hours=5),
        )

        self.assertFalse(core.are_flights_compatible([flight], constraint))

    def test_13(self):
        """
        are_flights_compatible: positive multiple flights

        """
        f1 = make_flight()
        f2 = make_flight(orig=f1.dest, dest='C', date0=f1.date1 + delta(hours=1), date1=f1.date1 + delta(hours=3))

        constraint = DateConstraint(
            earliest_out=dt(2016, 1, 1),
            latest_out=dt(2016, 1, 1, 23, 59, 59),
            latest_in=dt(2016, 1, 1, 23, 59, 59),
            min_between_flights=delta(hours=1),
            max_between_flights=delta(hours=5),
        )

        self.assertTrue(core.are_flights_compatible([f1, f2], constraint))

    def test_14(self):
        """
        Negative are_flights_compatible: there is not enough time between flights

        """
        f1 = make_flight()
        f2 = make_flight(orig=f1.dest, dest='C', date0=f1.date1, date1=f1.date1 + delta(hours=3))

        constraint = DateConstraint(
            earliest_out=dt(2016, 1, 1),
            latest_out=dt(2016, 1, 1, 23, 59, 59),
            latest_in=dt(2016, 1, 1, 23, 59, 59),
            min_between_flights=delta(hours=1),
            max_between_flights=delta(hours=5),
        )

        self.assertFalse(core.are_flights_compatible([f1, f2], constraint))

    def test_15(self):
        """
        Negative are_flights_compatible: there is too much time between flights

        """
        f1 = make_flight()
        f2 = make_flight(orig=f1.dest, dest='C', date0=f1.date1 + delta(hours=10), date1=f1.date1 + delta(hours=13))

        constraint = DateConstraint(
            earliest_out=dt(2016, 1, 1),
            latest_out=dt(2016, 1, 1, 23, 59, 59),
            latest_in=dt(2016, 1, 1, 23, 59, 59),
            min_between_flights=delta(hours=1),
            max_between_flights=delta(hours=5),
        )

        self.assertFalse(core.are_flights_compatible([f1, f2], constraint))
