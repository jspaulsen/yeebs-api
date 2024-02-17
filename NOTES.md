# Need a job that periodically reads the tokens and refreshes them
# (Maybe every 2 minutes? Spotify is 1 hour, Twitch is 30 days)
# Create a lock on the row to prevent using an expired token

# For PubSub, we need to track user's subscriptions to a topic per connection; we're limited to 50.