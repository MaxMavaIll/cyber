
chains = {
    'Mainnet': {
        'juno': {'bin': '/root/go/bin/junod', 'node': 'https://juno-rpc.polkachu.com:443', 
                'parameters': {'min_signed_per_window': 5, 'signed_blocks_window': 10000, 'blok_time': 5.5 }},
        'bostrom': {'bin': '/root/go/bin/cyber', 'node': 'https://rpc.bostrom.cybernode.ai:443', 
                'parameters': {'min_signed_per_window': 75, 'signed_blocks_window': 8000, 'blok_time': 5.5 }}
        }, 
    'Testnet': {
        'uptick': {'bin': '/root/go/bin/uptickd', 'node': 'https://uptick-testnet.nodejumper.io:443', 
                'parameters': {'min_signed_per_window': 50, 'signed_blocks_window': 14000, 'blok_time': 5.5 }}
        }
}


for network in chains:
    for chain in chains[network]:
        chains[network][chain]['parameters']['skipped_blocks_allowed'] = chains[network][chain]['parameters']['signed_blocks_window'] * ( 100 - chains[network][chain]['parameters']['min_signed_per_window']) / 100
name = "juno"
min_signed_per_window = 5
signed_blocks_window = 10000

skipped_blocks_allowed = int( signed_blocks_window * ( (100 - min_signed_per_window) / 100 ) ) # не допуста кількість пропущених блоків
time_jail = skipped_blocks_allowed * 5.5 # відповідь в секундах
