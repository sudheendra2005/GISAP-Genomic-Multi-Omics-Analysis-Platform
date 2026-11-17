---
name: emil-kowalski-ui
description: Accessible, purposeful motion and micro-interaction principles for scientific UI.
---

# Emil Kowalski UI & Motion Principles

## Overview
Guidelines derived from `emilkowalski/skills` for crafting scientific interfaces that feel polished, accessible, and responsive.

## Rules
- Honor `prefers-reduced-motion` across all transition effects.
- Use spring physics for physical interactions (modals, drawers, cards) rather than arbitrary linear animations.
- Design micro-interactions that clarify data state (upload progress, job execution status, hit selection).
- Preserve frontend isolation: animation scripts and styling never couple to backend services or business logic.
