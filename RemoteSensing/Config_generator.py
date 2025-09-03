from sentinelhub import SHConfig

config = SHConfig()
config.sh_client_id = "sh-140573ad-defa-41d4-96e9-eb114e38379a"
config.sh_client_secret = "wacmrBkcZmRNRwDzJjDA4mFYrLTVSoBV"
config.sh_base_url = "https://sh.dataspace.copernicus.eu"
config.save()  # guarda en ~/.sentinelhub/config.json
print("Base URL efectiva:", config.sh_base_url)
