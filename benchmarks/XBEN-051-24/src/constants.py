# LGSL Configuration Constants

LGSL_VERSION = "6.2.1"

# Server type identifiers
SERVER_TYPES = {
    "source": "Source Engine",
    "minecraft": "Minecraft",
    "samp": "SA-MP",
    "fivem": "FiveM",
    "rust": "Rust",
    "http": "HTTP JSON (type 40)",
    "other": "Other"
}

# Query timeouts
QUERY_TIMEOUT = 5
CRAWL_TIMEOUT = 8

# Image routes (kept for static asset compatibility)
IMAGE_ROUTES = {
    "server_online": "static/img/cookies/success_circle.png",
    "server_offline": "static/img/cookies/error_circle.png",
    "server_querying": "static/img/cookies/new_circle.png"
}
