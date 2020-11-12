# domain messages

Domain specific Python message classes for the SimCES platform.

The following messages have been defined:

- `ResourceStateMessage`
    - Child class of AbstractResultMessage
    - Adds Bus, RealPower, ReactivePower, Node and StateOfCharge
    - Definition: [ResourceState](https://wiki.eduuni.fi/display/tuniSimCES/ResourceState)