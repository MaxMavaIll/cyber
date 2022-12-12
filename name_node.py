
chains = {
    'Mainnet': {
        'juno': {'bin': '/root/go/bin/junod', 'node': 'https://juno-rpc.polkachu.com:443', 
                'parameters': {'min_signed_per_window': 5, 'signed_blocks_window': 10000, 'skipped_blocks_allowed': 10000 * (100 - 5) / 100, 'blok_time': 5.5 }},
        'bostrom': {'bin': '/root/go/bin/cyber', 'node': 'https://rpc.bostrom.cybernode.ai:443', 
                'parameters': {'min_signed_per_window': 75, 'signed_blocks_window': 8000, 'skipped_blocks_allowed': 8000 * (100 - 75) / 100, 'blok_time': 5.5 }}
        }, 
    'Testnet': {
        'uptick': {'bin': '/root/go/bin/uptickd', 'node': 'https://uptick-testnet.nodejumper.io:443', 
                'parameters': {'min_signed_per_window': 50, 'signed_blocks_window': 14000, 'blok_time': 5.5 }}
        }
}

name = "juno"
min_signed_per_window = 5
signed_blocks_window = 10000

skipped_blocks_allowed = int( signed_blocks_window * ( (100 - min_signed_per_window) / 100 ) ) # не допуста кількість пропущених блоків
time_jail = skipped_blocks_allowed * 5.5 # відповідь в секундах
