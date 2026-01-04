# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI debate simulation system built with Python using Microsoft's AutoGen framework. The system orchestrates structured debates between multiple AI agents playing different roles (debaters, judges, moderators) using various large language models through the OpenRouter API.

## Development Commands

### Running the Application
```bash
# Activate virtual environment (if not already activated)
venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On Unix/macOS

# Install dependencies
pip install -r requirements.txt

# Run the main application
python main.py
```

### Environment Setup
- Create a `.env` file with:
  ```
  OPENROUTER_API_KEY=your_api_key_here
  OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
  ```
- The system uses OpenRouter to access multiple AI models from different providers

## Code Architecture

### Core Components

**Main Application Flow:**
- `main.py` → Entry point that launches the Tkinter UI
- `debate_ui.py` → Complete GUI interface for debate configuration and execution
- `run_debate()` function → Core debate orchestration logic

**Agent Management:**
- `agents/factory.py` → Creates all AI agents (debaters, judges, moderator)
- `agents/custom_agents.py` → Custom agent classes extending AutoGen's base agents
- `agents/prompts.py` → System messages and prompts for different agent roles

**State Management:**
- `debate_state.py` → `DebateStateMachine` class controls debate flow and speaker transitions
- State progression: intro → opening → free_debate → closing → judging → final → end

**Configuration System:**
- `config.py` → Model assignments, API configuration, debate parameters
- `debater_traits.py` → Personality traits system for debaters
- Dynamic model assignment from multiple AI providers (Anthropic, OpenAI, Qwen, DeepSeek, etc.)

### Key Architectural Patterns

**Multi-Agent Orchestration:**
- Uses AutoGen's `GroupChat` and `GroupChatManager` for agent coordination
- Custom speaker selection via `DebateStateMachine.next_speaker()` method
- Each agent type has specific behavior through custom agent classes

**Model Diversity:**
- Pro and con sides can use different AI model providers for varied perspectives
- Judges use randomized high-quality models for independent evaluation
- Support for 20+ different AI models across 6 providers

**UI-Backend Separation:**
- UI communicates with debate logic through callback functions
- Real-time updates displayed via `ui_callback` parameter
- Threaded execution prevents UI blocking during long debates

**Independent Judge Scoring:**
- Judges evaluate debates without seeing other judges' scores
- Custom filtering ensures judges only see debate content, not evaluations
- Final scoring aggregation handled by moderator agent

### Configuration Architecture

**Dynamic Debate Parameters:**
- Configurable debaters per side (1-4)
- Adjustable judge count (1-5)
- Variable free debate rounds (1-10)
- Real-time parameter updates via `update_config()` function

**Model Assignment Strategy:**
- Random company selection for team consistency
- Per-debater model assignment within company constraints
- Judge model randomization for evaluation independence

**Trait System:**
- Predefined personality traits modify debater behavior
- Custom trait creation through UI
- Trait-specific prompt modifications

## Key Files and Responsibilities

- **`main.py`** - Application entry point and main debate execution function
- **`debate_state.py`** - State machine controlling debate flow and speaker transitions
- **`agents/factory.py`** - Agent creation and configuration with model/trait assignments
- **`agents/custom_agents.py`** - Custom agent classes (FinalModeratorAgent, FilteredAssistantAgent, DebaterAssistantAgent)
- **`config.py`** - Configuration management, model definitions, and API setup
- **`debate_ui.py`** - Complete Tkinter GUI for debate setup and real-time monitoring
- **`debater_traits.py`** - Personality trait system for debater customization

## Development Notes

**Testing Debates:**
- Use simple topics for quick testing: "Cats vs Dogs as pets"
- Monitor console output for debug information and model assignments
- Check UI real-time updates during debate execution

**Model Configuration:**
- Models are configured in `config.py` under `models_by_company`
- Judge models are separately configured in `judge_models` array
- API costs vary significantly between different models

**Error Handling:**
- `error_handler.py` provides centralized error management
- UI displays error messages through callback system
- Debug output helps track state transitions and agent behavior

**Performance Considerations:**
- Debates can run 15-30 minutes depending on model response times
- UI remains responsive through threaded execution
- Consider model costs when configuring multiple participants