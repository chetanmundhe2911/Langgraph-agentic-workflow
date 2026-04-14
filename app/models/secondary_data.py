"""Collection: secondary_data — Social media & digital footprint per platform."""
from typing import Optional, List
from datetime import date, datetime
from pydantic import Field
from .base import MongoModel


class SocialPlatformBase(MongoModel):
    profile_url: Optional[str] = None
    found: Optional[bool] = None
    followers_count: Optional[int] = None
    posts_count: Optional[int] = None
    avg_likes_per_post: Optional[float] = None
    avg_comments_per_post: Optional[float] = None
    active_months: List[str] = Field(default_factory=list)
    inactive_months: List[str] = Field(default_factory=list)
    last_post_date: Optional[date] = None
    last_profile_update: Optional[date] = None
    last_photo_updated: Optional[date] = None
    content_themes: List[str] = Field(default_factory=list)
    post_sentiment_avg: Optional[float] = None
    response_rate_pct: Optional[float] = None
    avg_response_time_hrs: Optional[float] = None


class FacebookData(SocialPlatformBase):
    user_id_handle: Optional[str] = None
    friends_count: Optional[int] = None
    posts_count_public: Optional[int] = None
    avg_posts_per_month: Optional[float] = None
    public_photos_count: Optional[int] = None
    groups_public: List[str] = Field(default_factory=list)


class InstagramData(SocialPlatformBase):
    handle: Optional[str] = None
    is_private: Optional[bool] = None
    following_count: Optional[int] = None
    reels_count: Optional[int] = None
    avg_reel_views: Optional[float] = None
    post_frequency_per_month: Optional[float] = None
    story_highlights: List[str] = Field(default_factory=list)


class LinkedInData(MongoModel):
    profile_url: Optional[str] = None
    found: Optional[bool] = None
    headline: Optional[str] = None
    connections_count: Optional[int] = None
    endorsements_count: Optional[int] = None
    recommendations_count: Optional[int] = None
    posts_count: Optional[int] = None
    last_post_date: Optional[date] = None
    career_consistency_score: Optional[float] = None
    skill_endorsements: List[str] = Field(default_factory=list)
    content_themes: List[str] = Field(default_factory=list)


class TwitterData(MongoModel):
    profile_url: Optional[str] = None
    handle: Optional[str] = None
    found: Optional[bool] = None
    followers_count: Optional[int] = None
    following_count: Optional[int] = None
    tweets_count: Optional[int] = None
    avg_tweets_per_month: Optional[float] = None
    tweet_topics: List[str] = Field(default_factory=list)
    political_lean_signal: Optional[str] = None
    content_themes: List[str] = Field(default_factory=list)
    post_sentiment_avg: Optional[float] = None


class YouTubeData(MongoModel):
    channel_url: Optional[str] = None
    found: Optional[bool] = None
    subscribers_count: Optional[int] = None
    videos_count: Optional[int] = None
    content_themes: List[str] = Field(default_factory=list)


class PortfolioData(MongoModel):
    portfolio_url: Optional[str] = None
    found: Optional[bool] = None
    type: Optional[str] = None  # personal_blog | github | behance | dribbble | other
    quality_score: Optional[float] = None


class AIDigitalAnalysis(MongoModel):
    digital_presence_score: Optional[float] = None
    authenticity_score: Optional[float] = None
    consistency_across_platforms: Optional[float] = None
    red_flags: List[str] = Field(default_factory=list)
    personality_inferred: List[str] = Field(default_factory=list)
    ai_summary: Optional[str] = None
    analysed_at: Optional[datetime] = None


class SecondaryDataDocument(MongoModel):
    """MongoDB collection: secondary_data"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    last_scraped_at: Optional[datetime] = None
    facebook: Optional[FacebookData] = None
    instagram: Optional[InstagramData] = None
    linkedin: Optional[LinkedInData] = None
    twitter: Optional[TwitterData] = None
    youtube: Optional[YouTubeData] = None
    portfolio: Optional[PortfolioData] = None
    ai_analysis: Optional[AIDigitalAnalysis] = None
