import socket
import dns.resolver

def resolve_with_doh(domain):
    """Resolve domain using Google's DNS-over-HTTPS"""
    try:
        # Use Google's public DNS
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '8.8.4.4']
        
        answers = resolver.resolve(domain, 'A')
        if answers:
            return str(answers[0])
    except Exception as e:
        print(f"DoH resolution failed: {e}")
        return None

# Monkey patch socket.getaddrinfo to use custom DNS
original_getaddrinfo = socket.getaddrinfo

def custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if 'animepahe' in host:
        ip = resolve_with_doh(host)
        if ip:
            # Replace host with IP
            return original_getaddrinfo(ip, port, family, type, proto, flags)
    return original_getaddrinfo(host, port, family, type, proto, flags)

socket.getaddrinfo = custom_getaddrinfo
