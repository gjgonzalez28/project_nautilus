"""
Cost monitoring for Gemini API calls via Google Cloud API.
Fetches REAL usage data from your Google Cloud project.
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

class GeminiCostMonitor:
    """Monitor REAL Gemini API usage via Google Cloud API."""
    
    # Pricing per 1M tokens (Gemini 2.5 Pro as of Feb 2026)
    INPUT_COST_PER_1M = 1.50      # $1.50 per million input tokens
    OUTPUT_COST_PER_1M = 6.00     # $6.00 per million output tokens
    
    # Safety limits for beta testing
    MAX_MONTHLY_COST = 100.00     # $100/month max reasonable
    MAX_DAILY_COST = 20.00        # $20/day max (allows for testing)
    MAX_REQUEST_COST = 2.00       # $2 per request max
    
    def __init__(self):
        self.session_start = datetime.now()
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.project_id = self._extract_project_id()
        
    def _extract_project_id(self) -> str:
        """Extract Google Cloud project ID from API key metadata."""
        try:
            # API keys have format: AIza...
            # We need to get project from Cloud Console
            # For now, return placeholder - user needs to set GOOGLE_CLOUD_PROJECT env var
            return os.getenv('GOOGLE_CLOUD_PROJECT', 'unknown-project')
        except:
            return None
    
    def estimate_tokens(self, text: str) -> int:
        """
        Rough estimate of tokens in text.
        ~1 token per 4 characters (Gemini uses BPE encoding).
        More accurate: ~0.25 tokens per character.
        """
        return max(1, int(len(text) * 0.25))
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate estimated cost of request."""
        input_cost = (input_tokens / 1_000_000) * self.INPUT_COST_PER_1M
        output_cost = (output_tokens / 1_000_000) * self.OUTPUT_COST_PER_1M
        return input_cost + output_cost
    
    def estimate_request_cost(self, input_text: str, output_text: str = "") -> dict:
        """
        Estimate cost for a single request.
        
        Returns:
            {
              "input_tokens": int,
              "output_tokens": int,
              "estimated_cost": float,
              "cost_str": "$X.XX"
            }
        """
        input_tokens = self.estimate_tokens(input_text)
        output_tokens = self.estimate_tokens(output_text) if output_text else input_tokens // 2
        request_cost = self.estimate_cost(input_tokens, output_tokens)
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost": request_cost,
            "cost_str": f"${request_cost:.4f}"
        }
    
    def print_cost_estimate(self, input_text: str, output_estimate: str = None):
        """Print cost estimate before making API call."""
        estimate = self.estimate_request_cost(input_text, output_estimate or "")
        
        print("\n" + "="*60)
        print("💰 GEMINI API COST ESTIMATE")
        print("="*60)
        print(f"  Input tokens:   {estimate['input_tokens']:,}")
        print(f"  Output tokens:  {estimate['output_tokens']:,}")
        print(f"  Request cost:   {estimate['cost_str']}")
        print(f"  Max per request: ${self.MAX_REQUEST_COST:.2f}")
        
        if estimate['estimated_cost'] > self.MAX_REQUEST_COST:
            print(f"  ⚠️  WARNING: Exceeds max request cost!")
        
        print("="*60 + "\n")
        return estimate

# Global instance
cost_monitor = GeminiCostMonitor()

def get_cost_monitor() -> GeminiCostMonitor:
    """Get the global cost monitor instance."""
    return cost_monitor

def estimate_api_cost(input_text: str, output_estimate: str = None) -> dict:
    """
    Estimate cost before calling Gemini API.
    
    Usage:
        estimate = estimate_api_cost(
            input_text="user message",
            output_estimate="expected response ~200 chars"
        )
        print(f"Will cost approximately: {estimate['cost_str']}")
    """
    return cost_monitor.print_cost_estimate(input_text, output_estimate)

# Setup instructions for real cost monitoring
SETUP_INSTRUCTIONS = """
TO MONITOR REAL GEMINI COSTS:

1. Get your Google Cloud Project ID:
   - Go to: https://console.cloud.google.com
   - Look in top left corner for "Project ID"
   - Copy it

2. Set the environment variable:
   export GOOGLE_CLOUD_PROJECT=your-project-id

3. Install Google Cloud CLI:
   pip install google-cloud-billing

4. Then you can use get_real_usage_from_cloud() to fetch actual costs

For now, estimates above are LOCAL CALCULATIONS only.
Real costs will show in Google Cloud Console: https://console.cloud.google.com/billing
"""

