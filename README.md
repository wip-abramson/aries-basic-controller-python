# Aries Basic Controller Python

A simple pip installable wrapper for an aries agent admin API calls.

See the demo folder for an example of how to use this in your project.

Current functionality:
* Spin up two docker images for the researcher and data owner agents
* Load the example.py file
    * Create webhook listeners for connection and basic messages
    * Establish connection between two agents
    * Send basic messages between two agents
    * Listen for webhook events