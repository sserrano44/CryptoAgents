"""
Standalone Cryptocurrency Trading Graph
This version avoids relative imports to prevent issues with parent module imports
"""
import os
import sys
from typing import Dict, Any, List, TypedDict, Annotated
from datetime import datetime
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import crypto modules using absolute imports
from cryptoagents.agents.crypto_analysts import (
    create_crypto_market_analyst,
    create_crypto_fundamentals_analyst,
    create_crypto_news_analyst,
    create_crypto_social_analyst
)
from cryptoagents.agents.crypto_stubs import (
    create_research_manager,
    create_risk_manager,
    create_bull_researcher,
    create_bear_researcher,
    create_trader
)
from cryptoagents.dataflows.crypto_toolkit import create_crypto_toolkit
from cryptoagents.config import get_crypto_config, CRYPTO_PROMPTS, validate_crypto_symbol


class CryptoTradingState(TypedDict):
    """State definition for crypto trading graph"""
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]
    crypto_of_interest: str
    trade_date: str
    # Analyst reports
    crypto_market_report: str
    crypto_fundamentals_report: str
    crypto_news_report: str
    crypto_social_report: str
    # Research reports
    bull_case: str
    bear_case: str
    research_conclusion: str
    # Trading decision
    trade_decision: str
    risk_assessment: str
    final_decision: str
    # Metadata
    iteration_count: int
    max_iterations: int


