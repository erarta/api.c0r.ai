#!/usr/bin/env python3
"""
Deployment Notifications for c0r.ai
Sends deployment status messages to service bot
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
import httpx
from loguru import logger

class DeploymentNotifier:
    def __init__(self, service_bot_token: str, service_chat_id: str):
        """Initialize deployment notifier"""
        self.service_bot_token = service_bot_token
        self.service_chat_id = service_chat_id
        self.base_url = f"https://api.telegram.org/bot{service_bot_token}"
    
    async def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """Send message to service bot"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": self.service_chat_id,
                        "text": message,
                        "parse_mode": parse_mode,
                        "disable_web_page_preview": True
                    }
                )
                
                if response.status_code == 200:
                    logger.success("✅ Notification sent to service bot")
                    return True
                else:
                    logger.error(f"❌ Failed to send notification: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error sending notification: {e}")
            return False
    
    def format_deployment_message(
        self, 
        status: str, 
        environment: str = "production",
        commit_hash: Optional[str] = None,
        migration_results: Optional[Dict[str, int]] = None,
        error_details: Optional[str] = None,
        duration: Optional[float] = None
    ) -> str:
        """Format deployment status message"""
        
        # Status emoji mapping
        status_emojis = {
            "started": "🚀",
            "success": "✅",
            "failed": "❌",
            "warning": "⚠️"
        }
        
        emoji = status_emojis.get(status, "📋")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        message_parts = [
            f"{emoji} **c0r.ai Deployment {status.title()}**",
            f"",
            f"🌍 **Environment:** {environment}",
            f"⏰ **Time:** {timestamp}",
        ]
        
        if commit_hash:
            message_parts.append(f"📝 **Commit:** `{commit_hash[:8]}`")
        
        if duration:
            message_parts.append(f"⏱️ **Duration:** {duration:.1f}s")
        
        # Migration results
        if migration_results:
            total = migration_results.get("total", 0)
            success = migration_results.get("success", 0)
            failed = migration_results.get("failed", 0)
            
            if total > 0:
                message_parts.extend([
                    f"",
                    f"📊 **Database Migrations:**",
                    f"• Total: {total}",
                    f"• Success: {success}",
                    f"• Failed: {failed}"
                ])
                
                if failed > 0:
                    message_parts.append(f"⚠️ **{failed} migrations failed!**")
        
        # Error details
        if error_details and status == "failed":
            message_parts.extend([
                f"",
                f"❌ **Error Details:**",
                f"```",
                error_details[:500] + ("..." if len(error_details) > 500 else ""),
                f"```"
            ])
        
        # Success details
        if status == "success":
            message_parts.extend([
                f"",
                f"🎉 **Deployment completed successfully!**",
                f"🔗 All services are running normally"
            ])
        
        return "\n".join(message_parts)
    
    async def notify_deployment_started(
        self, 
        environment: str = "production",
        commit_hash: Optional[str] = None
    ) -> bool:
        """Notify that deployment has started"""
        message = self.format_deployment_message(
            status="started",
            environment=environment,
            commit_hash=commit_hash
        )
        return await self.send_message(message)
    
    async def notify_deployment_success(
        self,
        environment: str = "production",
        commit_hash: Optional[str] = None,
        migration_results: Optional[Dict[str, int]] = None,
        duration: Optional[float] = None
    ) -> bool:
        """Notify successful deployment"""
        message = self.format_deployment_message(
            status="success",
            environment=environment,
            commit_hash=commit_hash,
            migration_results=migration_results,
            duration=duration
        )
        return await self.send_message(message)
    
    async def notify_deployment_failed(
        self,
        environment: str = "production",
        commit_hash: Optional[str] = None,
        error_details: Optional[str] = None,
        migration_results: Optional[Dict[str, int]] = None,
        duration: Optional[float] = None
    ) -> bool:
        """Notify failed deployment"""
        message = self.format_deployment_message(
            status="failed",
            environment=environment,
            commit_hash=commit_hash,
            error_details=error_details,
            migration_results=migration_results,
            duration=duration
        )
        return await self.send_message(message)

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deployment Notifications")
    parser.add_argument("--status", required=True, choices=["started", "success", "failed"])
    parser.add_argument("--environment", default="production", help="Deployment environment")
    parser.add_argument("--commit-hash", help="Git commit hash")
    parser.add_argument("--error-details", help="Error details for failed deployments")
    parser.add_argument("--migration-results", help="JSON string with migration results")
    parser.add_argument("--duration", type=float, help="Deployment duration in seconds")
    parser.add_argument("--service-bot-token", help="Service bot token (or use SERVICE_BOT_TOKEN env)")
    parser.add_argument("--service-chat-id", help="Service chat ID (or use SERVICE_CHAT_ID env)")
    
    args = parser.parse_args()
    
    # Get credentials from args or environment
    service_bot_token = args.service_bot_token or os.getenv("SERVICE_BOT_TOKEN")
    service_chat_id = args.service_chat_id or os.getenv("SERVICE_CHAT_ID")
    
    if not service_bot_token or not service_chat_id:
        logger.error("❌ Service bot token and chat ID are required")
        sys.exit(1)
    
    # Parse migration results if provided
    migration_results = None
    if args.migration_results:
        try:
            migration_results = json.loads(args.migration_results)
        except json.JSONDecodeError:
            logger.error("❌ Invalid migration results JSON")
            sys.exit(1)
    
    # Create notifier
    notifier = DeploymentNotifier(service_bot_token, service_chat_id)
    
    # Send notification based on status
    success = False
    if args.status == "started":
        success = await notifier.notify_deployment_started(
            environment=args.environment,
            commit_hash=args.commit_hash
        )
    elif args.status == "success":
        success = await notifier.notify_deployment_success(
            environment=args.environment,
            commit_hash=args.commit_hash,
            migration_results=migration_results,
            duration=args.duration
        )
    elif args.status == "failed":
        success = await notifier.notify_deployment_failed(
            environment=args.environment,
            commit_hash=args.commit_hash,
            error_details=args.error_details,
            migration_results=migration_results,
            duration=args.duration
        )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())