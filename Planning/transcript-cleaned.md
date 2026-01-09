# Updated Plan for Agentic AI Tools and Systems Administration

**Transcription Date:** 9 Jan 2026
**Source:** [idea-notes.mp3](./idea-notes.mp3)
**Type:** Cleaned transcript (filler words removed, punctuation added)

---

All right, so the purpose of this audio note and context and documentation is to lay down an updated plan for something I've been using agentic AI tools for quite a bit of time now, and finding a lot of success, in particular with Claude code.

The use case is specifically what you could call systems administration or using them for working on a local computer and updating local computers on the network, like a router or an Ubuntu VM, Home Assistant, basically all the devices because once you have an agent that can understand, has good reasoning, can execute Linux commands, you've essentially got the basis of a very good computer operator without any complications of vision.

So the ones that I've used it for, so I've used it extensively for my, for this computer, which is a Linux Ubuntu desktop, but then pretty much everything else on the network that I have, which has kind of I would say sprawled over time into an accidental kind of home lab, but it's incredibly useful.

## Managing Remotes with Claude: Three Methods

What I figured out is that there are a few ways that you can do this to manage a remote with Claude code. The first is you can put Claude on any remote, so I can go into my home server, install Claude, SSH into the server, run Claude, and then I'm running Claude within the context. It's local to that server. That's, let's say, method one.

Method two is asking Claude just to do stuff on different machines with SSH. I need to authenticate with SSH in order for that to work. Then I typically do something like say, "Okay, these are my SSH aliases. This is what each one is." So like kind of a human description, bash aliases, and then saying with that very, very small layer of context, I can then say things like, "Oh, check why the IP camera thing is not working on the home server." Then it can say, "Okay, home server means SSH alias this, and I'm going to do that."

Approach number three, which is much more recent that I've begun doing this, and I assumed that two and three were kind of synonymous. There was really not much of an advantage to three. But then I saw it work in practice and it changed my mind. Three is using MCP.

MCP in this context, the kind of architecture that I documented a few weeks ago. This is basically a planning note/actual implementation for a GUI version of that. The MCP version is just, "Okay, these are the things on my home network. I have an Ubuntu VM, I have a router, I have a Raspberry Pi, I have one or two other things." I'm going to put a very lightweight MCP server on all of these endpoints. Then, instead of telling Claude to use SSH, I'm going to just say, "Connect to these MCPs." I'm going to give an MCP tool exposure.

## MCP Servers and Performance Advantages

What I noticed was that, and this was the Raspberry Pi bug, it was just like not working. I couldn't get it to work over SSH. Something was overloading the Raspberry Pi, so Claude would connect, try to start fixing something, and then the Pi would run out of memory and I couldn't fix it.

Then I said, okay, so this was an accidental discovery. Why don't we put a little MCP server on the on the Pi? Then let's exit this session. Next session, connect via MCP and try to fix the problem. That worked. Basically, the overhead of MCP, I guess, was a lot lighter than the previous method.

So I thought, this is a good pattern. I'm going to put these MCP servers on every computer on the network. I can use something like Meta MCP, which is a very cool project, an MCP aggregator to aggregate together an MCP server that's like home management MCP. I can have all the things that, excuse me, I might want to have my home network. So like Home Assistant, Homebox, which is what we use for inventory, what else, those computers.

That's an appealing idea because it's like, "Oh, I'll just have a home management MCP," and I can use agents to do everything on the home. But we run into the problem of tools and context, which I'm very confident will be solved this year with the MCP standard, but until we have proper dynamic tool exposure, we have to take this approach of minimal tools for the job. Bring a, bring as compact a toolbox as you can for the task. For that reason, the idea and design for this implementation is kind of a spin on something I've been trying, which is creating what I call Claude spaces. It's my own terminology. Claude space meaning a repository where you have cloud.md providing the context, and you have mcp.json providing the MCP.

## Implementation Attempts

So, there are two things I'd like to try in this in this implementation attempt. The first is what you, what we might call the preferred approach, which is providing MCP one aggregated MCP for everything on the network, all the all the computers, and then having a cloud.md saying, "You are the, you are the land manager. Your task is to work with the user to administer local computers on the network. Here is a rough guide to what the names are and what they do. Save logs in this folder." You have all this all the things via MCP. Now that's going to give it the heaviest load because every MCP tool is going to, it's going to add its tool, but on the plus side, it's the easiest. There's only one assistant to configure. There's only one, there's only one, and there's one single set of MCPs.

The second approach that I'd like to do as well is to have a modular approach. It's worth, I think, having both because it might be the case that the single computer manager performs better because it doesn't have to, you eliminate the potential of it making a mistake, getting the, connecting to the wrong machine, getting confused by the wrong MCP. So it's very much you are the, and I'm going to use my Ubuntu VM. It's my home server. You are the Ubuntu VM manager. Here's an MCP to it.

For GUI, what I want to do basically is the goal of this of this design is to eliminate, I've already used this approach for a consolidated repository manager. And what I want to do is eliminate the time that I, you know, every day go connect to Ubuntu VM and do this thing. So what I'm envisioning is just a, and the question is, can this wrap around Claude in a way that actually works. This is what the goal is, a GUI window and presenting the assistance, assistance in the plural.

One being, as I said, the kind of home network manager, that's the meta configuration. These are all locally, this is all local MCP connections or local to, and all the MCPs on my network are streamable HTTP. Important detail.

So, at the front page, we're going to have the LAN manager, the big, the consolidated one, and then one button for each computer. It would be worth trying actually maybe just to really flesh out this experiment. One, one for the SBCs, Raspberry Pi and bedroom, two orange pies I have. I use those mostly for audio. So one that actually says, "You're in charge of three computers, here's three MCPs." So it's kind of a between the two, between the individual configs and the master one. Then one that says you are just for this computer. I'll create one of those for each, each computer. I'll provide the list. I'll provide the IP addresses, static IPs. I'll provide the MCPs. Are those can be discovered on the local network. They're unauthenticated.

So it's really a launcher that if I go into Ubuntu, our home server manager, the idea would be that it would open up a console. I'm using in KDE Plasma, the terminal, at the subfolder for that computer with cloud.md instructing its job being specifically executing commands using the MCP to update the server. Here's what the server is, here's what it does. And maybe instructing it to use the logs subfolder, so a subfolder within the computer folder for saving logs and context data. And that's it. So you get you open you click that and Claude propagates in Claude opens in that subfolder with, oh, and of course, how could I forget the MCP. So it's got mcp.json. And what I really want is, I don't want to, I want this to be, I forget the way Claude do it at the moment, but for the individual computers, actually for all of these configs, I want what I define in mcp.json to be that's the MCP, that's the full list. In other words, I don't want to add my user level MCPs on top or beneath this one. This should be just the agent has just this one tool as we define it.

So in summary, creating a GUI providing a kind of UI skeleton around functionality for creating Claude.md Claude assistance, whose task it is to take actions on a local computer or remote in time, but let's start with local for ease of authentication, operating via a preconfigured MCP with a preconfigured cloud.md defining the role, and with a couple of folders ready in place for them to be able to persistently save things like documentation and logs to support the, to basically reduce manual effort in directing Claude to work on local computers and make it a much more seamless and time efficient process while still benefiting from the power and utility of Claude code as the as the actual agent.
