"""
Cryptocurrency Market Analyst Agent
Analyzes crypto market data, technical indicators, and price movements
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_crypto_market_analyst(llm, toolkit):
    """
    Create a cryptocurrency market analyst agent
    """
    def crypto_market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        
        if toolkit.config["online_tools"]:
            tools = [
                toolkit.get_crypto_price_data_window,
                toolkit.get_crypto_technical_indicators,
                toolkit.get_crypto_correlation_analysis,
            ]
        else:
            tools = [
                toolkit.get_crypto_price_data_window,
                toolkit.get_crypto_technical_indicators,
            ]
        
        system_message = """You are a cryptocurrency market analyst specializing in technical analysis and market trends. 
        Your role is to analyze crypto market data and provide insights for trading decisions.
        
        Key responsibilities:
        1. Analyze price movements and volume patterns in 24/7 crypto markets
        2. Calculate and interpret technical indicators adapted for high-volatility crypto assets
        3. Identify support/resistance levels and trend patterns
        4. Consider crypto-specific factors like Bitcoin correlation and market dominance
        5. Account for exchange-specific price differences and liquidity
        
        Technical Indicators to analyze (select up to 8 most relevant):
        
        Moving Averages:
        - close_50_sma: 50 SMA for medium-term crypto trends
        - close_200_sma: 200 SMA for long-term crypto trends (note: crypto markets are younger)
        - close_10_ema: 10 EMA for short-term momentum in volatile crypto markets
        
        MACD Related:
        - macd: MACD for momentum shifts in crypto
        - macds: MACD Signal line crossovers
        - macdh: MACD Histogram for momentum strength
        
        Momentum Indicators:
        - rsi: RSI (consider crypto often stays overbought/oversold longer)
        - mfi: Money Flow Index combining price and volume
        
        Volatility Indicators:
        - boll: Bollinger Bands middle line
        - boll_ub: Upper band for resistance/breakout levels
        - boll_lb: Lower band for support/oversold conditions
        - atr: ATR for crypto volatility measurement
        
        Volume-Based:
        - vwma: Volume-weighted moving average
        
        Remember:
        - Crypto markets trade 24/7 without traditional market hours
        - Higher volatility requires adjusted indicator interpretations
        - Consider correlation with Bitcoin and Ethereum
        - Account for crypto market cycles and halving events
        
        First retrieve price data, then calculate relevant indicators. Provide a detailed analysis
        of trends, patterns, and potential trading opportunities. Include a summary table at the end."""
        
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
                    " For your reference, the current date is {current_date}. The cryptocurrency we want to analyze is {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        
        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)
        
        # Execute tools directly to get market data
        ticker = state["company_of_interest"]
        
        # Get price data first
        try:
            price_data = toolkit.get_crypto_price_data_window.invoke({
                "symbol": ticker,
                "curr_date": current_date,
                "look_back_days": 30
            })
        except Exception as e:
            price_data = f"Error retrieving price data: {str(e)}"
        
        # Get technical indicators
        try:
            tech_indicators = toolkit.get_crypto_technical_indicators.invoke({
                "symbol": ticker,
                "curr_date": current_date,
                "look_back_days": 30
            })
        except Exception as e:
            tech_indicators = f"Error retrieving technical indicators: {str(e)}"
        
        # Prepare tool results for analysis
        tool_results = f"Price Data:\n{price_data}\n\nTechnical Indicators:\n{tech_indicators}"
        
        # Create analysis prompt with tool results
        analysis_prompt = f"""Based on the following market data for {ticker}, provide a comprehensive technical analysis:

{tool_results}

Please analyze trends, patterns, and potential trading opportunities. Include a summary table at the end."""
        
        # Create chain without tools for analysis
        chain = prompt | llm
        
        # Create messages with tool results
        messages_with_data = state["messages"] + [
            {"role": "user", "content": analysis_prompt}
        ]
        
        result = chain.invoke(messages_with_data)
        
        return {
            "messages": [result],
            "crypto_market_report": result.content,
        }
    
    return crypto_market_analyst_node
