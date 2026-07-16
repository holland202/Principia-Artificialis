stateDiagram-v2
    direction LR
    [*] --> Idle
    Idle --> Sampling : start
    Sampling --> Stable : T < 38.5C and ΔG <= 0
    Sampling --> Warning : ΔG > 0
    Sampling --> Critical : T >= 38.5C
    Warning --> FlushMemory : sustained anomaly
    Critical --> FlushMemory : atomic reduction collapse
    FlushMemory --> Logged : gc.collect()
    Stable --> Logged : write sample
    Logged --> Sampling : next interval
    Warning --> Sampling : recover
    Critical --> Sampling : cool down
