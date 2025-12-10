"""Slack integration."""

from typing import Dict, Any, Tuple, List
import os


def test_slack_connection(config: Dict[str, Any], credentials: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Test Slack connection.
    
    Returns:
        (success, message)
    """
    try:
        bot_token = credentials.get('bot_token')
        
        if not bot_token:
            return False, "Missing bot_token in credentials"
        
        # Try importing slack_sdk
        try:
            from slack_sdk import WebClient
            from slack_sdk.errors import SlackApiError
        except ImportError:
            return False, "slack-sdk not installed. Run: pip install slack-sdk"
        
        # Test connection
        client = WebClient(token=bot_token)
        response = client.auth_test()
        
        if response.get('ok'):
            team = response.get('team', 'Unknown')
            user = response.get('user', 'Unknown')
            return True, f"Connected to {team} as {user}"
        else:
            return False, f"Slack API error: {response.get('error', 'Unknown error')}"
    
    except Exception as e:
        return False, f"Connection failed: {str(e)}"


def get_slack_mentions(config: Dict[str, Any], credentials: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get recent Slack mentions for the authenticated user.
    
    Returns:
        List of mention dictionaries
    """
    try:
        from slack_sdk import WebClient
        
        bot_token = credentials.get('bot_token')
        client = WebClient(token=bot_token)
        
        # Get conversations where bot is mentioned
        # Note: This is simplified - in production you'd use Socket Mode or Events API
        response = client.conversations_list()
        
        mentions = []
        # This is a placeholder - real implementation would track actual mentions
        # via Socket Mode or Events API webhook
        
        return mentions
    
    except Exception as e:
        print(f"Error getting Slack mentions: {e}")
        return []


def send_slack_notification(
    config: Dict[str, Any],
    credentials: Dict[str, Any],
    channel: str,
    text: str
) -> Tuple[bool, str]:
    """
    Send a notification to Slack.
    
    Returns:
        (success, message)
    """
    try:
        from slack_sdk import WebClient
        
        bot_token = credentials.get('bot_token')
        client = WebClient(token=bot_token)
        
        response = client.chat_postMessage(
            channel=channel,
            text=text
        )
        
        if response.get('ok'):
            return True, "Message sent successfully"
        else:
            return False, f"Failed to send: {response.get('error')}"
    
    except Exception as e:
        return False, f"Error sending message: {str(e)}"

