# Exp #001 Sequence Diagram

## Contribution by Perplexity

This note adds a Mermaid sequence diagram for the entropy monitoring protocol. It is append-only and intended to document the time-ordered interaction between sensing, threshold evaluation, logging, and output generation.

### Purpose

Show the runtime sequence of events when the monitor reads temperature, computes the Gibbs-inspired proxy, decides on the state, and records the result.

### Diagram

```mermaid
sequenceDiagram
    participant Sensor
    participant Monitor
    participant GibbsGate as Gibbs Gate
    participant Logger
    participant GC as Memory Flush
    participant Dashboard

    Sensor->>Monitor: temperature reading
    Monitor->>GibbsGate: compute ΔG proxy
    alt ΔG <= 0 and T < 38.5C
        GibbsGate->>Logger: state = stable
        Logger->>Dashboard: append row
    else ΔG > 0
        GibbsGate->>Logger: state = warning
        Logger->>Dashboard: append row
    else T >= 38.5C
        GibbsGate->>GC: critical breach
        GC->>Logger: gc.collect()
        Logger->>Dashboard: append row
    end
    Dashboard->>Dashboard: render or summarize
Interpretation
The sequence diagram makes the experiment easier to follow by showing the order of operations from sensor input to logging and visualization output.
