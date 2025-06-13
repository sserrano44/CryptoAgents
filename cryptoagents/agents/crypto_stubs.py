"""
Simplified stub agents for crypto trading
These are simplified versions that don't require the memory system
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_research_manager(llm, toolkit):
    """Create a simplified research manager"""
    def research_manager_node(state):
        # Collect all analyst reports
        market_report = state.get("crypto_market_report", "")
        fundamentals_report = state.get("crypto_fundamentals_report", "")
        news_report = state.get("crypto_news_report", "")
        social_report = state.get("crypto_social_report", "")
        
        prompt = f"""As the research manager, synthesize the following analyst reports and provide a comprehensive 
        investment research conclusion for cryptocurrency trading.
        
        Market Analysis:
        {market_report}
        
        Fundamentals Analysis:
        {fundamentals_report}
        
        News Analysis:
        {news_report}
        
        Social Sentiment:
        {social_report}
        
        Provide a balanced research conclusion that considers all perspectives."""
        
        response = llm.invoke(prompt)
        
        return {
            "messages": [response],
            "research_conclusion": response.content
        }
    
    return research_manager_node


def create_bull_researcher(llm, toolkit):
    """Create a simplified bull researcher"""
    def bull_researcher_node(state):
        research_conclusion = state.get("research_conclusion", "")
        
        prompt = f"""As a bullish cryptocurrency researcher, analyze the research conclusion and make a strong 
        case for BUYING this cryptocurrency. Focus on positive factors, growth potential, and opportunities.
        
        Research Conclusion:
        {research_conclusion}
        
        Make a compelling bull case for this cryptocurrency."""
        
        response = llm.invoke(prompt)
        
        return {
            "messages": [response],
            "bull_case": response.content
        }
    
    return bull_researcher_node


def create_bear_researcher(llm, toolkit):
    """Create a simplified bear researcher"""
    def bear_researcher_node(state):
        research_conclusion = state.get("research_conclusion", "")
        bull_case = state.get("bull_case", "")
        
        prompt = f"""As a bearish cryptocurrency researcher, analyze the research and counter the bull case.
        Make a strong case for SELLING or avoiding this cryptocurrency. Focus on risks, overvaluation, and concerns.
        
        Research Conclusion:
        {research_conclusion}
        
        Bull Case to Counter:
        {bull_case}
        
        Make a compelling bear case against this cryptocurrency."""
        
        response = llm.invoke(prompt)
        
        return {
            "messages": [response],
            "bear_case": response.content
        }
    
    return bear_researcher_node


def create_trader(llm, toolkit):
    """Create a simplified trader"""
    def trader_node(state):
        bull_case = state.get("bull_case", "")
        bear_case = state.get("bear_case", "")
        
        prompt = f"""As a cryptocurrency trader, analyze both the bull and bear cases and make a trading decision.
        Consider the arguments from both sides and decide: BUY, SELL, or HOLD.
        
        Bull Case:
        {bull_case}
        
        Bear Case:
        {bear_case}
        
        Make a clear trading decision with rationale. Your decision must be one of: BUY, SELL, or HOLD."""
        
        response = llm.invoke(prompt)
        
        return {
            "messages": [response],
            "trade_decision": response.content
        }
    
    return trader_node


def create_risk_manager(llm, toolkit):
    """Create a simplified risk manager"""
    def risk_manager_node(state):
        trade_decision = state.get("trade_decision", "")
        crypto = state.get("crypto_of_interest", "")
        
        prompt = f"""As a cryptocurrency risk manager, evaluate the trading decision and provide risk assessment.
        Consider the high volatility of crypto markets, liquidity risks, and position sizing.
        
        Cryptocurrency: {crypto}
        Trading Decision:
        {trade_decision}
        
        Provide risk assessment and final recommendation. Include:
        1. Risk level (High/Medium/Low)
        2. Suggested position size (as % of portfolio)
        3. Stop loss recommendations
        4. Final decision: APPROVE or REJECT the trade
        
        End with a clear FINAL DECISION: BUY/SELL/HOLD"""
        
        response = llm.invoke(prompt)
        
        # Extract final decision from response
        content = response.content
        final_decision = "HOLD"  # Default
        
        if "FINAL DECISION: BUY" in content.upper():
            final_decision = "BUY"
        elif "FINAL DECISION: SELL" in content.upper():
            final_decision = "SELL"
        elif "FINAL DECISION: HOLD" in content.upper():
            final_decision = "HOLD"
        
        return {
            "messages": [response],
            "risk_assessment": response.content,
            "final_decision": final_decision
        }
    
    return risk_manager_node
