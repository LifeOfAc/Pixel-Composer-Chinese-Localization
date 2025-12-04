MK Panels is a node for generating random industrial panels. It consists of 2 processes, Panel generation and Shape drawing. Each process relies on a "Pattern" string which defines a set of rules. A pattern can contain duplicate symbols to increase the chance of being selected.

## Panel Pattern Symbols

{g}
<x20> [x]    <x40>  Split X axis
<x20> [y]    <x40>  Split Y axis
<x20> [h(n)] <x40> Split X axis (n) parts equally
<x20> [v(n)] <x40> Split Y axis (n) parts equally
<x20> [i]    <x40>  Inset
<x20> [I]    <x40>  Inset uniform
<x20> [f]    <x40>  Frame
<x20> [F]    <x40>  Frame uniform
<x20> [e]    <x40>  Empty frame
<x20> [E]    <x40>  Empty frame uniform
{g}

## Shape Pattern Symbols

{g}
<x20> [r]  <x40> Rectangle
<x20> [d]  <x40> Cut cornered Rectangle
<x20> [c]  <x40> Round cornered Rectangle
<x20> [P]  <x40> Shaded pipes
<x20> [*s] <x40> Add slots
{g}