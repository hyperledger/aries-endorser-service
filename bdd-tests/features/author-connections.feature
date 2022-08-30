@Connections
Feature: Author Endorser Connection

    @Connections-001
    Scenario: Author connects to the Endorser and sets up connection meta-data
        Given the endorser service is running
        And the endorser has a well-known public DID
        And there is a new author agent "alice"
        When "alice" connects to the endorser using their public DID
        And the endorser accepts "alice" connection request
        And "alice" sets endorser meta-data on the connection
        Then "alice" has an "active" connection to the endorser
        And the endorser has an "active" connection with "alice"

    @Connections-002
    Scenario: Author connects to the Endorser (with auto-accept) and sets up connection meta-data
        Given the endorser service is running
        And the endorser has "ENDORSER_AUTO_ACCEPT_CONNECTIONS" configured as "true"
        And the endorser has a well-known public DID
        And there is a new author agent "alice"
        When "alice" connects to the endorser using their public DID
        And "alice" sets endorser meta-data on the connection
        Then "alice" has an "active" connection to the endorser
        And the endorser has an "active" connection with "alice"

    @Connections-003
    Scenario: Author connects to the Endorser and sets up connection meta-data in one step
        Given There is a new agent "bob" that is connected to the endorser
        Then "bob" has an "active" connection to the endorser
        And the endorser has an "active" connection with "bob"

    @Connections-004
    Scenario: Author connects to the Endorser and sets up connection meta-data in one step
        Given There is a new agent "bob" that is connected to the endorser (with auto-accept)
        Then "bob" has an "active" connection to the endorser
        And the endorser has an "active" connection with "bob"
