"""
Cost optimization settings for OpenAI usage
"""

# Model configurations (from cheapest to most expensive)
MODEL_CONFIGS = {
    "ultra_budget": {
        "model": "gpt-3.5-turbo",
        "max_tokens": 100,
        "temperature": 0.5,
        "description": "Ultra budget mode - minimal costs, basic improvements",
        "estimated_cost_per_improvement": 0.005
    },
    "budget": {
        "model": "gpt-3.5-turbo", 
        "max_tokens": 150,
        "temperature": 0.6,
        "description": "Budget mode - low costs, good improvements",
        "estimated_cost_per_improvement": 0.008
    },
    "balanced": {
        "model": "gpt-3.5-turbo",
        "max_tokens": 200,
        "temperature": 0.7,
        "description": "Balanced mode - moderate costs, better quality",
        "estimated_cost_per_improvement": 0.012
    },
    "premium": {
        "model": "gpt-4o-mini",
        "max_tokens": 250,
        "temperature": 0.7,
        "description": "Premium mode - higher costs, best quality",
        "estimated_cost_per_improvement": 0.025
    }
}

# Default cost mode
DEFAULT_COST_MODE = "budget"

# Maximum cost per session (USD)
MAX_SESSION_COST = 0.50  # 50 cents max per session

# Cost warnings
COST_WARNING_THRESHOLD = 0.10  # Warn when session cost exceeds 10 cents
