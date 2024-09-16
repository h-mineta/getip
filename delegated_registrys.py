#!/usr/bin/env python3

import ipaddress
import math
import requests
import polars as pl

REGISTRYS: dict[str, str] = {
    "apnic" :   "https://ftp.apnic.net/stats/apnic/delegated-apnic-extended-latest",
    "afrinic" : "https://ftp.apnic.net/stats/afrinic/delegated-afrinic-extended-latest",
    "arin":     "https://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest",
    "lacnic":   "https://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-extended-latest",
    "ripencc":  "https://ftp.ripe.net/ripe/stats/delegated-ripencc-extended-latest.txt"
}
COLUMN_NAMES: list[str] = ["network_address", "registry", "country_code", "type", "start", "value", "date", "status"]

def calculate_ipv4_cidr_prefix(ip_count: int) -> int:
    """IPv4アドレスの数からCIDRプレフィックスを計算する"""
    if ip_count <= 0 or (ip_count & (ip_count - 1)) != 0:
        raise ValueError("IPv4アドレスの数は2のべき乗でなければなりません。")
    return 32 - int(math.log2(ip_count))

def main():
    for nic_name, url in REGISTRYS.items():
        #print(nic_name, url)

        data = None
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.text
        except:
            continue

        lines = data.strip().split("\n")
        addresses = []
        for line in lines:
            if line.startswith("#"):
                continue

            # 行を分割してリストにする
            row = line.strip().split("|")

            # version line は除外
            if row[0] != nic_name:
                continue

            # summary line は除外
            if row[1] == "*" and row[3] == "*":
                continue

            # ASN は除外
            if row[2] == "asn":
                continue

            network = None
            if row[2] == "ipv4":
                try:
                    prefix = calculate_ipv4_cidr_prefix(int(row[4]))
                    network = ipaddress.ip_network(f"{row[3]}/{prefix}")
                except ValueError:
                    network = None
            elif row[2] == "ipv6":
                try:
                    network = ipaddress.ip_network(f"{row[3]}/{row[4]}")
                except ValueError:
                    network = None

            row.insert(0, str(network))

            addresses.append(row[0:8])

        df = pl.DataFrame(addresses, schema=COLUMN_NAMES, orient="row")
        df.write_csv(f"registry_{nic_name}.csv")

if __name__ == "__main__":
    main()
