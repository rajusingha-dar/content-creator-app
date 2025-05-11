# app/services/youtube_service.py (Updated)
import googleapiclient.discovery
import googleapiclient.errors
import datetime
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class YouTubeService:
    def __init__(self):
        try:
            self.api_key = settings.YOUTUBE_API_KEY
            self.youtube = googleapiclient.discovery.build(
                "youtube", "v3", developerKey=self.api_key
            )
            logger.info("YouTube API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize YouTube API client: {str(e)}", exc_info=True)
            raise
    
    def get_trending_videos(self, category, max_results=10):
        """
        Fetch trending videos from YouTube based on category.
        
        Args:
            category (str): Category or search term
            max_results (int): Maximum number of results
        
        Returns:
            list: List of video data dictionaries
        """
        try:
            logger.info(f"Fetching trending videos for category: {category}")
            
            # First try searching for the exact category
            search_response = self.youtube.search().list(
                q=category,
                part="id,snippet",
                maxResults=max_results,
                type="video",
                order="viewCount",  # Sort by view count
                relevanceLanguage="en"
            ).execute()
            
            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
            
            # If no results, try with broader category terms
            if not video_ids and len(category.split()) > 1:
                broader_term = category.split()[0]  # Use just the first word
                logger.info(f"No results for '{category}', trying broader term: '{broader_term}'")
                
                search_response = self.youtube.search().list(
                    q=broader_term,
                    part="id,snippet",
                    maxResults=max_results,
                    type="video",
                    order="viewCount",
                    relevanceLanguage="en"
                ).execute()
                
                video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
            
            # If still no results, try getting generally trending videos
            if not video_ids:
                logger.info(f"No results for '{category}', fetching general trending videos")
                
                # Get videos from trending
                videos_response = self.youtube.videos().list(
                    part="snippet,statistics,contentDetails",
                    chart="mostPopular",
                    regionCode="US",  # You might want to make this dynamic based on user location
                    maxResults=max_results
                ).execute()
                
                return videos_response.get('items', [])
            
            # If we have video IDs, get detailed information
            if video_ids:
                logger.info(f"Found {len(video_ids)} videos, fetching details")
                
                videos_response = self.youtube.videos().list(
                    part="snippet,statistics,contentDetails",
                    id=",".join(video_ids)
                ).execute()
                
                return videos_response.get('items', [])
            
            return []
            
        except googleapiclient.errors.HttpError as e:
            logger.error(f"YouTube API HTTP error: {str(e)}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"Error fetching trending videos: {str(e)}", exc_info=True)
            return []
    
    def analyze_engagement(self, videos):
        """
        Calculate engagement metrics for videos.
        
        Args:
            videos (list): List of video data from YouTube API
            
        Returns:
            list: Enhanced video data with engagement scores
        """
        try:
            now = datetime.datetime.now(datetime.timezone.utc)
            
            for video in videos:
                stats = video.get('statistics', {})
                
                # Extract metrics with safe defaults
                views = int(stats.get('viewCount', 0))
                likes = int(stats.get('likeCount', 0))
                comments = int(stats.get('commentCount', 0))
                
                # Calculate recency (days since publication)
                published_at = video.get('snippet', {}).get('publishedAt', '')
                if published_at:
                    published_date = datetime.datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    days_since_published = (now - published_date).days
                    recency_score = max(0, 1 - (days_since_published / 30))  # Higher score for newer videos
                else:
                    recency_score = 0
                
                # Calculate engagement score with safe division
                engagement_score = (
                    views * 0.4 +
                    likes * 0.3 +
                    comments * 0.2 +
                    recency_score * 100000  # Boost recency importance
                )
                
                # Add engagement data to video
                video['engagement'] = {
                    'score': engagement_score,
                    'views': views,
                    'likes': likes,
                    'comments': comments,
                    'recency_score': recency_score
                }
            
            # Sort by engagement score
            return sorted(videos, key=lambda x: x.get('engagement', {}).get('score', 0), reverse=True)
        except Exception as e:
            logger.error(f"Error analyzing engagement: {str(e)}", exc_info=True)
            # Return unsorted videos if error occurs
            return videos