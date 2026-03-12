"""
fallback_questions.py
---------------------
Pre-generated question bank for when API quota is exhausted.
Serves as offline fallback to keep the app functional.
"""

FALLBACK_QUESTIONS = {
    "MLS Listings & Terminology_beginner": {
        "question": "What does MLS stand for?",
        "hint": "It's an acronym for a real estate database system used by agents.",
        "correct_answer": "Multiple Listing Service - a shared database of property listings used by real estate agents to buy, sell, and exchange property information.",
        "key_points": ["MLS acronym", "Shared database", "Agent network"],
        "topic": "MLS Listings & Terminology",
        "difficulty": "beginner"
    },
    "MLS Listings & Terminology_intermediate": {
        "question": "How does MLS data availability affect property marketability?",
        "hint": "Think about how quickly buyers find properties and what happens to unsold inventory.",
        "correct_answer": "Wider MLS distribution increases property exposure to more potential buyers, reducing days on market and attracting competitive offers. Properties not listed on MLS have significantly limited buyer access.",
        "key_points": ["Market exposure", "Buyer access", "Days on market"],
        "topic": "MLS Listings & Terminology",
        "difficulty": "intermediate"
    },
    "MLS Listings & Terminology_advanced": {
        "question": "Explain how MLS cooperation agreements and buyer commissions influence bidding behavior in competitive markets.",
        "hint": "Consider what incentives agents have and how commission splits affect strategy.",
        "correct_answer": "Standard MLS cooperation offers 2.5-3% buyer agent commission, incentivizing representation. In competitive markets, higher commission offers attract more buyer agents to showings, increasing activity. Sellers reducing commission may face fewer showings. Dual agency situations complicate incentives.",
        "key_points": ["Commission incentives", "Market activity", "Agent behavior"],
        "topic": "MLS Listings & Terminology",
        "difficulty": "advanced"
    },
    "Property Valuation_beginner": {
        "question": "Name three physical factors that affect property value.",
        "hint": "Think about what a buyer sees when they visit a property.",
        "correct_answer": "Lot size, building condition, square footage, age of property, roof condition, plumbing/electrical systems, and aesthetic appeal.",
        "key_points": ["Physical characteristics", "Building components", "Property condition"],
        "topic": "Property Valuation",
        "difficulty": "beginner"
    },
    "Property Valuation_intermediate": {
        "question": "Describe how a Comparative Market Analysis (CMA) differs from a professional appraisal.",
        "hint": "Consider who performs each, their purpose, and their legal validity.",
        "correct_answer": "A CMA is prepared by agents using recent comparable sales and is an informal estimate for marketing. An appraisal is a professional valuation by a licensed appraiser using standardized methodology and is legally recognized for lending.",
        "key_points": ["Agent vs appraiser", "Legal recognition", "Methodology"],
        "topic": "Property Valuation",
        "difficulty": "intermediate"
    },
    "Property Valuation_advanced": {
        "question": "If comparable properties sold for $450K, $425K, and $475K, a subject property is 1200 sq ft vs avg comparables at 1100 sq ft, and homes in this area price at $350/sq ft. What's your value estimate and reasoning?",
        "hint": "Use both comparable sales and price per square foot methods, then reconcile.",
        "correct_answer": "Comparable average: $450K. By price per sq ft: 1200 sq ft × $350 = $420K. Subject property is slightly larger (100 sq ft), suggesting premium. Reconciled estimate: $435-445K, accounting for both methods and the size premium.",
        "key_points": ["Comparable sales method", "Price per sq ft", "Reconciliation"],
        "topic": "Property Valuation",
        "difficulty": "advanced"
    },
    "Listing Agreements_beginner": {
        "question": "What is a listing agreement?",
        "hint": "It's a contract between two parties in real estate.",
        "correct_answer": "A contract between a property owner and a real estate agent that authorizes the agent to market and sell the property, typically specifying commission rate, listing duration, and agent responsibilities.",
        "key_points": ["Contract", "Agent authorization", "Terms"],
        "topic": "Listing Agreements",
        "difficulty": "beginner"
    },
    "Listing Agreements_intermediate": {
        "question": "Compare exclusive right to sell vs exclusive agency listing agreements.",
        "hint": "The difference is what happens if the owner sells the property themselves.",
        "correct_answer": "Exclusive right to sell: agent earns commission regardless of who sells the property. Exclusive agency: agent earns commission only for sales made by other agents; seller can sell personally without paying commission.",
        "key_points": ["Agent protection", "Owner rights", "Commission structure"],
        "topic": "Listing Agreements",
        "difficulty": "intermediate"
    },
    "Listing Agreements_advanced": {
        "question": "A seller terminates an exclusive right to sell agreement early. Discuss the legal implications and agent's recourse options.",
        "hint": "Think about contract breach, damages, and what an agent might claim.",
        "correct_answer": "Early termination may constitute breach of contract. Agent can pursue damages (lost commission on ready, willing, willing buyers), specific performance, or exclusive listing clause enforcement. Many agreements include protection periods—if property sells within this window after termination to a buyer the agent showed, commission is owed.",
        "key_points": ["Breach of contract", "Damages", "Protection periods"],
        "topic": "Listing Agreements",
        "difficulty": "advanced"
    },
    "Cap Rates & ROI_beginner": {
        "question": "Define Cap Rate.",
        "hint": "It's an acronym related to real estate investment returns.",
        "correct_answer": "Cap Rate (Capitalization Rate) = Net Operating Income (NOI) ÷ Property Purchase Price. It represents the annual return on investment for a real estate property.",
        "key_points": ["ROI measurement", "Formula", "Investment return"],
        "topic": "Cap Rates & ROI",
        "difficulty": "beginner"
    },
    "Cap Rates & ROI_intermediate": {
        "question": "A property generates $50,000 NOI annually and sells for $500,000. What's the cap rate, and what does it tell you?",
        "hint": "Use the cap rate formula and interpret the result.",
        "correct_answer": "Cap Rate = $50,000 ÷ $500,000 = 10%. This means the property provides a 10% annual return on investment. Higher cap rates indicate better returns but often reflect riskier markets.",
        "key_points": ["Calculation", "Return interpretation", "Risk assessment"],
        "topic": "Cap Rates & ROI",
        "difficulty": "intermediate"
    },
    "Cap Rates & ROI_advanced": {
        "question": "Explain why two properties with identical cap rates may have significantly different risk profiles and investment suitability.",
        "hint": "Consider location stability, tenant quality, market conditions, and future appreciation potential.",
        "correct_answer": "Cap rate reflects current yield only. A stable urban office building at 8% cap rate in a strong market is lower risk than a 8% cap rate rural property with weak demand. Market growth, demographic trends, and tenant stability vary. Cap rate ignores appreciation potential—declining markets with high cap rates are risky despite attractive yields.",
        "key_points": ["Market risk", "Tenant stability", "Growth potential"],
        "topic": "Cap Rates & ROI",
        "difficulty": "advanced"
    },
    "Property Types_beginner": {
        "question": "Name four common residential property types.",
        "hint": "Think about different ways people live in real estate.",
        "correct_answer": "Single-family homes, townhouses, condominiums, and multi-family apartments (duplexes to apartment buildings).",
        "key_points": ["Residential categories", "Ownership structures", "Building types"],
        "topic": "Property Types",
        "difficulty": "beginner"
    },
    "Property Types_intermediate": {
        "question": "What are the key differences between owning a condo and owning a townhouse?",
        "hint": "Consider what you own, maintenance responsibilities, and HOA fees.",
        "correct_answer": "Condo owners own the unit interior; building exterior/structure is common property. Townhouse owners typically own the entire structure and land. Condos usually have HOA fees for maintenance; townhouses may have minimal HOA. Condos restrict exterior modifications; townhouses offer more owner control.",
        "key_points": ["Ownership scope", "Maintenance", "HOA responsibilities"],
        "topic": "Property Types",
        "difficulty": "intermediate"
    },
    "Property Types_advanced": {
        "question": "Analyze how zoning regulations impact property type feasibility and development potential in urban vs suburban settings.",
        "hint": "Consider density restrictions, mixed-use allowances, and market demand differences.",
        "correct_answer": "Urban zoning typically allows higher density (multifamily, mixed-use). Suburban zoning restricts to single-family. Commercial zoning prevents residential. Industrial zoning restricts office use. Zoning changes significantly impact property value and feasibility. Urban properties face development constraints but higher demand; suburban face zoning restrictions but lower density requirements.",
        "key_points": ["Zoning restrictions", "Density regulations", "Market demand"],
        "topic": "Property Types",
        "difficulty": "advanced"
    },
}


def get_fallback_question(topic: str, difficulty: str = "intermediate") -> dict:
    """Retrieve a fallback question by topic and difficulty."""
    key = f"{topic}_{difficulty}"
    if key in FALLBACK_QUESTIONS:
        return FALLBACK_QUESTIONS[key].copy()
    
    # Default fallback if specific combination not found
    default_key = f"{topic}_intermediate"
    if default_key in FALLBACK_QUESTIONS:
        return FALLBACK_QUESTIONS[default_key].copy()
    
    # Last resort: return a generic fallback
    return {
        "question": f"Can you explain key concepts related to {topic}?",
        "hint": "Think about the fundamental principles of this topic.",
        "correct_answer": "While the AI system is temporarily unavailable, please review the course materials on this topic.",
        "key_points": ["Review materials", "Core concepts", "Fundamentals"],
        "topic": topic,
        "difficulty": difficulty
    }
