# app/api/trending.py (Updated)
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.utils.logger import get_logger
from app.services.youtube_service import YouTubeService
from app.entrypoint_agent.llm_handler import LLMHandler
import json

logger = get_logger(__name__)
router = APIRouter()

class TrendingRequest(BaseModel):
    prompt: str

# Initialize the services
youtube_service = YouTubeService()
llm_handler = LLMHandler()

# @router.post("/analyze")
# async def analyze_trending(
#     request_data: TrendingRequest,
#     request: Request,
#     db: Session = Depends(get_db)
# ):
#     """
#     Analyze trending videos based on the user's prompt
#     """
#     try:
#         logger.info(f"Analyzing trending videos for prompt: {request_data.prompt}")
        
#         # Extract category from prompt
#         category = request_data.prompt.strip()
        
#         # Fetch videos - use a larger maximum result to ensure we get some videos
#         videos = youtube_service.get_trending_videos(category, max_results=20)
        
#         if not videos:
#             logger.warning(f"No videos found for category: {category}")
#             return {
#                 "success": False,
#                 "message": f"No trending videos found for '{category}'",
#                 "category": category
#             }
        
#         # Analyze and rank videos
#         ranked_videos = youtube_service.analyze_engagement(videos)
        
#         # Format videos for frontend
#         formatted_videos = []
#         for video in ranked_videos:
#             snippet = video.get('snippet', {})
#             stats = video.get('statistics', {})
            
#             formatted_videos.append({
#                 "id": video.get('id'),
#                 "title": snippet.get('title', 'Untitled'),
#                 "channelTitle": snippet.get('channelTitle', 'Unknown Channel'),
#                 "publishedAt": snippet.get('publishedAt', ''),
#                 "thumbnail": snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
#                 "viewCount": int(stats.get('viewCount', 0)),
#                 "likeCount": int(stats.get('likeCount', 0)),
#                 "commentCount": int(stats.get('commentCount', 0)),
#                 "engagementScore": video.get('engagement', {}).get('score', 0)
#             })
        
#         # Generate analysis
#         trend_analysis = {
#             "trend_strength": 7,  # Default value
#             "trend_direction": "growing",
#             "summary": f"Analysis of trending {category} videos on YouTube",
#             "insights": f"These videos about {category} are gaining popularity with high engagement",
#             "recommendations": f"Consider creating content about {category} with similar engaging aspects to these trending videos"
#         }
        
#         # Store in database if user is authenticated
#         try:
#             user_id = request.session.get("user_id")
#             if user_id:
#                 from app.models.trend_analysis import TrendAnalysis
                
#                 db_analysis = TrendAnalysis(
#                     user_id=user_id,
#                     query=request_data.prompt,
#                     platform="youtube",
#                     trend_strength=trend_analysis.get('trend_strength', 5),
#                     trend_direction=trend_analysis.get('trend_direction', 'stable'),
#                     summary=trend_analysis.get('summary', ''),
#                     insights=trend_analysis.get('insights', ''),
#                     recommendations=trend_analysis.get('recommendations', ''),
#                     metrics=json.dumps({
#                         "video_count": len(videos),
#                         "avg_views": sum(int(v.get('statistics', {}).get('viewCount', 0)) for v in videos) / len(videos) if videos else 0,
#                     }),
#                     full_response=json.dumps({
#                         "category": category,
#                         "videos": formatted_videos[:10],
#                         "analysis": trend_analysis
#                     })
#                 )
                
#                 db.add(db_analysis)
#                 db.commit()
#                 logger.info(f"Stored trend analysis in database")
#         except Exception as e:
#             logger.error(f"Error storing trend analysis: {str(e)}")
#             # Continue even if storage fails
        
#         # Return response
#         return {
#             "success": True,
#             "category": category,
#             "videos": formatted_videos,
#             "analysis": trend_analysis
#         }
        
#     except Exception as e:
#         logger.error(f"Error analyzing trending videos: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred: {str(e)}"
#         )


# app/api/trending.py (update the analyze_trending function)

@router.post("/analyze")
async def analyze_trending(
    request_data: TrendingRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Analyze trending videos based on the user's prompt
    """
    try:
        logger.info(f"Analyzing trending videos for prompt: {request_data.prompt}")
        
        # Extract category from prompt
        category = request_data.prompt.strip()
        
        # Fetch videos
        videos = youtube_service.get_trending_videos(category, max_results=20)
        
        if not videos:
            logger.warning(f"No videos found for category: {category}")
            return {
                "success": False,
                "message": f"No trending videos found for '{category}'",
                "category": category
            }
        
        # Analyze and rank videos
        ranked_videos = youtube_service.analyze_engagement(videos)
        
        # Format videos for frontend
        formatted_videos = []
        for video in ranked_videos:
            snippet = video.get('snippet', {})
            stats = video.get('statistics', {})
            
            formatted_videos.append({
                "id": video.get('id'),
                "title": snippet.get('title', 'Untitled'),
                "channelTitle": snippet.get('channelTitle', 'Unknown Channel'),
                "publishedAt": snippet.get('publishedAt', ''),
                "thumbnail": snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                "viewCount": int(stats.get('viewCount', 0)),
                "likeCount": int(stats.get('likeCount', 0)),
                "commentCount": int(stats.get('commentCount', 0)),
                "engagementScore": video.get('engagement', {}).get('score', 0)
            })
        
        # Generate analysis
        trend_analysis = {
            "trend_strength": 7,
            "trend_direction": "growing",
            "summary": f"Analysis of trending {category} videos on YouTube",
            "insights": f"These videos about {category} are gaining popularity with high engagement",
            "recommendations": f"Consider creating content about {category} with similar engaging aspects to these trending videos"
        }
        
        # Try to store in database if user is authenticated
        try:
            # Try to get user ID from token (safer than accessing session)
            user_id = None
            token = request.cookies.get("access_token")
            
            if token and token.startswith("Bearer "):
                # Extract token
                token = token.replace("Bearer ", "")
                
                # Decode token to get user ID
                from app.utils.security import decode_access_token
                payload = decode_access_token(token)
                
                if payload:
                    # Get username from token
                    username = payload.get("sub")
                    
                    # Look up user in database
                    if username:
                        user = db.query(User).filter(User.username == username).first()
                        if user:
                            user_id = user.id
            
            # If we have a user ID, store the analysis
            if user_id:
                from app.models.trend_analysis import TrendAnalysis
                
                db_analysis = TrendAnalysis(
                    user_id=user_id,
                    query=request_data.prompt,
                    platform="youtube",
                    trend_strength=trend_analysis.get('trend_strength', 5),
                    trend_direction=trend_analysis.get('trend_direction', 'stable'),
                    summary=trend_analysis.get('summary', ''),
                    insights=trend_analysis.get('insights', ''),
                    recommendations=trend_analysis.get('recommendations', ''),
                    metrics=json.dumps({
                        "video_count": len(videos),
                        "avg_views": sum(int(v.get('statistics', {}).get('viewCount', 0)) for v in videos) / len(videos) if videos else 0,
                    }),
                    full_response=json.dumps({
                        "category": category,
                        "videos": formatted_videos[:10],
                        "analysis": trend_analysis
                    })
                )
                
                db.add(db_analysis)
                db.commit()
                logger.info(f"Stored trend analysis in database")
        except Exception as e:
            logger.error(f"Error storing trend analysis: {str(e)}")
            # Continue even if storage fails
        
        # Return response
        return {
            "success": True,
            "category": category,
            "videos": formatted_videos,
            "analysis": trend_analysis
        }
        
    except Exception as e:
        logger.error(f"Error analyzing trending videos: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )