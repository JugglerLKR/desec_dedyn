# desec_dedyn
Home Assistant deSEC dynamic dns integration (dedyn.io)

```
# Example configuration.yaml entry
desec_dedyn:
  # full DNS name
  domain: example.dedyn.io 
  # access token in quotes
  access_token: "blablablaaV"
  protocol:
    - ipv4
    - ipv6
  # if you don't want to set either ipv4 or ipv6 records just comment or remove. this means also that correspoding ipv4 (A) or ipv6 (AAAA) dns record also be removed 
```
