"""
Cryptocurrency Social Media Analyst Agent
Analyzes crypto social sentiment, community activity, and influencer opinions
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_crypto_social_analyst(llm, toolkit):
    """
    Create a cryptocurrency social media analyst agent
    """
    def crypto_social_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        
        if toolkit.config["online_tools"]:
            tools = [
                toolkit.get_crypto_social_sentiment_openai,
                toolkit.get_reddit_crypto_sentiment,
            ]
        else:
            tools = [
                toolkit.get_reddit_crypto_sentiment,
                toolkit.get_google_news,  # Fallback for social signals
            ]
        
        system_message = """You are a cryptocurrency social media analyst specializing in sentiment analysis, 
        community engagement, and social signals. Your role is to gauge market sentiment and identify 
        social trends that could impact cryptocurrency prices.
        
        Key platforms and metrics to analyze:
        
        1. **Crypto Twitter (X)**:
           - Influencer sentiment and reach
           - Trending hashtags and topics
           - Community mood (bullish/bearish)
           - FUD or FOMO indicators
           - Notable whale or insider tweets
        
        2. **Reddit Communities**:
           - r/cryptocurrency sentiment
           - Project-specific subreddit activity
           - Post volume and engagement rates
           - Quality of discussions
           - Meme momentum (for meme coins)
        
        3. **Discord/Telegram**:
           - Community size and growth
           - Active user metrics
           - Developer engagement
           - Announcement impacts
           - Community concerns or excitement
        
        4. **Social Metrics**:
           - Social volume trends
           - Sentiment score changes
           - Influencer endorsements/criticisms
           - Viral content analysis
           - Community growth rate
        
        5. **On-Chain Social Signals**:
           - Holder count changes
           - Whale accumulation/distribution
           - Smart money movements
           - Exchange flows correlation with sentiment
        
        Crypto-specific social considerations:
        - Crypto communities are highly reactive to social media
        - Influencer opinions can cause significant price movements
        - Meme culture plays a major role in some tokens
        - Coordinated social campaigns (pump/dump risks)
        - Echo chamber effects in crypto communities
        
        Red flags to identify:
        - Sudden sentiment shifts
        - Coordinated shill campaigns
        - Influencer pump schemes
        - Community discord or team issues
        - Negative viral events
        
        Positive signals to highlight:
        - Organic community growth
        - Increasing developer activity
        - Positive influencer coverage
        - Strong community support during dips
        - Viral adoption stories
        
        Provide a comprehensive social sentiment analysis that captures the current 
        community mood, key influencer opinions, and potential social catalysts. 
        Include a sentiment score and summary table of key social indicators."""
        
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    " For your reference, the current date is {current_date}. We are analyzing social sentiment for {ticker} cryptocurrency",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        
        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)
        
        # Execute tools directly to get social data
        ticker = state["company_of_interest"]
        
        # Get social sentiment data
        try:
            social_data = toolkit.get_reddit_crypto_sentiment.invoke({
                "ticker": ticker,
                "curr_date": current_date,
                "look_back_days": 7,
                "max_limit_per_day": 10
            })
        except Exception as e:
            social_data = f"Error retrieving social sentiment data: {str(e)}"
        
        # Prepare tool results for analysis
        tool_results = f"Social Sentiment Data:\n{social_data}"
        
        # Create analysis prompt with tool results
        analysis_prompt = f"""Based on the following social sentiment data for {ticker}, provide a comprehensive analysis:

{tool_results}

Please analyze the community sentiment, trending topics, and social momentum. Identify potential catalysts or concerns."""
        
        # Create chain without tools for analysis
        chain = prompt | llm
        
        # Create messages with tool results
        messages_with_data = state["messages"] + [
            {"role": "user", "content": analysis_prompt}
        ]
        
        result = chain.invoke(messages_with_data)
        
        return {
            "messages": [result],
            "crypto_social_report": result.content,
        }
    
    return crypto_social_analyst_node
