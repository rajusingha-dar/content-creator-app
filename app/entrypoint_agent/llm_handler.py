# app/entrypoint_agent/llm_handler.py
import openai
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class LLMHandler:
    def __init__(self):
        try:
            self.api_key = settings.OPENAI_API_KEY
            openai.api_key = self.api_key
            logger.info("LLM handler initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LLM handler: {str(e)}", exc_info=True)
            raise
    
    def extract_category(self, user_prompt):
        """
        Extract the main category from a user prompt
        """
        try:
            prompt = f"""
            Given the user input: "{user_prompt}"
            Identify the main video category or topic the user is interested in.
            Output just the category name without any additional text.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are a helpful assistant."}, 
                         {"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=50
            )
            
            category = response.choices[0].message.content.strip()
            logger.info(f"Extracted category '{category}' from prompt: '{user_prompt}'")
            return category
            
        except Exception as e:
            logger.error(f"Error extracting category: {str(e)}", exc_info=True)
            return user_prompt.lower().strip()
    
    def analyze_trends(self, videos, category):
        """
        Analyze trends in the videos using the LLM
        """
        try:
            import json
            
            # Extract relevant data for analysis
            video_data = []
            for video in videos[:10]:
                snippet = video.get('snippet', {})
                stats = video.get('statistics', {})
                
                video_data.append({
                    'title': snippet.get('title', ''),
                    'channelTitle': snippet.get('channelTitle', ''),
                    'publishedAt': snippet.get('publishedAt', ''),
                    'views': int(stats.get('viewCount', 0)),
                    'likes': int(stats.get('likeCount', 0)),
                    'comments': int(stats.get('commentCount', 0))
                })
            
            # Create prompt for trend analysis
            prompt = f"""
            Based on the following trending YouTube videos in the '{category}' category:
            {json.dumps(video_data, indent=2)}
            
            Please analyze and provide:
            1. A trend strength score from 1-10
            2. A trend direction (growing, stable, declining)
            3. A summary of the overall trends (max 100 words)
            4. Key insights about what makes these videos successful (max 200 words)
            5. Recommendations for content creators in this space (max 200 words)
            
            Format your response as a JSON object with keys: trend_strength, trend_direction, summary, insights, recommendations
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=[{"role": "system", "content": "You are a helpful assistant skilled in analyzing YouTube trends."}, 
                         {"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=1000
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Try to parse as JSON, but handle text response as well
            try:
                analysis = json.loads(analysis_text)
            except json.JSONDecodeError:
                # If not valid JSON, extract what we can
                logger.warning("LLM did not return valid JSON. Attempting to parse text.")
                analysis = {
                    "trend_strength": 5,
                    "trend_direction": "stable",
                    "summary": analysis_text[:100],
                    "insights": analysis_text[100:300],
                    "recommendations": analysis_text[300:500]
                }
            
            logger.info(f"Generated trend analysis for '{category}'")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {str(e)}", exc_info=True)
            return {
                "trend_strength": 5,
                "trend_direction": "stable",
                "summary": f"Analysis of trending videos in {category}.",
                "insights": "Could not generate insights due to an error.",
                "recommendations": "Try again later for recommendations."
            }