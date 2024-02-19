# TODO:
# Add jwt function for validating tokens (from cookies) - probably later, as it won't be needed until user routes exist
# Test and leverage Refresher task

<!-- We can use the user info to validate the access token - if the token is expired, we should try and regenerate/set cookie on the response (how?) -->
Tokens don't need to be OIDC - we need to validate it hourly (sigh)

_alternatively_, just give 

Basically, I _think_ we need to store the access token and the refresh token. `select for update` for that row, if not out of date, drop the transaction and use the token