---
title: 'When Your Project Starts Explaining Itself'
description: 'Experimenting with NotebookLM from Google to turn messy project documentation into organized diagrams, summaries, and even architecture explanation videos.'
pubDate: '2025-11-29'
heroImage: './project-explains-itself-hero.png'
tags: ['ai-tools', 'workflow', 'notes']
---

Lately I've been experimenting with **NotebookLM** from Google (you can poke it here: [notebooklm.google](https://notebooklm.google/)).

For one of my projects, **Luntra**, I dumped pretty much *all* of its documentation into NotebookLM: architecture notes, specs, half-finished diagrams, and those heroic "TODO: document later" sections that somehow made it in. Instead of collapsing under the weight of my chaos, the system calmly digested everything and started talking back to me like it had been on the team for months.

---

## Reorganizing My Own Material

The first surprise was how well it **reorganized** my own material. I knew what Luntra was in my head, but NotebookLM turned that into something more structured: clear sections, a map of core ideas, and a kind of conceptual "table of contents" that I never had time to create properly. It felt like handing your messy room to an AI and getting a floor plan back.

Then it went visual. NotebookLM generated **graphical representations of the main concepts**—how pieces of Luntra relate, where the flows are, what plays with what. I've drawn diagrams before, but this time it was built directly from the docs I'd already written. No extra modeling tool, no manual dragging of arrows at midnight. Just: "Here, this is how your system looks, structurally."

---

## From Documentation to Video

And then there was the **video**. From the same documentation pile, NotebookLM generated an architecture explainer:

<video controls preload="metadata" style="width: 100%; max-width: 800px; margin: 2rem auto; display: block; border-radius: 8px;" playsinline>
  <source src="/videos/Luntra_s_Architecture.mp4" type="video/mp4; codecs=avc1.42E01E,mp4a.40.2">
  <p>Your browser does not support HTML5 video. You can <a href="/videos/Luntra_s_Architecture.mp4">download the video</a> instead.</p>
</video>

The result wasn't some Hollywood trailer, but it was shockingly decent. It walked through the main components, explained the data flow, and highlighted the big ideas in a way that would take me hours to script and storyboard on my own.

---

## Active Documentation

What really hits me is how this changes the way I think about **project documentation**. Traditionally, docs sit in folders like a digital attic. You know there's something valuable there, but you only go in when you have to. With tools like NotebookLM, those same documents become *active*—they can respond, summarize, visualize, and even narrate your own architecture back to you.

It also flips the usual direction of effort. Instead of "I need to find time to make a nice diagram and a clean explanation," the workflow becomes "I'll write honest, detailed docs, and then let the system generate the polished artifacts." Suddenly, writing documentation looks less like a chore and more like feeding a very hungry visualization machine.

---

## Self-Explaining Systems

On a philosophical level, this feels like the early stages of **self-explaining systems**. You design and build a platform like Luntra, you document it as best you can, and then an AI agent reorganizes that knowledge into interfaces, graphs, and videos you can hand to new teammates, investors, or your future self. The project becomes capable of introducing itself.

There's also something quietly funny about watching your own work explained back to you in a cleaner way than you've ever described it. You spend weeks wrestling with architecture decisions, layering components, juggling services—and then a model reads your notes and says, "So what you *meant* was this," and presents a crisp summary.

---

## The Heavy Lifting Still Matters

Of course, this doesn't replace actual thinking or design. The heavy lifting is still in the architecture choices, trade-offs, and the boring parts of reality (latency, edge cases, budgets, all the usual suspects). But once that thinking is captured in text, tools like NotebookLM turn it into a kind of multi-format knowledge layer: text, diagrams, Q&A, and now even video.

So from now on, when I'm working on Luntra, I don't just see a pile of docs. I see raw material for future visualizations, walkthroughs, and explainers. And somewhere in Google's servers, NotebookLM is politely waiting for the next batch of notes, ready to transform them into yet another version of my project that looks more organized than my brain feels.
