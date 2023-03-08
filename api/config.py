import environs

env = environs.Env()
env.read_env()
API_TOKEN = env.str("MINT_SCAN_API_TOKEN")

nodes = {
    "<network>": ["/root/go/bin/<bin>","<rpc>"],
}
