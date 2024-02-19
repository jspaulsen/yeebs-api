# yeebs-api

API For Yeebs, the Twitch multi-integration

## Running Migrations

This service uses [dbmate](https://github.com/amacneil/dbmate?tab=readme-ov-file#installation) to run migrations. This is typically done automatically, built within the docker image; however, this can be run manually via `ghcr.io/amacneil/dbmate`.

### Generating new migration files

```shell
docker run --rm -it --network=host -v "$(pwd)/db:/db" ghcr.io/amacneil/dbmate new <new schema name>
```

## Building Docker Image

```shell
docker build --target production -t abc .
```

### Generating AES Key

Python can be used to generate a key for AES encryption. This can be done using the following code:

```python
import secrets
import codecs

key = secrets.token_bytes(16)
hex_key = codecs.encode(key, 'hex').decode()
```

Alternatively, _any_ 32 character hex string can be used as a key as long as it's random.