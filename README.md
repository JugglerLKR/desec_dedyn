# desec_dedyn
Home Assistant deSEC dynamic dns integration (dedyn.io)

# Example configuration.yaml entry
desec_dedyn:
  domain: example.dedyn.io # full DNS
  access_token: "blablablaaV" # access token in quotes
  protocol:
    - ipv4 # (update ipv4 record)
    - ipv6 # (update ipv6 record)
# if you don't want to set ipv4 or ipv6 records just comment them
