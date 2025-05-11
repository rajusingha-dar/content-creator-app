# app/entrypoint_agent/agent.py
import json
import datetime
from sqlalchemy.orm import Session
from app.services.youtube_service import YouTubeService
from app.entrypoint_agent.llm_handler import LLMHandler
from app.models.trend_analysis import TrendAnalysis
from app.utils.logger import get_logger

logger = get_logger(__name__)

class TrendingVideoAgent:
    def __init__(self):
        try:
            self.youtube_service = YouTubeService()
            self.llm_handler = LLMHandler()
            logger.info("TrendingVideoAgent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TrendingVideoAgent: {str(e)}", exc_info=True)
            raise
    
    async def process_query(self, user_prompt, user_id, db: Session):
        """
        Process a user query and return trending videos
        
        Args:
            user_prompt (str): The user's query about trending videos
            user_id (int): The ID of the user making the request
            db (Session): The database session
            
        Returns:
            dict: The response with trending videos and analysis
        """
        try:
            logger.info(f"Processing query: '{user_prompt}' for user_id: {user_id}")
            
            # 1. Extract category from user prompt
            category = self.llm_handler.extract_category(user_prompt)
            
            # 2. Fetch trending videos from YouTube
            videos = self.youtube_service.get_trending_videos(category)
            
            if not videos:
                logger.warning(f"No videos found for category: {category}")
                return {
                    "success": False,
                    "message": f"No trending videos found for '{category}'",
                    "category": category,
                    "videos": []
                }
            
            # 3. Analyze engagement and rank videos
            ranked_videos = self.youtube_service.analyze_engagement(videos)
            
            # 4. Analyze trends using LLM
            trend_analysis = self.llm_handler.analyze_trends(ranked_videos, category)
            
            # 5. Format response for frontend
            formatted_videos = []
            for video in ranked_videos:
                snippet = video.get('snippet', {})
                stats = video.get('statistics', {})
                
                formatted_videos.append({
                    "id": video.get('id'),
                    "title": snippet.get('title'),
                    "channelTitle": snippet.get('channelTitle'),
                    "publishedAt": snippet.get('publishedAt'),
                    "thumbnail": snippet.get('thumbnails', {}).get('high', {}).get('url'),
                    "viewCount": stats.get('viewCount'),
                    "likeCount": stats.get('likeCount'),
                    "commentCount": stats.get('commentCount'),
                    "engagementScore": video.get('engagement', {}).get('score', 0)
                })
            
            # 6. Store analysis in database
            db_analysis = TrendAnalysis(
                user_id=user_id,
                query=user_prompt,
                platform="youtube",
                trend_strength=float(trend_analysis.get('trend_strength', 5)),
                trend_direction=trend_analysis.get('trend_direction', 'stable'),
                summary=trend_analysis.get('summary', ''),
                insights=trend_analysis.get('insights', ''),
                recommendations=trend_analysis.get('recommendations', ''),
                metrics=json.dumps({
                    "video_count": len(videos),
                    "avg_views": sum(int(v.get('statistics', {}).get('viewCount', 0)) for v in videos) / len(videos) if videos else 0,
                    "avg_likes": sum(int(v.get('statistics', {}).get('likeCount', 0)) for v in videos) / len(videos) if videos else 0,
                    "avg_comments": sum(int(v.get('statistics', {}).get('commentCount', 0)) for v in videos) / len(videos) if videos else 0
                }),
                full_response=json.dumps({
                    "category": category,
                    "videos": formatted_videos,
                    "analysis": trend_analysis
                })
            )
            
            db.add(db_analysis)
            db.commit()
            db.refresh(db_analysis)
            logger.info(f"Stored trend analysis in database with ID: {db_analysis.id}")
            
            # 7. Return response
            return {
                "success": True,
                "category": category,
                "videos": formatted_videos,
                "analysis": trend_analysis,
                "analysis_id": db_analysis.id
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            # Rollback transaction if an error occurred
            db.rollback()
            return {
                "success": False,
                "message": "An error occurred while processing your request",
                "error": str(e)
            }