import os
import httpx
# Import the shared FastMCP instance from the core framework
from core.server import mcp

# kagent deploy stores this key under the lowercase name "finnhub_api_key" in the
# MCP server's secret; locally it is usually exported as FINNHUB_API_KEY.
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY") or os.environ.get("finnhub_api_key", "")
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

@mcp.tool()
async def get_stock_quote(symbol: str) -> dict:
    """Get the current stock quote for a given ticker symbol.

    Args:
        symbol: The stock ticker symbol (e.g., AAPL, MSFT, GOOGL)

    Returns:
        A dictionary with current price (c), change (d), percent change (dp),
        high (h), low (l), open (o), previous close (pc), and timestamp (t).
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FINNHUB_BASE_URL}/quote",
            params={"symbol": symbol.upper(), "token": FINNHUB_API_KEY},
        )
        response.raise_for_status()
        data = response.json()
        return {
            "symbol": symbol.upper(),
            "current_price": data["c"],
            "change": data["d"],
            "percent_change": data["dp"],
            "high": data["h"],
            "low": data["l"],
            "open": data["o"],
            "previous_close": data["pc"],
        }
@mcp.tool()
async def get_company_profile(symbol: str) -> dict:
    """Get the company profile for a given ticker symbol.

    Args:
        symbol: The stock ticker symbol (e.g., AAPL, MSFT, GOOGL)

    Returns:
        A dictionary with company name, industry, market cap, and other details.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FINNHUB_BASE_URL}/stock/profile2",
            params={"symbol": symbol.upper(), "token": FINNHUB_API_KEY},
        )
        response.raise_for_status()
        return response.json()
@mcp.tool()
async def get_recommendation_trends(symbol: str) -> list:
    """Get analyst recommendation trends for a given ticker symbol.

    Args:
        symbol: The stock ticker symbol (e.g., AAPL, MSFT, GOOGL)

    Returns:
        A list of monthly recommendation data with buy, hold, sell, strongBuy, strongSell counts.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FINNHUB_BASE_URL}/stock/recommendation",
            params={"symbol": symbol.upper(), "token": FINNHUB_API_KEY},
        )
        response.raise_for_status()
        return response.json()
