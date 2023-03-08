import environs

env = environs.Env()
env.read_env()
API_TOKEN = env.str("MINT_SCAN_API_TOKEN")

nodes = {
    "juno": ["/root/go/bin/junod","http://65.21.132.27:28057"],
}