class CryptoTradingAgentsGraph:
    """
    Main cryptocurrency trading agents graph
    """
    
    def __init__(self, debug: bool = False, config: Dict[str, Any] = None):
        """
        Initialize the crypto trading graph
        
        Args:
            debug: Enable debug mode
            config: Configuration dictionary
        """
        self.debug = debug
        self.config = config or get_crypto_config()
        self.toolkit = create_crypto_toolkit(self.config)
        
        # Initialize LLMs (without temperature for models that don't support it)
        self.deep_llm = ChatOpenAI(
            model=self.config["deep_think_llm"]
        )
        self.quick_llm = ChatOpenAI(
            model=self.config["quick_think_llm"]
        )
        
        # Build the graph
        self._build_graph()
    
    def _build_graph(self):
        """Build the crypto trading graph"""
        # Create the graph
        workflow = StateGraph(CryptoTradingState)
        
        # Create agent nodes
        market_analyst = create_crypto_market_analyst(self.quick_llm, self.toolkit)
        fundamentals_analyst = create_crypto_fundamentals_analyst(self.quick_llm, self.toolkit)
        news_analyst = create_crypto_news_analyst(self.quick_llm, self.toolkit)
        social_analyst = create_crypto_social_analyst(self.quick_llm, self.toolkit)
        
        # Research and trading agents (reuse from original with crypto context)
        research_manager = create_research_manager(self.deep_llm, self.toolkit)
        bull_researcher = create_bull_researcher(self.quick_llm, self.toolkit)
        bear_researcher = create_bear_researcher(self.quick_llm, self.toolkit)
        trader = create_trader(self.deep_llm, self.toolkit)
        risk_manager = create_risk_manager(self.deep_llm, self.toolkit)
        
        # Add nodes
        workflow.add_node("market_analyst", market_analyst)
        workflow.add_node("fundamentals_analyst", fundamentals_analyst)
        workflow.add_node("news_analyst", news_analyst)
        workflow.add_node("social_analyst", social_analyst)
        workflow.add_node("research_manager", research_manager)
        workflow.add_node("bull_researcher", bull_researcher)
        workflow.add_node("bear_researcher", bear_researcher)
        workflow.add_node("trader", trader)
        workflow.add_node("risk_manager", risk_manager)
        
        # Define the flow
        workflow.set_entry_point("market_analyst")
        
        # Analyst phase (parallel analysis)
        workflow.add_edge("market_analyst", "fundamentals_analyst")
        workflow.add_edge("fundamentals_analyst", "news_analyst")
        workflow.add_edge("news_analyst", "social_analyst")
        workflow.add_edge("social_analyst", "research_manager")
        
        # Research phase
        workflow.add_edge("research_manager", "bull_researcher")
        workflow.add_edge("bull_researcher", "bear_researcher")
        workflow.add_edge("bear_researcher", "trader")
        
        # Trading decision phase
        workflow.add_edge("trader", "risk_manager")
        workflow.add_edge("risk_manager", END)
        
        # Compile the graph
        self.graph = workflow.compile()
    
    def _create_initial_state(self, crypto_symbol: str, trade_date: str) -> CryptoTradingState:
        """
        Create initial state for the trading graph
        
        Args:
            crypto_symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
            trade_date: Trading date in YYYY-MM-DD format
        
        Returns:
            Initial state dictionary
        """
        # Add crypto context to the initial message
        crypto_context = CRYPTO_PROMPTS["market_context"] + "\n\n" + CRYPTO_PROMPTS["risk_warning"]
        
        initial_message = HumanMessage(
            content=f"""Analyze {crypto_symbol} cryptocurrency for trading on {trade_date}.
            
{crypto_context}

Please provide comprehensive analysis considering all crypto-specific factors."""
        )
        
        return {
            "messages": [initial_message],
            "crypto_of_interest": crypto_symbol.upper(),
            "trade_date": trade_date,
            "crypto_market_report": "",
            "crypto_fundamentals_report": "",
            "crypto_news_report": "",
            "crypto_social_report": "",
            "bull_case": "",
            "bear_case": "",
            "research_conclusion": "",
            "trade_decision": "",
            "risk_assessment": "",
            "final_decision": "",
            "iteration_count": 0,
            "max_iterations": self.config.get("max_recur_limit", 100)
        }
    
    def analyze_crypto(self, crypto_symbol: str, trade_date: str = None) -> Dict[str, Any]:
        """
        Analyze a cryptocurrency for trading
        
        Args:
            crypto_symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
            trade_date: Trading date (defaults to today)
        
        Returns:
            Analysis results and trading decision
        """
        # Validate crypto symbol
        if not validate_crypto_symbol(crypto_symbol):
            print(f"Warning: {crypto_symbol} is not in the supported crypto list. Proceeding anyway...")
        
        # Default to today if no date provided
        if trade_date is None:
            trade_date = datetime.now().strftime("%Y-%m-%d")
        
        # Create initial state
        initial_state = self._create_initial_state(crypto_symbol, trade_date)
        
        if self.debug:
            print(f"\n{'='*50}")
            print(f"Starting Crypto Analysis for {crypto_symbol} on {trade_date}")
            print(f"{'='*50}\n")
        
        # Run the graph
        try:
            final_state = self.graph.invoke(initial_state)
            
            # Extract results
            results = {
                "crypto": crypto_symbol,
                "date": trade_date,
                "market_analysis": final_state.get("crypto_market_report", ""),
                "fundamentals": final_state.get("crypto_fundamentals_report", ""),
                "news": final_state.get("crypto_news_report", ""),
                "social_sentiment": final_state.get("crypto_social_report", ""),
                "bull_case": final_state.get("bull_case", ""),
                "bear_case": final_state.get("bear_case", ""),
                "research_conclusion": final_state.get("research_conclusion", ""),
                "trade_decision": final_state.get("trade_decision", ""),
                "risk_assessment": final_state.get("risk_assessment", ""),
                "final_decision": final_state.get("final_decision", "")
            }
            
            if self.debug:
                self._print_results(results)
            
            return results
            
        except Exception as e:
            print(f"Error during crypto analysis: {str(e)}")
            raise
    
    def _print_results(self, results: Dict[str, Any]):
        """Print analysis results in a formatted way"""
        print(f"\n{'='*50}")
        print(f"CRYPTO TRADING ANALYSIS RESULTS")
        print(f"{'='*50}")
        print(f"Cryptocurrency: {results['crypto']}")
        print(f"Date: {results['date']}")
        print(f"\nFinal Decision: {results['final_decision']}")
        print(f"\nRisk Assessment Summary:")
        print(results['risk_assessment'][:500] + "..." if len(results['risk_assessment']) > 500 else results['risk_assessment'])
        print(f"\n{'='*50}\n")
    
    def batch_analyze(self, crypto_list: List[str], trade_date: str = None) -> List[Dict[str, Any]]:
        """
        Analyze multiple cryptocurrencies
        
        Args:
            crypto_list: List of cryptocurrency symbols
            trade_date: Trading date
        
        Returns:
            List of analysis results
        """
        results = []
        
        for crypto in crypto_list:
            try:
                result = self.analyze_crypto(crypto, trade_date)
                results.append(result)
            except Exception as e:
                print(f"Error analyzing {crypto}: {str(e)}")
                results.append({
                    "crypto": crypto,
                    "date": trade_date,
                    "error": str(e),
                    "final_decision": "ERROR"
                })
        
        return results


# Convenience function for backward compatibility
def create_crypto_trading_graph(debug: bool = False, config: Dict[str, Any] = None) -> CryptoTradingAgentsGraph:
    """
    Create a crypto trading graph instance
    
    Args:
        debug: Enable debug mode
        config: Configuration dictionary
    
    Returns:
        CryptoTradingAgentsGraph instance
    """
    return CryptoTradingAgentsGraph(debug=debug, config=config)
