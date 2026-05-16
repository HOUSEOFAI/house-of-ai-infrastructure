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
    "ray-cfu": {
        "name": "Ray CFU",
        "channel_handle": "@raycfu",
        "channel_id": None,
        "search_query": "Ray CFU YouTube",
        "role": "Viral Content Strategy & Growth",
        "extract_focus": [
            "viral content frameworks and what makes content spread",
            "YouTube growth and audience-building strategies",
            "content formats and styles that get high engagement",
            "hooks and thumbnails that drive clicks",
            "storytelling techniques for viral reach",
            "platform algorithm strategies",
            "monetization and offer integration within content",
            "community building and loyal audience frameworks",
        ],
        "marketing_application": (
            "Program viral content patterns, high-engagement formats, and "
            "growth-driving hooks into the daily content engine"
        ),
    },
    "melanie-ann-layer": {
        "name": "Melanie Ann Layer",
        "channel_handle": "@MelanieAnnLayer",
        "channel_id": None,
        "search_query": "Melanie Ann Layer feminine power activation",
        "role": "Feminine Power, Quantum Identity & Desire-Based Transformation",
        "extract_focus": [
            "feminine power as a creative and magnetic force",
            "quantum identity and quantum leaping frameworks",
            "desire as a compass — teaching that desire is divine direction",
            "the Activation Method and identity-level transformation",
            "being vs. doing — embodiment over hustle",
            "high-level woman identity and self-concept elevation",
            "manifestation through identity not action",
            "premium positioning through energetic authority",
            "the feminine as the source of creation and attraction",
            "wealth and success as a natural state of being",
            "releasing masculine hustle patterns for feminine flow",
            "activating the next-level version of self in clients",
            "desire-based marketing — selling through vision not pain",
            "language that activates and elevates rather than convinces",
        ],
        "marketing_application": (
            "Program desire-based, identity-elevation language into content — "
            "speak to the woman your audience is becoming, activate their next-level "
            "self-concept, and attract through embodied feminine authority rather than "
            "pain-point or hustle-based marketing"
        ),
    },
    "russell-brunson": {
        "name": "Russell Brunson",
        "channel_handle": "@RussellBrunson",
        "channel_id": "UCnXSgCcGPFBNMBBrBVSZJGQ",
        "role": "Funnel Hacking & Offer Architecture",
        "extract_focus": [
            "funnel hacking methodology — reverse-engineering competitor funnels",
            "value ladder and offer stacking frameworks",
            "the hook, story, offer framework",
            "epiphany bridge and origin story scripts",
            "dream customer avatar and customer journey",
            "two comma club funnel structures (lead magnet, tripwire, core offer, upsells)",
            "webinar funnel scripts (Perfect Webinar framework)",
            "sales letter and VSL (video sales letter) structure",
            "clickfunnels funnel types: squeeze, sales, membership, summit, challenge",
            "attractive character and soap opera sequences",
            "DotCom Secrets, Expert Secrets, Traffic Secrets frameworks",
            "offer creation and irresistible offer stacking",
            "urgency, scarcity, and deadline frameworks",
            "traffic temperature: cold, warm, hot audience sequences",
        ],
        "marketing_application": (
            "Program full funnel architecture — value ladders, offer stacks, "
            "VSL/webinar scripts, hook-story-offer sequences, and traffic-to-conversion "
            "funnels into the automated marketing engine"
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
    "funnel_architecture": "Funnel hacking structures, value ladders, and offer stacks",
    "offer_stacking": "Irresistible offer construction and bonus stacking frameworks",
    "story_selling": "Epiphany bridge, origin story, and hook-story-offer scripts",
    "traffic_sequences": "Cold/warm/hot audience nurture sequences and follow-up funnels",
    "desire_activation": "Desire-based language that speaks to who the audience is becoming",
    "quantum_identity": "Identity-elevation frameworks that activate the next-level self",
    "feminine_power": "Feminine energy, embodiment, and magnetic attraction language",
    "being_vs_doing": "Embodiment-first language patterns that replace hustle-based messaging",
}
