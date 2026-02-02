from collectors.bazaar import collect_bazaar
from collectors.ah import collect_ah
from collectors.events import collect_events


def main():
    print("Starte SkyBlock Engine...")

    collect_bazaar()
    collect_ah()
    collect_events()

    print("Snapshot abgeschlossen.")


if __name__ == "__main__":
    main()
