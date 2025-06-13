"""
Cryptocurrency News Analyst Agent
Analyzes crypto news, regulatory developments, and market events
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_crypto_news_analyst(llm, toolkit):
    """
    Create a cryptocurrency news analyst agent
    """
    def crypto_news_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        
        if toolkit.config["online_tools"]:
            tools = [
                toolkit.get_crypto_news_openai,
                toolkit.get_crypto_news,
                toolkit.get_crypto_market_overview,
            ]
        else:
            tools = [
                toolkit.get_crypto_news,
                toolkit.get_google_news,
                toolkit.get_crypto_market_overview,
            ]
        
        system_message = """You are a cryptocurrency news analyst specializing in market events, 
        regulatory developments, and crypto ecosystem news. Your role is to analyze recent news 
        and events that could impact cryptocurrency prices and market sentiment.
        
        Key areas to monitor and analyze:
        
        1. **Project-Specific News**:
           - Technical updates and upgrades
           - Partnership announcements
           - Exchange listings/delistings
           - Security incidents or hacks
           - Team changes or developments
        
        2. **Regulatory Developments**:
           - Government regulations and policies
           - SEC, CFTC, and other regulatory actions
           - Tax law changes
           - Central bank digital currency (CBDC) developments
           - Country-specific crypto adoption or bans
        
        3. **Market Events**:
           - Major whale movements
           - Exchange outflows/inflows
           - Liquidation events
           - Market manipulation concerns
           - Stablecoin depegging risks
        
        4. **Macro Crypto Trends**:
           - Bitcoin and Ethereum movements affecting altcoins
           - DeFi trends and TVL changes
           - NFT market developments
           - Layer 2 adoption
           - Cross-chain bridge incidents
        
        5. **Global Economic Factors**:
           - Traditional market correlations
           - Inflation and monetary policy
           - Geopolitical events
           - Energy prices (for PoW coins)
        
        Crypto-specific considerations:
        - News spreads faster in crypto due to 24/7 markets
        - Social media and influencer impact is significant
        - FUD (Fear, Uncertainty, Doubt) and FOMO (Fear of Missing Out) cycles
        - Regulatory news has outsized impact on prices
        
        Analyze the news with a focus on:
        - Immediate price impact potential
        - Long-term implications for the project
        - Market sentiment shifts
        - Regulatory risk changes
        
        Provide a comprehensive news analysis report highlighting the most important 
        developments and their potential market impact. Include a summary table of 
        key news items ranked by importance."""
        
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
                    " For your reference, the current date is {current_date}. We are analyzing news for {ticker} cryptocurrency",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        
        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)
        
        # Execute tools directly to get news data
        ticker = state["company_of_interest"]
        
        # Get crypto news
        try:
            news_data = toolkit.get_crypto_news.invoke({
                "ticker": ticker,
                "curr_date": current_date,
                "look_back_days": 7
            })
        except Exception as e:
            news_data = f"Error retrieving news data: {str(e)}"
        
        # Prepare tool results for analysis
        tool_results = f"Crypto News:\n{news_data}"
        
        # Create analysis prompt with tool results
        analysis_prompt = f"""Based on the following news data for {ticker}, provide a comprehensive analysis:

{tool_results}

Please analyze the sentiment, key developments, and potential market impact. Focus on actionable insights."""
        
        # Create chain without tools for analysis
        chain = prompt | llm
        
        # Create messages with tool results
        messages_with_data = state["messages"] + [
            {"role": "user", "content": analysis_prompt}
        ]
        
        result = chain.invoke(messages_with_data)
        
        return {
            "messages": [result],
            "crypto_news_report": result.content,
        }
    
    return crypto_news_analyst_node
