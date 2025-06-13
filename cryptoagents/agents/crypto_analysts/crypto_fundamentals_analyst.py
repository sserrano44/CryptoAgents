"""
Cryptocurrency Fundamentals Analyst Agent
Analyzes crypto project fundamentals, tokenomics, and on-chain metrics
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_crypto_fundamentals_analyst(llm, toolkit):
    """
    Create a cryptocurrency fundamentals analyst agent
    """
    def crypto_fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        
        if toolkit.config["online_tools"]:
            tools = [
                toolkit.get_crypto_fundamentals_report,
                toolkit.get_crypto_market_sentiment,
                toolkit.get_crypto_market_overview,
            ]
        else:
            tools = [
                toolkit.get_crypto_fundamentals_report,
                toolkit.get_crypto_market_sentiment,
            ]
        
        system_message = """You are a cryptocurrency fundamentals analyst specializing in tokenomics, 
        project evaluation, and on-chain analysis. Your role is to assess the fundamental value and 
        long-term potential of cryptocurrency projects.
        
        Key areas to analyze:
        
        1. **Tokenomics**:
           - Total supply, circulating supply, and max supply
           - Token distribution and vesting schedules
           - Inflation/deflation mechanisms
           - Token utility and use cases
        
        2. **Project Fundamentals**:
           - Team background and credibility
           - Technology and innovation
           - Roadmap and development progress
           - Partnerships and real-world adoption
           - Community size and engagement
        
        3. **Market Position**:
           - Market capitalization and ranking
           - Trading volume and liquidity
           - Exchange listings
           - Competitive landscape
        
        4. **On-Chain Metrics** (when available):
           - Active addresses
           - Transaction volume
           - Network growth
           - Holder distribution
        
        5. **Risk Factors**:
           - Regulatory risks
           - Technical vulnerabilities
           - Centralization concerns
           - Competition from other projects
        
        Consider crypto-specific factors:
        - Smart contract risks for tokens on other blockchains
        - DeFi integration and TVL (Total Value Locked)
        - Governance mechanisms
        - Staking rewards and yield opportunities
        
        Provide a comprehensive fundamental analysis report that evaluates the project's 
        strengths, weaknesses, opportunities, and threats. Include quantitative metrics 
        and qualitative assessments. End with a summary table of key fundamental indicators."""
        
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
        
        # Execute tools directly to get fundamentals data
        ticker = state["company_of_interest"]
        
        # Get fundamentals report
        try:
            fundamentals_data = toolkit.get_crypto_fundamentals_report.invoke({
                "ticker": ticker,
                "curr_date": current_date
            })
        except Exception as e:
            fundamentals_data = f"Error retrieving fundamentals data: {str(e)}"
        
        # Get market sentiment
        try:
            sentiment_data = toolkit.get_crypto_market_sentiment.invoke({
                "ticker": ticker,
                "curr_date": current_date
            })
        except Exception as e:
            sentiment_data = f"Error retrieving sentiment data: {str(e)}"
        
        # Prepare tool results for analysis
        tool_results = f"Fundamentals Report:\n{fundamentals_data}\n\nMarket Sentiment:\n{sentiment_data}"
        
        # Create analysis prompt with tool results
        analysis_prompt = f"""Based on the following fundamentals data for {ticker}, provide a comprehensive analysis:

{tool_results}

Please analyze the tokenomics, project fundamentals, and long-term potential. Include specific recommendations."""
        
        # Create chain without tools for analysis
        chain = prompt | llm
        
        # Create messages with tool results
        messages_with_data = state["messages"] + [
            {"role": "user", "content": analysis_prompt}
        ]
        
        result = chain.invoke(messages_with_data)
        
        return {
            "messages": [result],
            "crypto_fundamentals_report": result.content,
        }
    
    return crypto_fundamentals_analyst_node
