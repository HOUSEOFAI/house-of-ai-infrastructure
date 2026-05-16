"""
Creator channel configurations and extraction goals for the
House of AI™ marketing & content knowledge engine.
"""

CREATORS = {
    "chase-hughes": {
        "name": "Chase Hughes",
        "channel_handle": "@chasehughes",
        "channel_id": "UCQnK22_pHSMgGcPQ09gMbig",
        "role": "Buyer Psychology & Behavioral Influence",
        "extract_focus": [
            "behavioral profiling frameworks (PRISM, 6MWF)",
            "buyer psychology triggers and compliance sequences",
            "language patterns and scripts for influence",
            "the 6 laws of influence and persuasion",
            "behavioral tells and reading people",
            "authority and trust-building frameworks",
            "objection dissolution language",
            "covert compliance techniques",
        ],
        "marketing_application": (
            "Program buyer psychology triggers, influence sequences, and "
            "behavioral language patterns into marketing copy and sales content"
        ),
    },
    "leanne-mosley": {
        "name": "Leanne Mosley (Rich Queen)",
        "channel_handle": "@RichQueenLM",
        "channel_id": None,  # Set after lookup or use search
        "search_query": "Leanne Mosley Rich Queen",
        "role": "Messaging & Identity-Based Marketing",
        "extract_focus": [
            "messaging frameworks for premium positioning",
            "identity-based messaging and client attraction language",
            "wealth mindset language patterns",
            "niche clarity and voice frameworks",
            "high-ticket offer messaging",
            "queen energy and authority communication",
            "visibility and content messaging strategy",
        ],
        "marketing_application": (
            "Program premium messaging, identity language, and "
            "authority positioning into all content and copy"
        ),
    },
    "brooke-shelton": {
        "name": "Brooke Shelton",
        "channel_handle": "@BrookeShelton",
        "channel_id": None,
        "search_query": "Brooke Shelton content marketing",
        "role": "Content Structure & Strategy",
        "extract_focus": [
            "content pillar frameworks",
            "story structure and narrative arcs",
            "content batching and repurposing systems",
            "hook formulas and opening structures",
            "content calendar and strategic flow",
            "audience journey mapping through content",
            "conversion-focused content architecture",
        ],
        "marketing_application": (
            "Program content structure, story arcs, hook formulas, and "
            "strategic content flow into the content engine"
        ),
    },
}

# Marker categories that map to the marketing engine
MARKETING_MARKERS = {
    "psychology_triggers": "Buyer psychology and behavioral influence points",
    "messaging_language": "Identity-based messaging and authority language patterns",
    "content_structure": "Frameworks for structuring content that converts",
    "hooks_and_opens": "Attention-capturing openings and hook formulas",
    "objection_handling": "Language patterns for dissolving resistance",
    "authority_signals": "Trust and authority-building frameworks",
    "identity_shifts": "Language that shifts buyer identity and self-concept",
    "conversion_sequences": "Step-by-step sequences that move people to action",
}
