#!/usr/bin/env python3
"""
Scheduled task to refresh knowledge base with real-time financial data
Run this script daily using cron or task scheduler
"""
import asyncio
import sys
import os
from datetime import datetime
import logging

# Add the api directory to the path
sys.path.append(os.path.dirname(__file__))

from rag_system import finance_scraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def scheduled_knowledge_refresh():
    """Scheduled task to refresh knowledge base"""
    try:
        logger.info("=" * 60)
        logger.info(f"Starting scheduled knowledge base refresh at {datetime.now()}")
        logger.info("=" * 60)
        
        # Refresh knowledge base with real-time data
        success = await finance_scraper.refresh_knowledge_base()
        
        if success:
            logger.info("✅ Scheduled knowledge base refresh completed successfully!")
        else:
            logger.error("❌ Scheduled knowledge base refresh failed")
        
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error in scheduled knowledge refresh: {e}")

if __name__ == "__main__":
    asyncio.run(scheduled_knowledge_refresh())
