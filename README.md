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

## Generating Secrets 

### Generating AES Key

Python can be used to generate a key for AES encryption. This can be done using the following code:

```python
import secrets

key = secrets.token_bytes(16)
print(key.hex())
```

Alternatively, _any_ 32 character hex string can be used as a key as long as it's random.

### Generating JWT Secret Key

Similarly, a secret key for JWT can be generated using the same method as above. The key should be 32 characters long.

## Required Environment Variables

The following environment variables are required to run the service:

- `TWITCH_CLIENT_ID` - The client ID for the Twitch Application
- `TWITCH_CLIENT_SECRET` - The client secret for the Twitch Application
- `DATABASE_URL` - The URL for the database
- `AES_ENCRYPTION_KEY` - The key for AES encryption, used to encrypt/decrypt the Twitch OAuth tokens and refresh tokens
- `JWT_SECRET_KEY` - The key for JWT, used to sign the JWT tokens
