from enum import StrEnum

from pydantic import BaseModel

# channel.follow
# channel.ad_break.begin
# channel.chat.message
# channel.subscribe # First subscribe
# channel.subscription.gift
# channel.subscription.message # Resubscribes
# channel.cheer
# channel.raid
# channel.ban
# channel.unban
# stream.online
# stream.offline

class EventType(StrEnum):
    CHANNEL_FOLLOW = "channel.follow"
    CHANNEL_AD_BREAK_BEGIN = "channel.ad_break.begin"
    CHANNEL_CHAT_MESSAGE = "channel.chat.message"
    CHANNEL_SUBSCRIBE = "channel.subscribe"
    CHANNEL_SUBSCRIPTION_GIFT = "channel.subscription.gift"
    CHANNEL_SUBSCRIPTION_MESSAGE = "channel.subscription.message"
    CHANNEL_CHEER = "channel.cheer"
    CHANNEL_RAID = "channel.raid"
    CHANNEL_BAN = "channel.ban"
    CHANNEL_UNBAN = "channel.unban"
    STREAM_ONLINE = "stream.online"
    STREAM_OFFLINE = "stream.offline"


class TransportMethod(BaseModel):
    method: str = "webhook"
    callback: str
    secret: str


class EventSubConditionBase(BaseModel):
    pass


class ChatMessageSubscriptionCondition(EventSubConditionBase):
    broadcaster_user_id: str
    user_id: str


class ChannelChatMessageSubscriptionCondition(ChatMessageSubscriptionCondition):
    pass
