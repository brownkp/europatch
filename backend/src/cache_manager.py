"""
Cache manager for module manuals and forum data.
"""
import os
import re
import logging
import requests
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import praw
from src.models import db, Module, ForumSource

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheManager:
    """Cache manager for module manuals and forum data."""
    
    def __init__(self):
        """Initialize the cache manager."""
        self.cache_dir = os.environ.get('CACHE_DIR', '/app/cache')
        self.manual_cache_dir = os.path.join(self.cache_dir, 'manuals')
        self.forum_cache_dir = os.path.join(self.cache_dir, 'forums')
        
        # Create cache directories if they don't exist
        os.makedirs(self.manual_cache_dir, exist_ok=True)
        os.makedirs(self.forum_cache_dir, exist_ok=True)
        
        # Initialize Reddit API client
        self.reddit = None
        try:
            self.reddit = praw.Reddit(
                client_id=os.environ.get('REDDIT_CLIENT_ID', 'YOUR_CLIENT_ID'),
                client_secret=os.environ.get('REDDIT_CLIENT_SECRET', 'YOUR_CLIENT_SECRET'),
                user_agent=os.environ.get('REDDIT_USER_AGENT', 'europatch:v1.0.0 (by /u/your_username)')
            )
            logger.info("Reddit API client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Reddit API client: {str(e)}")
            # Continue without Reddit API - we'll use web scraping as fallback
    
    def get_manual_content(self, module_id, manual_url, force_refresh=False):
        """
        Get manual content for a module, either from cache or by fetching from URL.
        
        Args:
            module_id (int): ID of the module
            manual_url (str): URL of the manual
            force_refresh (bool): Whether to force refresh the cache
            
        Returns:
            str: Manual content
        """
        # Check if manual content exists in database
        module = Module.query.get(module_id)
        
        # If content exists in database and is not expired, return it
        if module.manual_content and module.manual_last_updated and not force_refresh:
            # Check if manual was updated within the last 30 days
            if module.manual_last_updated > datetime.utcnow() - timedelta(days=30):
                logger.info(f"Using cached manual content from database for module {module_id}")
                return module.manual_content
        
        # If we need to fetch the manual, do so
        logger.info(f"Fetching manual content for module {module_id} from {manual_url}")
        
        try:
            # Determine file type from URL
            file_extension = os.path.splitext(manual_url)[1].lower()
            
            if file_extension in ['.pdf', '.doc', '.docx']:
                # For PDFs and Word docs, we can't easily extract text, so just store the URL
                manual_content = f"Manual available at: {manual_url}"
            else:
                # For HTML and other text-based formats, fetch and extract text
                response = requests.get(manual_url, timeout=10)
                response.raise_for_status()
                
                # Parse HTML and extract text
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.extract()
                
                # Get text
                manual_content = soup.get_text(separator='\n', strip=True)
                
                # Clean up text
                manual_content = re.sub(r'\n+', '\n', manual_content)
                manual_content = re.sub(r'\s+', ' ', manual_content)
            
            # Update module in database
            module.manual_content = manual_content
            module.manual_last_updated = datetime.utcnow()
            db.session.commit()
            
            return manual_content
        except Exception as e:
            logger.error(f"Error fetching manual content for module {module_id}: {str(e)}")
            
            # If we have existing content, return it even if it's expired
            if module.manual_content:
                return module.manual_content
            
            return f"Error fetching manual content: {str(e)}"
    
    def get_forum_data(self, module_id, module_name, source_type='all', force_refresh=False):
        """
        Get forum data for a module, either from cache or by fetching from forums.
        
        Args:
            module_id (int): ID of the module
            module_name (str): Name of the module
            source_type (str): Type of source to get data from ('all', 'reddit', 'modwiggler')
            force_refresh (bool): Whether to force refresh the cache
            
        Returns:
            list: Forum data
        """
        # Check if forum data exists in database
        existing_sources = ForumSource.query.filter_by(module_id=module_id)
        
        if source_type != 'all':
            existing_sources = existing_sources.filter_by(source_type=source_type)
        
        existing_sources = existing_sources.all()
        
        # If data exists in database and is not expired, return it
        if existing_sources and not force_refresh:
            # Check if any source was updated within the last 7 days
            recent_source = False
            for source in existing_sources:
                if source.last_updated > datetime.utcnow() - timedelta(days=7):
                    recent_source = True
                    break
            
            if recent_source:
                logger.info(f"Using cached forum data from database for module {module_id}")
                return [source.to_dict() for source in existing_sources]
        
        # If we need to fetch forum data, do so
        logger.info(f"Fetching forum data for module {module_id} ({module_name})")
        
        forum_data = []
        
        # Fetch data from Reddit
        if source_type in ['all', 'reddit']:
            try:
                reddit_data = self._scrape_reddit(module_id, module_name)
                forum_data.extend(reddit_data)
            except Exception as e:
                logger.error(f"Error fetching Reddit data for module {module_id}: {str(e)}")
        
        # Fetch data from ModWiggler
        if source_type in ['all', 'modwiggler']:
            try:
                modwiggler_data = self._scrape_modwiggler(module_id, module_name)
                forum_data.extend(modwiggler_data)
            except Exception as e:
                logger.error(f"Error fetching ModWiggler data for module {module_id}: {str(e)}")
        
        # If we have existing data but couldn't fetch new data, return existing data
        if not forum_data and existing_sources:
            return [source.to_dict() for source in existing_sources]
        
        return forum_data
    
    def _scrape_reddit(self, module_id, module_name):
        """
        Scrape Reddit for posts about a module.
        
        Args:
            module_id (int): ID of the module
            module_name (str): Name of the module
            
        Returns:
            list: Reddit data
        """
        logger.info(f"Scraping Reddit for module {module_name}")
        
        reddit_data = []
        
        # Try using Reddit API if available
        if self.reddit:
            try:
                # Search for module name in r/modular, r/eurorack, and r/synthesizers
                subreddits = ['modular', 'eurorack', 'synthesizers']
                
                for subreddit_name in subreddits:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    # Search for module name
                    search_query = f'"{module_name}"'
                    search_results = subreddit.search(search_query, limit=10)
                    
                    for submission in search_results:
                        # Create forum source entry
                        source = ForumSource(
                            module_id=module_id,
                            source_type='reddit',
                            source_url=f"https://www.reddit.com{submission.permalink}",
                            title=submission.title,
                            content=submission.selftext,
                            relevance_score=self._calculate_relevance_score(submission.title, submission.selftext, module_name),
                            last_updated=datetime.utcnow()
                        )
                        
                        # Save to database
                        db.session.add(source)
                        db.session.commit()
                        
                        # Add to results
                        reddit_data.append(source.to_dict())
                        
                        # Get top comments
                        submission.comments.replace_more(limit=0)
                        for comment in submission.comments[:5]:
                            if len(comment.body) > 100:  # Only include substantial comments
                                # Create forum source entry for comment
                                comment_source = ForumSource(
                                    module_id=module_id,
                                    source_type='reddit',
                                    source_url=f"https://www.reddit.com{submission.permalink}{comment.id}/",
                                    title=f"Comment on: {submission.title}",
                                    content=comment.body,
                                    relevance_score=self._calculate_relevance_score(submission.title, comment.body, module_name),
                                    last_updated=datetime.utcnow()
                                )
                                
                                # Save to database
                                db.session.add(comment_source)
                                db.session.commit()
                                
                                # Add to results
                                reddit_data.append(comment_source.to_dict())
                
                return reddit_data
            
            except Exception as e:
                logger.error(f"Error using Reddit API: {str(e)}")
                # Fall back to web scraping
        
        # Web scraping fallback
        try:
            # Use requests and BeautifulSoup to scrape Reddit
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Search Reddit
            search_url = f"https://www.reddit.com/search/?q={module_name}%20eurorack"
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find post elements
            posts = soup.find_all('div', {'class': 'Post'})
            
            for post in posts[:10]:  # Limit to 10 posts
                try:
                    # Extract title
                    title_element = post.find('h3')
                    if not title_element:
                        continue
                    
                    title = title_element.text.strip()
                    
                    # Extract URL
                    url_element = post.find('a', {'data-click-id': 'body'})
                    if not url_element:
                        continue
                    
                    url = url_element.get('href')
                    if not url.startswith('http'):
                        url = f"https://www.reddit.com{url}"
                    
                    # Visit post page to get content
                    post_response = requests.get(url, headers=headers, timeout=10)
                    post_response.raise_for_status()
                    
                    post_soup = BeautifulSoup(post_response.text, 'html.parser')
                    
                    # Extract post content
                    content_element = post_soup.find('div', {'data-test-id': 'post-content'})
                    content = ""
                    if content_element:
                        content = content_element.text.strip()
                    
                    # Calculate relevance score
                    relevance_score = self._calculate_relevance_score(title, content, module_name)
                    
                    # Only include relevant posts
                    if relevance_score > 0.5:
                        # Create forum source entry
                        source = ForumSource(
                            module_id=module_id,
                            source_type='reddit',
                            source_url=url,
                            title=title,
                            content=content,
                            relevance_score=relevance_score,
                            last_updated=datetime.utcnow()
                        )
                        
                        # Save to database
                        db.session.add(source)
                        db.session.commit()
                        
                        # Add to results
                        reddit_data.append(source.to_dict())
                
                except Exception as e:
                    logger.error(f"Error processing Reddit post: {str(e)}")
                    continue
            
            return reddit_data
        
        except Exception as e:
            logger.error(f"Error scraping Reddit: {str(e)}")
            return []
    
    def _scrape_modwiggler(self, module_id, module_name):
        """
        Scrape ModWiggler for posts about a module.
        
        Args:
            module_id (int): ID of the module
            module_name (str): Name of the module
            
        Returns:
            list: ModWiggler data
        """
        logger.info(f"Scraping ModWiggler for module {module_name}")
        
        modwiggler_data = []
        
        try:
            # Use requests and BeautifulSoup to scrape ModWiggler
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Search ModWiggler
            search_url = f"https://www.modwiggler.com/forum/search.php?keywords={module_name}&terms=all&author=&sc=1&sf=all&sr=posts&sk=t&sd=d&st=0&ch=300&t=0&submit=Search"
            response = requests.get(search_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find search results
            search_results = soup.find_all('div', {'class': 'search-result'})
            
            for result in search_results[:10]:  # Limit to 10 results
                try:
                    # Extract title and URL
                    title_element = result.find('a', {'class': 'topictitle'})
                    if not title_element:
                        continue
                    
                    title = title_element.text.strip()
                    url = title_element.get('href')
                    
                    # Make URL absolute
                    if not url.startswith('http'):
                        url = f"https://www.modwiggler.com/forum/{url}"
                    
                    # Extract sn<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>