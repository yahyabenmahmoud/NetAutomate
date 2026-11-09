# =====================================================================
# services/network.py
# Fonctions de traitement réseau utilisées par les routeurs de l'API.
# Bibliothèques : socket (DNS/TCP), ipaddress (IP/sous-réseaux),
#                 psutil (interfaces), os/time (outils généraux).
# =====================================================================

# --- Imports de la bibliothèque standard Python ---
import ipaddress          # calcul et validation des adresses IP / sous-réseaux
import os                 # lecture des variables d'environnement
import socket             # résolution DNS et connexions TCP
import time               # mesure de la latence
from typing import List, Optional   # annotations de types (listes, valeur optionnelle)

# --- Bibliothèque externe ---
import psutil             # informations système : interfaces réseau

# --- Modèles de données (définis dans models/schemas.py) ---
from models.schemas import (ConnectivityResult, Device, DnsResult, InterfaceInfo,
                            NetworkConfig, SubnetInfo)

# Liste blanche par défaut des cibles autorisées pour les diagnostics.
# Elle peut être remplacée par la variable d'environnement ALLOWED_TARGETS.
# Format : noms de domaine ou réseaux CIDR, séparés par des virgules.
DEFAULT_ALLOWED = "localhost,127.0.0.1,example.com,192.168.56.0/24"

# Inventaire statique des équipements réseau (utilisé par GET /api/devices).
# Chaque élément est un dictionnaire converti plus tard en modèle Device.
DEVICES = [
    {"id": 1, "name": "core-router-01", "type": "router", "ip": "192.168.56.1",
     "location": "Salle serveur", "status": "active"},
    {"id": 2, "name": "access-switch-01", "type": "switch", "ip": "192.168.56.2",
     "location": "Baie A", "status": "active"},
    {"id": 3, "name": "edge-firewall-01", "type": "firewall", "ip": "192.168.56.3",
     "location": "Baie A", "status": "active"},
    {"id": 4, "name": "wifi-ap-01", "type": "access-point", "ip": "192.168.56.4",
     "location": "Etage 1", "status": "maintenance"},
    {"id": 5, "name": "netdevops-vm", "type": "server", "ip": "192.168.56.10",
     "location": "VirtualBox", "status": "active"},
]


# ---------- Autorisation des cibles (liste blanche) ----------
def _allowed_entries() -> List[str]:
    # Lit ALLOWED_TARGETS dans l'environnement, sinon utilise la valeur par défaut
    raw = os.getenv("ALLOWED_TARGETS", DEFAULT_ALLOWED)
    # Découpe sur les virgules, supprime les espaces, met en minuscules,
    # et ignore les entrées vides
    return [x.strip().lower() for x in raw.split(",") if x.strip()]


def is_target_allowed(host: str) -> bool:
    # Normalise l'hôte demandé (espaces retirés, minuscules)
    host = host.strip().lower()
    # Compare l'hôte à chaque entrée de la liste blanche
    for entry in _allowed_entries():
        if "/" in entry:
            # Entrée de type réseau CIDR (ex. 192.168.56.0/24)
            try:
                # Vrai si l'hôte est une adresse IP contenue dans ce réseau
                if ipaddress.ip_address(host) in ipaddress.ip_network(entry, strict=False):
                    return True
            except ValueError:
                # L'hôte n'est pas une IP (c'est un nom) : on passe à l'entrée suivante
                continue
        elif host == entry or host.endswith("." + entry):
            # Entrée de type nom de domaine : correspondance exacte
            # ou sous-domaine (www.example.com pour example.com)
            return True
    # Aucune entrée ne correspond : cible refusée
    return False


# ---------- Validation IPv4 ----------
def is_valid_ipv4(value: str) -> bool:
    try:
        # Lève ValueError si la chaîne n'est pas une IPv4 valide
        ipaddress.IPv4Address(value)
        return True
    except ValueError:
        return False


# ---------- Interfaces et configuration (psutil) ----------
def list_interfaces() -> List[InterfaceInfo]:
    # État de chaque interface (up/down, vitesse, MTU), indexé par nom
    stats = psutil.net_if_stats()
    result = []
    # net_if_addrs() renvoie, pour chaque interface, la liste de ses adresses
    for name, addrs in psutil.net_if_addrs().items():
        ipv4, ipv6, mac = [], [], None
        for a in addrs:
            if a.family == socket.AF_INET:
                # Adresse IPv4
                ipv4.append(a.address)
            elif a.family == socket.AF_INET6:
                # Adresse IPv6 ; on retire le suffixe de zone (ex. %eth0)
                ipv6.append(a.address.split("%")[0])
            elif a.family == psutil.AF_LINK:
                # Adresse MAC (couche liaison)
                mac = a.address
        # Statistiques de cette interface (None si absentes)
        st = stats.get(name)
        # Construit l'objet de réponse validé par Pydantic
        result.append(InterfaceInfo(
            name=name, is_up=bool(st and st.isup),
            speed_mbps=st.speed if st else 0, mtu=st.mtu if st else 0,
            ipv4=ipv4, ipv6=ipv6, mac=mac))
    return result


