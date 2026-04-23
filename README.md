# CaptureTheTarget
AI-Driven Network Pathfinder

A Cybersecurity-Focused Network Visualization & Pathfinding Application

CaptureTheTarget is an interactive GUI application that visualizes network topologies and demonstrates pathfinding algorithms (BFS and A*) in the context of cyber attack simulations. Built with Python and Tkinter, it provides an educational platform for understanding how different search algorithms explore network graphs.
📋 Table of Contents

    Features

    Quick Start

    Algorithm Details

✨ Features
Core Functionality

    Interactive Network Visualization – Nodes and edges rendered on a customizable canvas

    Dual Pathfinding Algorithms – BFS (Breadth-First Search) and A*

    Algorithm Comparison Mode – Run both algorithms simultaneously and compare efficiency

    Real-time Animation – Watch algorithms explore the network node by node

    Click & Shift+Click Selection – Intuitive start/target node selection

Visualization Features

    Device Icons – Visual indicators for different node types (Router, Switch, Server, etc.)

    Security Rating System – 1-5 security level indicators with color-coded dots

    Edge Weight Display – Connection costs shown on each link

    Dynamic Edge Coloring – Different colors for visited paths and unexplored edges

    Comparison Visualization – BFS vs A* when in compare mode

Information Panels

    System Log – Timestamped, color-coded event logging

    Results Panel – Detailed metrics including path length and nodes explored

    Status Bar – Real-time node/edge count and simulation status

    Hover Tooltips – Node information on mouse hover (type, security level)

Configuration Options

    Multiple Network Presets – Predefined topologies (Enterprise, Data Center, etc.)

    Custom Start/Target Selection – Via canvas or dropdown menus

    Regenerate Network – Randomize node positions while preserving topology

🎮 Quick Start

    Select a network preset from the dropdown menu

    Choose start and target nodes:

        Normal click on a node → Set as START (green)

        Shift+Click on a node → Set as TARGET (red)

    Pick an algorithm:

        BFS – Guarantees shortest hop count

        A* – Uses heuristic for smarter search

        COMPARE BOTH – Run side-by-side comparison

    Click RUN SIMULATION – Watch the algorithm explore the network

    View results in the RESULTS tab

🧠 Algorithm Details
BFS (Breadth-First Search)

    Strategy – Explores neighbors layer by layer

    Guarantee – Finds shortest path in terms of hop count

    Best For – Unweighted graphs, finding minimum hops

A* (A-Star Search)

    Strategy – Uses heuristic + cost to guide search

    Heuristic formula – f(n) = g(n) + h(n)

        g(n) = cost from start to current node

        h(n) = estimated cost to target (heuristic)

    Best For – Weighted graphs, faster pathfinding

Comparison Mode

When "COMPARE BOTH" is selected:

    BFS runs first (cyan highlights)

    A* runs second (orange highlights)

    Results show side-by-side comparison

    Winner determined by fewer nodes explored
