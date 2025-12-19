---
title: 'Tasks as Thought: Building a Personal Cognitive Interface with MCP and Todoist'
description: 'A task is not an action—it is a decision to care later. This post explores building an MCP server connected to Todoist that treats tasks as compressed representations of thought, creating a cognitive interface that respects the shape of thinking.'
pubDate: '2025-12-19'
heroImage: '../../assets/tasks-as-thought-hero.png'
tags: ['ai', 'productivity', 'mcp', 'tools']
---

For a long time, I believed that task management was about discipline.
Later, I believed it was about systems.
Only recently did it become clear that it is really about **how thought turns into action**.

Most productivity tools quietly assume something false: that we think in tasks.
We don't.
We think in fragments, paragraphs, contradictions, half-formed intentions, and long stretches of uncertainty. Tasks appear only at the very end of this process, as a kind of compression artifact.

This post is about an attempt to work closer to the source.

## Thought Is Not Atomic

Human thinking is not made of checkboxes. It is continuous, narrative, recursive.

Ideas arrive as text. Sometimes spoken. Sometimes emotional. Sometimes technical. Sometimes philosophical. They are rarely shaped like "Do X at 3 PM."

When we force these raw thoughts directly into task managers, we lose something important: **context**. The *why* collapses, dependencies disappear, and the task becomes brittle. It either gets done mechanically or avoided indefinitely.

I wanted a system that respected the *shape of thinking*, not just the shape of execution.

## Tasks as Compressed Intentions

A task is not an action.
A task is a **decision to care later**.

It is a promise between two versions of yourself: the one who understands the problem now, and the one who will face it in the future. The tragedy of most task systems is that this promise is underspecified.

By the time the future arrives, the meaning is gone.

So I started treating tasks not as actions, but as **compressed representations of thought**. Lossy compression, inevitably—but with the goal of minimizing semantic loss.

That framing changed everything.

## MCP as an External Cognitive Layer

I built a local MCP server connected to Todoist and plugged it into my Cloud Desktop environment.

Technically, this is straightforward. Conceptually, it is not.

What this setup does is remove the UI from the loop and replace it with **language**. I no longer manage tasks by clicking and dragging. I describe intentions. I provide context. I think out loud.

The system can:
- create, delete, and modify tasks
- break long texts into structured action items
- infer priorities and near-term plans
- reshape tasks as my understanding evolves

The important part is not automation.
The important part is **interpretation**.

## The Extended Mind, Implemented

Philosophers of mind have long argued that cognition does not stop at the skull. Notes, diagrams, language, and tools are not aids to thinking—they *are thinking*.

This system is my attempt to take that idea seriously.

The MCP server becomes a kind of cognitive membrane:
- raw thought enters as text
- structure emerges through interpretation
- future behavior is shaped as a result

Todoist stops being a task list and becomes **memory with intention attached**.

## Work as a Dataset

Once tasks are created through this layer, something interesting happens: work becomes observable.

Not in a surveillance sense, but in an epistemic one.

You can analyze:
- how often you decompose versus postpone
- where complexity clusters
- which projects generate cognitive friction
- how language predicts avoidance
- where optimism consistently overrides reality

This is not productivity analytics.
It is **self-study**.

The system quietly accumulates a dataset about how you actually work, not how you claim to.

## Why This Is Open Source

I published the MCP Todoist server as a free public GitHub repository - [MCP-Todoist](https://github.com/t-boris/MCP-Todoist)

Not because it is "finished."
Not because it is "the right way."

But because we are at a strange inflection point.

For the first time, tools can:
- read language
- extract intention
- act on our behalf
- remember for us

The question is no longer which app is best.
The question is **what kind of thinking we want our tools to encourage**.

## A Different Definition of Order

Order is often confused with control.
Control with rigidity.
Rigidity with seriousness.

But real order is fluid. It adapts. It renegotiates meaning as understanding changes.

This system does not try to make me more efficient.
It tries to make me more *honest*—about what I'm doing, why I'm doing it, and what I am avoiding.

Tasks, in this sense, are not obligations.
They are **artifacts of thought over time**.

And once you see them that way, productivity stops being a performance—and becomes a dialogue.

The repository link is below.
Use it, adapt it, or ignore it.

But if you are interested in building tools that think *with* you instead of *for* you, this is a place to start.
