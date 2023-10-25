import keyring

# Set the API key in the system's keyring
keyring.set_password("openai", "api_key", "")
