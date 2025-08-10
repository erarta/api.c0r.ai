"""
Centralized routes configuration for all services
"""

class Routes:
    # === ML Service routes ===
    ML_ANALYZE = "/api/v1/analyze"
    ML_GENERATE_RECIPE = "/api/v1/generate-recipe"
    ML_HEALTH = "/"
    ML_LABEL_ANALYZE = "/api/v1/label/analyze"
    ML_LABEL_PERPLEXITY = "/api/v1/label/perplexity"
    
    # === Payment Service routes ===
    PAY_INVOICE = "/invoice"
    PAY_WEBHOOK_YOOKASSA = "/webhook/yookassa"
    PAY_WEBHOOK_STRIPE = "/webhook/stripe"
    PAY_HEALTH = "/"
    
    # === API Service routes ===
    API_REGISTER = "/register"
    API_ANALYZE = "/analyze"
    API_CREDITS_BUY = "/credits/buy"
    API_CREDITS_ADD = "/credits/add" 