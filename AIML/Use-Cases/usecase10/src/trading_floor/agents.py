from __future__ import annotations
#after annotations we have tradeidea so python stores 
#it as a string internally "TradeIdea" useful for:
# circular imports, faster imports, modern type hinting
from .models import TradeIdea
from .tools import infer_quantity, normalize_symbol, ticker_lookup, web_search_market_brief

#this receives memories with research 
def research_agent(message: str, memories: list[str], propose_trade: bool = True) -> tuple[TradeIdea, str]:
    symbol = normalize_symbol(message)#if user ask buy Apple stock output is "AAPL"
    quote = ticker_lookup(symbol)   
    #ex: if i/p : {"symbol":"AAPL","price":210.50 } the o/p: quote["price"]=210.50
    brief = web_search_market_brief(symbol) #"Apple beat earnings expectations and AI demand is strong."  so this becomes the rationale
    quantity = infer_quantity(message, quote["price"]) if propose_trade else 0 
    # i/p: Buy $1000 of Apple price is $200/share so the o/p: 1000/200=5, quantity=5
    #if the propose_trade=False, quantity=0

# create the TradeIdea
    idea = TradeIdea(
        symbol=symbol,  
        side="buy",
        quantity=quantity,
        price=quote["price"],
        rationale=brief,
    )
# this gets handed tot he risk agent
#     TradeIdea(
#     symbol="AAPL",
#     side="buy",
#     quantity=5,
#     price=210.50,
#     rationale="Strong earnings..."
# )

# here it checks both symbol + price and quantity if not else block execute 
    if propose_trade:
        summary = f"Research found {symbol} at ${quote['price']:.2f}. Proposed {quantity} share(s)."
    else:
        summary = f"Research found {symbol} at ${quote['price']:.2f}. No trade was proposed."

    return idea, summary
  

def compile_langgraph_swarm(llm):
    """Optional production graph using langgraph-swarm when dependencies are installed."""
    # creates ReAct agents= reason, act, observe, repeat, so the 
    # agent can think, use tools, respond
    from langgraph.prebuilt import create_react_agent  # type: ignore
    # create_handoff_tool is create a tool that transfers control to an already existing agent.
    # create_swarm is registers all the agents 

    # ex: research agent calls handoff tool -> to_risk
    # swarm transfoers control
    # risk agent starts executing
    from langgraph_swarm import create_handoff_tool, create_swarm  

    to_research = create_handoff_tool(agent_name="research_agent")
    to_risk = create_handoff_tool(agent_name="risk_agent")
    to_execution = create_handoff_tool(agent_name="execution_agent")

    research = create_react_agent(
        llm,
        tools=[to_risk],
        name="research_agent",
        prompt="Research tickers and produce paper-trade ideas. Handoff to risk_agent before execution.",
    )
    risk = create_react_agent(
        llm,
        tools=[to_research, to_execution],
        name="risk_agent",
        prompt="Validate trades against limits. Handoff to execution_agent only after approval.",
    )
    execution = create_react_agent(
        llm,
        tools=[to_risk],
        name="execution_agent",
        prompt="Execute only mock broker trades that have a risk-agent approval.",
    )
    return create_swarm(
        agents=[research, risk, execution],
        default_active_agent="research_agent",
    ).compile()
