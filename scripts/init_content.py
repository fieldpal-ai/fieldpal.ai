#!/usr/bin/env python3
"""
Initialize default content in Azure Storage
Run this script to populate Azure Storage with default homepage content
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.azure_storage import AzureStorageService

DEFAULT_CONTENT = {
    "hero": {
        "subtitle": "Real work. Real time. Real AI.",
        "title": "Voice-first AI for Frontline Workers - capture, find and fix in minutes."
    },
    "stats": {
        "stats": [
            {"number": "40%", "label": "Downtime cut"},
            {"number": "60%", "label": "Faster access"},
            {"number": "80%", "label": "Training speed"},
            {"number": "3-4", "label": "Months to ROI"}
        ]
    },
    "what-we-do": {
        "title": "What We Do",
        "heading": "Harness the power of AI for frontline operations.",
        "body": "FieldPal provides customised AI solutions tailored to the specific needs and goals of industrial operations. From manufacturing to utilities to industrial services, we deliver platform capabilities including:",
        "list_items": [
            "Voice-first data capture and analysis",
            "Legacy system integration and unified intelligence",
            "Predictive equipment maintenance and safety",
            "Real-time dashboards and decision support",
            "Enterprise-grade security and compliance"
        ],
        "button_text": "Get in touch"
    },
    "problem": {
        "title": "The Problem We Solve",
        "heading": "The challenge holding Industrial Operations Back"
    },
    "challenges": {
        "challenges": [
            {
                "title": "Unplanned Downtime",
                "heading": "5M+",
                "body": "£5M+ in annual losses from preventable equipment failures. Every unplanned shutdown triggers lost production, emergency repair costs, and cascading supply chain headaches."
            },
            {
                "title": "Knowledge Loss",
                "heading": "20+ Years",
                "body": "20+ years of expertise walks out the door each time a technician retires. New hires take over a year to catch up, meanwhile, mistakes and lost efficiency become the norm."
            },
            {
                "title": "Data Silos",
                "heading": "60%",
                "body": "Workers waste up to 60% of their time searching for information hidden in legacy systems and scattered files - time lost, problems unsolved, decisions delayed."
            },
            {
                "title": "Safety & Compliance Risk",
                "heading": "99.7%",
                "body": "99.7% accuracy and consistency is demanded by regulators, but manual processes make perfect compliance nearly impossible. The cost of a single safety slip or failed audit can devastate reputations and finances."
            }
        ]
    },
    "capture-module": {
        "subtitle": "Capture Module",
        "heading": "Hands-free, conversational capture",
        "body": "Record tasks and observations as you work. Technicians can record steps, faults and observations as they work. FieldPal automatically structures and tags every entry to the correct asset or task, turning daily activity into usable operational knowledge.",
        "list_items": [
            "Captures work even in noisy environments",
            "Auto-tags entries to assets and tasks",
            "Cuts down paperwork and manual reporting",
            "Keeps field data accurate and audit-ready"
        ],
        "tech_subtitle": "Technology",
        "tech_heading": "Core tech that powers FieldPal",
        "tech_features": [
            {
                "heading": "Micro-indexing technology",
                "text": "Sub-second indexing for precise retrieval across assets and transcripts."
            },
            {
                "heading": "Human-centred design",
                "text": "Voice-first UX optimised for noisy, hands-busy environments."
            },
            {
                "heading": "Contextual intelligence",
                "text": "Answers tailored by asset, location and role for accurate guidance."
            },
            {
                "heading": "API-first platform",
                "text": "Restful APIs and connectors to CMMS, ERP and document systems."
            }
        ]
    },
    "faq": {
        "title": "Understanding FieldPal.ai",
        "questions": [
            {
                "question": "What is FieldPal.ai?",
                "answer": "FieldPal.ai is an AI-driven platform that converts complex operational documentation into searchable, bite-sized knowledge for frontline and field workers, enabling faster troubleshooting and safer operations."
            },
            {
                "question": "Who uses FieldPal.ai?",
                "answer": "Organisations with field-facing operations — manufacturing, utilities, facilities management, large equipment service and inspection teams — that need quick access to technical knowledge and standard operating procedures."
            },
            {
                "question": "What problems does FieldPal.ai solve?",
                "answer": "It reduces asset downtime, captures tribal expertise, unifies fragmented documentation and helps teams meet compliance and safety requirements by surfacing the right information at the right time."
            },
            {
                "question": "How does FieldPal.ai work with our existing systems?",
                "answer": "FieldPal.ai is API-first and supports integration with legacy systems, document stores and ERPs so you can embed knowledge into current workflows and apps. For developer resources, request API docs via our contact form."
            },
            {
                "question": "Is FieldPal.ai secure and enterprise-grade?",
                "answer": "Yes — FieldPal.ai is designed for enterprise deployment with access controls and enterprise security features. For specific compliance, certification and data residency requirements, speak to the FieldPal team."
            },
            {
                "question": "Can field workers use FieldPal.ai offline?",
                "answer": "FieldPal.ai supports mobile-first workflows; discuss offline caching and sync options with the implementation team to ensure knowledge is available where connectivity is limited."
            },
            {
                "question": "How long does implementation take?",
                "answer": "Implementation time depends on scale and source data complexity. A typical pilot (ingesting a subset of documents and integrating one system) can be scoped within a few weeks — liaise with FieldPal for a tailored timeline."
            },
            {
                "question": "How is FieldPal.ai priced?",
                "answer": "Pricing varies by number of users, integrations and level of customisation. Contact sales for a demo and tailored quote."
            },
            {
                "question": "What support and onboarding do you offer?",
                "answer": "Onboarding includes implementation support, admin training and access to developer documentation. Ongoing support packages are available — see the Support page or contact the team."
            }
        ]
    }
}

async def main():
    """Initialize default content in Azure Storage"""
    print("Initializing default content in Azure Storage...")
    
    try:
        storage_service = AzureStorageService()
        await storage_service.save_content("home", DEFAULT_CONTENT)
        print("✓ Successfully initialized default content for homepage")
        print(f"  Content includes sections: {', '.join(DEFAULT_CONTENT.keys())}")
    except Exception as e:
        print(f"✗ Error initializing content: {e}")
        print("\nMake sure Azure Storage is configured:")
        print("  1. Set AZURE_STORAGE_CONNECTION_STRING environment variable, or")
        print("  2. Ensure Pulumi outputs are available with storage_account_name and resource_group_name")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())






