#!/usr/bin/env python3.12

import ipaddress
import os
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

def calculate_ipv4_networks(start_ip, ip_count: int) -> list:
    networks = []
    remaining_ips = ip_count
    current_ip = start_ip

    while remaining_ips > 0:
        # 残りのIP数に収まる最大の2のべき乗を計算
        max_prefix = 32 - (remaining_ips - 1).bit_length()
        try:
            network = ipaddress.ip_network(f"{current_ip}/{max_prefix}", strict=True)
        except ValueError:
            pass
            # IPアドレスが無効な場合、サイズを小さくして再計算
            for max_prefix in range(max_prefix+1, 32, 1):
                try:
                    network = ipaddress.ip_network(f"{current_ip}/{max_prefix}", strict=True)
                    break
                except ValueError:
                    continue

        networks.append(network)

        # 次のネットワークの開始アドレスを計算
        remaining_ips -= network.num_addresses
        current_ip = network[-1] + 1

    return networks

def main():
    for nic_name, url in REGISTRYS.items():
        #print(nic_name, url)

        data = None
        if os.path.isfile(f"./nic/{nic_name}"):
            with open(f"./nic/{nic_name}", "r") as fp:
                data = fp.read()
        else:
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.text
            except:
                continue

        lines = data.strip().split("\n")
        records = []
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

            networks = []
            if row[2] == "ipv4":
                networks = calculate_ipv4_networks(ipaddress.IPv4Address(row[3]),int(row[4]))
            elif row[2] == "ipv6":
                networks = [ipaddress.ip_network(f"{row[3]}/{row[4]}", strict=False)]

            for network in networks:
                data = [
                    f"{str(network.network_address)}/{str(network.prefixlen)}",
                    row[0],  # registry
                    row[1],  # country_code
                    row[2],  # type
                    str(network.network_address),  # start
                    network.num_addresses if row[2] == "ipv4" else None,  # value
                    row[5],  # date
                    row[6],  # status
                ]
                records.append(data)

        df = pl.DataFrame(records, schema=COLUMN_NAMES, orient="row")
        df.write_csv(f"registry_{nic_name}.csv")

if __name__ == "__main__":
    main()
