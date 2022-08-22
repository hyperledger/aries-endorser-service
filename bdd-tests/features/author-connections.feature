Feature: Author Endorser Connection
    Scenario: Author connects to the Endorser and sets up connection meta-data
        Given the endorser service is running
        And the endorser has a well-known public DID
        And there is a new author agent "alice"
        When "alice" connects to the endorser using their public DID
        And the endorser accepts "alice" connection request
        And "alice" sets endorser meta-data on the connection
        Then "alice" has an "active" connection to the endorser
        And the endorser has an "active" connection with "alice"

    Scenario: Author connects to the Endorser and sets up connection meta-data in one step
        Given There is a new agent "bob" that is connected to the endorser
        Then "bob" has an "active" connection to the endorser
        And the endorser has an "active" connection with "bob"