def _default_gateway() -> Optional[str]:
    # Lit la table de routage Linux pour trouver la passerelle par défaut
    try:
        with open("/proc/net/route") as f:
            next(f)  # saute la ligne d'en-tête
            for line in f:
                fields = line.split()
                # Destination 00000000 = route par défaut ;
                # flag 2 (RTF_GATEWAY) = route passant par une passerelle
                if fields[1] == "00000000" and int(fields[3], 16) & 2:
                    # L'adresse est en hexadécimal little-endian :
                    # on la convertit en 4 octets puis en notation pointée
                    return socket.inet_ntoa(int(fields[2], 16).to_bytes(4, "little"))
    except (OSError, IndexError, ValueError):
        # Fichier absent (autre OS) ou format inattendu : on ignore
        pass
    return None


def _dns_servers() -> List[str]:
    servers = []
    try:
        # Les serveurs DNS configurés sont listés dans /etc/resolv.conf
        with open("/etc/resolv.conf") as f:
            for line in f:
                # Lignes de la forme : nameserver 8.8.8.8
                if line.startswith("nameserver"):
                    servers.append(line.split()[1])
    except OSError:
        # Fichier illisible : on renvoie une liste vide
        pass
    return servers


def get_network_config() -> NetworkConfig:
    # Rassemble le nom d'hôte, le FQDN, la passerelle et les serveurs DNS
    return NetworkConfig(hostname=socket.gethostname(), fqdn=socket.getfqdn(),
                         default_gateway=_default_gateway(), dns_servers=_dns_servers())


# ---------- Diagnostics (socket) ----------
def resolve_dns(hostname: str) -> DnsResult:
    # Interroge le résolveur DNS ; lève socket.gaierror si le nom est introuvable
    infos = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
    # i[4][0] = adresse IP ; l'ensemble {} supprime les doublons, sorted() trie
    return DnsResult(hostname=hostname, addresses=sorted({i[4][0] for i in infos}))


def check_connectivity(host: str, port: int, timeout: float = 3.0) -> ConnectivityResult:
    # Démarre le chronomètre avant la tentative de connexion
    start = time.perf_counter()
    try:
        # Tente une connexion TCP complète ; le timeout évite de bloquer le serveur
        with socket.create_connection((host, port), timeout=timeout):
            # Latence en millisecondes (le with ferme la connexion ensuite)
            latency = (time.perf_counter() - start) * 1000
        return ConnectivityResult(host=host, port=port, reachable=True,
                                  latency_ms=round(latency, 2))
    except OSError as exc:
        # Refus, timeout, réseau injoignable... : cible considérée non joignable
        return ConnectivityResult(host=host, port=port, reachable=False, error=str(exc))


# ---------- Sous-réseaux (ipaddress) ----------
def calculate_subnet(cidr: str) -> SubnetInfo:
    # strict=False accepte une adresse d'hôte (192.168.1.77/24) et la ramène au réseau.
    # Lève ValueError si le CIDR est invalide ou s'il s'agit d'IPv6.
    net = ipaddress.IPv4Network(cidr, strict=False)
    # Nombre total d'adresses du réseau (2^(32 - préfixe))
    total = net.num_addresses
    if net.prefixlen == 32:
        # /32 : une seule adresse, un seul hôte
        usable, first, last = 1, net.network_address, net.network_address
    elif net.prefixlen == 31:
        # /31 : lien point à point (RFC 3021), 2 hôtes sans adresse de broadcast
        usable, first, last = 2, net.network_address, net.broadcast_address
    else:
        # Cas général : on retire l'adresse réseau et l'adresse de broadcast
        usable = total - 2
        # Premier hôte = réseau + 1 ; dernier hôte = broadcast - 1
        first, last = net.network_address + 1, net.broadcast_address - 1
    return SubnetInfo(
        cidr=str(net), network_address=str(net.network_address),
        broadcast_address=str(net.broadcast_address), netmask=str(net.netmask),
        wildcard=str(net.hostmask),     # inverse du masque (utilisé dans les ACL)
        prefix_length=net.prefixlen,
        total_addresses=total, usable_hosts=usable,
        first_host=str(first), last_host=str(last))


# ---------- Inventaire ----------
def list_devices() -> List[Device]:
    # Transforme chaque dictionnaire de DEVICES en objet Device validé
    # (**d déballe les clés/valeurs comme arguments nommés)
    return [Device(**d) for d in DEVICES]