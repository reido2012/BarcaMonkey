from smarkets import Smarkets


def main():
    smarkets = Smarkets.SmarketsParser()
    smarkets.write_or_update_events()


if __name__ == '__main__':
    main()
