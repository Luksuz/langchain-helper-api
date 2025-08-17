
from datetime import datetime, timedelta
from ryanair import Ryanair
from ryanair.types import Flight

def main():
    api = Ryanair(currency="EUR")
    tomorrow = datetime.today().date() + timedelta(days=1)
    try:
        flights = api.get_cheapest_flights("DUB", tomorrow, tomorrow + timedelta(days=1))
        if not flights:
            print("No flights found.")
            return
        flight: Flight = flights[0]
        print(flight)
        print(flight.price)
    except TypeError as te:
        print("A TypeError occurred, possibly due to an incompatibility in the ryanair package or its dependencies:")
        print(te)
    except Exception as exc:
        print("An unexpected error occurred:")
        print(exc)

if __name__ == "__main__":
    main()