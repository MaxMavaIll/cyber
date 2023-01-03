import environs
import asyncio
import logging
import collections

time_wait=180
nodes = dict()
env = environs.Env()
env.read_env()
API_TOKEN = env.str("MINT_SCAN_API_TOKEN")


chains = {
    'Mainnet': {
        'juno': {'bin': '/root/go/bin/junod', 'node': 'https://juno-rpc.polkachu.com:443', 
                'parameters': {'min_signed_per_window': 5, 'signed_blocks_window': 10000, 'blok_time': 6 }},
        'bostrom': {'bin': '/root/go/bin/cyber', 'node': 'https://rpc.bostrom.cybernode.ai:443', 
                'parameters': {'min_signed_per_window': 75, 'signed_blocks_window': 8000, 'blok_time': 5.5 }},
        'gravity-bridge': {'bin': '/root/go/bin/gravity', 'node': 'https://gravity-rpc.polkachu.com:443', 
                'parameters': {'min_signed_per_window': 50, 'signed_blocks_window': 10000, 'blok_time': 6 }},
        'bitsong': {'bin': '/root/go/bin/bitsongd', 'node': 'https://bitsong.stakesystems.io:2053', 
                'parameters': {'min_signed_per_window': 5, 'signed_blocks_window': 10000, 'blok_time': 6 }},
        'teritori': {'bin': '/root/go/bin/teritorid', 'node': 'https://teritori.nodejumper.io:443', 
                'parameters': {'min_signed_per_window': 50, 'signed_blocks_window': 10000, 'blok_time': 6 }},
        'rebus': {'bin': '/root/go/bin/rebusd', 'node': 'https://rebus.nodejumper.io:443',
                'parameters': {'min_signed_per_window': 30, 'signed_blocks_window': 20000, 'blok_time': 6 }},
        'jackal': {'bin': '/root/go/bin/canined', 'node': 'https://jackal.nodejumper.io:443', 
                'parameters': {'min_signed_per_window': 5, 'signed_blocks_window': 10000, 'blok_time': 6 }},
        'stargaze': {'bin': '/root/go/bin/starsd', 'node': 'https://stargaze-rpc.polkachu.com:443', 
                'parameters': {'min_signed_per_window': 5, 'signed_blocks_window': 25000, 'blok_time': 6 }},
        'shentu': {'bin': '/root/go/bin/shentud', 'node': 'https://certik-rpc.polkachu.com:443', 
                'parameters': {'min_signed_per_window': 5, 'signed_blocks_window': 1000, 'blok_time': 6 }},
        'quicksilver': {'bin': '/root/go/bin/quicksilverd', 'node': 'https://quicksilver-rpc.polkachu.com:443', 
                'parameters': {'min_signed_per_window': 10, 'signed_blocks_window': 10000, 'blok_time': 6 }},
        'bitccana': {'bin': '/root/go/bin/bcnad', 'node': 'https://bitcanna-rpc.polkachu.com:443', 
                'parameters': {'min_signed_per_window': 50, 'signed_blocks_window': 29794, 'blok_time': 6 }},
        'assetmantle': {'bin': '/root/go/bin/mantleNode', 'node':'https://assetmantle-rpc.polkachu.com:443',
                'parameters': {'min_signed_per_window': 5, 'signed_blocks_window': 10000, 'blok_time': 6 }},
        'omniflix': {'bin': '/root/go/bin/omniflixhubd', 'node': 'https://omniflix.nodejumper.io:443', 
                'parameters': {'min_signed_per_window': 5, 'signed_blocks_window': 10000, 'blok_time': 6 }},
        'rizon': {'bin': '/root/go/bin/rizond', 'node': 'https://rizon.nodejumper.io:443', 
                'parameters': {'min_signed_per_window': 5, 'signed_blocks_window': 10000, 'blok_time': 6 }},
        'likecoin': {'bin': '/root/go/bin/liked', 'node': 'https://mainnet-node-rpc.like.co:443', 
                'parameters': {'min_signed_per_window': 50, 'signed_blocks_window': 10000, 'blok_time': 6 }},

        }, 
    'Testnet': {
        'uptick': {'bin': '/root/go/bin/uptickd', 'node': 'https://uptick-testnet.nodejumper.io:443', 
                'parameters': {'min_signed_per_window': 50, 'signed_blocks_window': 14000, 'blok_time': 6 }},
        'hypersing': {'bin': '/root/go/bin/hid-noded', 'node': 'https://hypersign-testnet-rpc.polkachu.com:443', 
                'parameters': {'min_signed_per_window': 50, 'signed_blocks_window': 10000, 'blok_time': 6 }},
        'okp4d': {'bin': '/root/go/bin/okp4d', 'node': 'https://okp4-testnet.nodejumper.io:443', 
                'parameters': {'min_signed_per_window': 5, 'signed_blocks_window': 10000, 'blok_time': 6 }}
        },
}

for network in chains:
    for chain in chains[network]:
#        exemple = [chains[network][chain]['bin'], 'q', 'slashing', 'params', '-o', 'json']
#        params = asyncio.run( run_app(exemple) )
#        chains[network][chain]['min_signed_per_window'] = float(params.get('slash_fraction_double_sign'))
#        chains[network][chain]['signed_blocks_window'] = float(params.get('signed_blocks_window'))
        chains[network][chain]['parameters']['skipped_blocks_allowed'] = chains[network][chain]['parameters']['signed_blocks_window'] * ( 100 - chains[network][chain]['parameters']['min_signed_per_window']) / 100
        nodes[chain] = [chains[network][chain]['bin'], chains[network][chain]['node']]

d = {
     "Mainnet": {},
     "Testnet": {}
}

#keys = list(chains[network].keys())
#keys.sort()
for network in chains:
    keys = list(chains[network].keys())
    keys.sort()
    for chain in keys:
        d[network][chain] = chains[network][chain]


chains = d
