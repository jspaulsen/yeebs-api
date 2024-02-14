# Required Tables

- User Table
    - user_id (pk) (auto incrementing)
    - external_user_id (unique)
    - created_at
    - updated_at

- Origin Table
    - origin_id (pk) (auto incrementing)
    - origin (varchar/enum)
    - created_at
    - updated_at

(Only origin for starters will be Twitch and Spotify)

- Authorization Token Table
    - authorization_id (pk) (auto incrementing)
    - user_id (fk) (unique with origin
    - origin_id (fk)
    - access_token (varchar, nullable)
    - refresh_token (varchar, nullable)
    - invalid_token (boolean, default false)
    - expires_at (timestamp, nullable)
    - refresh_lock (boolean, default false)
    - last_refreshed_at (timestamp, nullable)

# Need a job that periodically reads the tokens and refreshes them
# (Maybe every 2 minutes? Spotify is 1 hour, Twitch is 30 days)
# Create a lock on the row to prevent using an expired token

# For PubSub, we need to track user's subscriptions to a topic per connection; we're limited to 50.