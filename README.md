# Autonomous Video Generator

This project automatically generates 30-second vertical videos (YouTube Shorts, Instagram Reels) from breaking news using a multi-stage pipeline, LLMs, and cloud services.

## Features
- News fetching, validation, and script generation
- Image and video creation with AI and FFmpeg
- Automated publishing to YouTube and Instagram
- Error-aware, retryable pipeline with MongoDB state

## Structure
See the directory tree for details on each module.

## Setup
1. Copy `.env.example` to `.env` and fill in credentials.
2. `pip install -r requirements.txt`
3. Run with Docker Compose or locally.

## Docs
- See `docs/PRD.md` for the full product requirements and schema. 