"""
Market Data Routes
Provides access to real-time market data.
"""

from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, status
from loguru import logger

from app.services.market_data import market_data

router = APIRouter(prefix="/market", tags=["Market Data"])


@router.get("/mutual-funds/search")
async def search_mutual_funds(
    query: str = Query(..., min_length=3, description="Search query for mutual fund name")
):
    """
    Search for mutual funds by name.
    
    Returns:
    - List of matching mutual fund schemes with codes
    """
    try:
        results = await market_data.search_mutual_funds(query)
        return {"results": results, "count": len(results)}
    except Exception as e:
        logger.error(f"MF search error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search mutual funds"
        )


@router.get("/mutual-funds/{scheme_code}")
async def get_mutual_fund_nav(scheme_code: str):
    """
    Get current NAV for a mutual fund scheme.
    
    Args:
        scheme_code: AMFI scheme code
        
    Returns:
    - Current NAV and fund details
    """
    try:
        result = await market_data.get_mutual_fund_nav(scheme_code)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mutual fund with code {scheme_code} not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MF NAV error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch mutual fund data"
        )


@router.get("/mutual-funds/{scheme_code}/history")
async def get_mutual_fund_history(
    scheme_code: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of history")
):
    """
    Get historical NAV data for a mutual fund.
    
    Returns:
    - List of NAV data points
    """
    try:
        result = await market_data.get_mutual_fund_historical(scheme_code, days)
        return {"scheme_code": scheme_code, "history": result, "count": len(result)}
    except Exception as e:
        logger.error(f"MF history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch mutual fund history"
        )


@router.get("/interest-rates")
async def get_interest_rates():
    """
    Get current benchmark interest rates.
    
    Returns:
    - RBI repo rate, bank rates, savings scheme rates
    """
    return market_data.get_current_interest_rates()


@router.get("/tax-slabs")
async def get_tax_slabs(
    regime: str = Query("new", description="Tax regime: 'new' or 'old'")
):
    """
    Get income tax slabs for the specified regime.
    
    Returns:
    - Tax slabs with rates
    """
    if regime.lower() == "new":
        return {
            "regime": "new",
            "financial_year": "2024-25",
            "slabs": market_data.get_tax_slabs_new_regime()
        }
    elif regime.lower() == "old":
        return {
            "regime": "old",
            "financial_year": "2024-25",
            "slabs": market_data.get_tax_slabs_old_regime()
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid regime. Use 'new' or 'old'."
        )


@router.get("/deduction-limits")
async def get_deduction_limits():
    """
    Get tax deduction limits under various sections.
    
    Returns:
    - Section 80C, 80D, 24 limits
    """
    return {
        "financial_year": "2024-25",
        "limits": market_data.get_section_80c_limits()
    }
