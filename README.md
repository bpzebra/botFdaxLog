# FDAX Trade Logger Bot

Dieser einfache Bot verbindet sich mit Interactive Brokers (IB) über TWS oder das IB Gateway und loggt Trades des nächsten FDAX Futures an der EureX in eine CSV-Datei.

## Anforderungen

- Python 3.x
- Ein laufendes TWS oder IB Gateway mit aktiviertem API-Zugriff.
- API-Einstellungen:
  - Port: 7497 (Paper Trading) oder 7496 (Live Trading)
  - "Enable ActiveX and Socket Clients" muss aktiviert sein.

## Installation

Installieren Sie die Abhängigkeiten:

```bash
pip install -r requirements.txt
```

## Verwendung

Führen Sie das Skript aus:

```bash
python fdax_logger.py
```

Der Bot sucht automatisch nach dem FDAX Future mit dem nächsten Verfallsdatum (front-month) auf der Eurex und beginnt mit dem Loggen der Trades in `trades_log.csv`.

### Felder in der Log-Datei:

1. `timestamp`: Zeitstempel des Trades.
2. `tradeprice`: Preis zu dem der Trade stattfand.
3. `tradevolume`: Volumen des Trades.

## Konfiguration

Sie können den Host, Port und die ClientID direkt im Kopf von `fdax_logger.py` anpassen:

```python
HOST = '127.0.0.1'
PORT = 7497  # Standard für Paper Trading
CLIENT_ID = 1
LOG_FILE = 'trades_log.csv'
```
