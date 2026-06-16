from enum import StrEnum

class CloudModel(StrEnum):
    ANTHROPIC_CLAUDE = 'claude-sonnet-4-6'
    OPENAI_GPT = 'gpt-5.4-mini'
    GOOGLE_GEMINI = 'gemini-2.5-flash'

class CloudModelProvider(StrEnum):
    ANTHROPIC = 'anthropic'
    OPENAI = 'openai'
    GOOGLE = 'google'
