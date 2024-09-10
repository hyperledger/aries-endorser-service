@Endorsements
Feature: Author Creates various tranactions and asks for endorsement

    @Endorsements-001
    Scenario: Author connects to the Endorser and then creates a schema and credential definition without revocation and granularly auto-endorse
        Given There is a new agent "bob" that is connected to the endorser and has a public DID
        And "bob" has an "active" connection to the endorser
        And the endorser has an "active" connection with "bob"
        And "bob" has a public DID
        And the endorser has an "active" connection with "bob"
        When "bob" creates a new schema
        And the endorser receives an endorsement request from "bob"
        Then the endorser allows "bob" last schema
        And "bob" receives the endorsed transaction from the endorser
        And "bob" has an active schema on the ledger
        And "bob" creates a new credential definition with the last schema from "bob" "without" revocation support
        And the endorser allows "bob" last credential definition "without" revocation support
        And "bob" has an active credential definition on the ledger
        Then "bob" has an active schema on the ledger
        And "bob" has an active credential definition on the ledger

    @Endorsements-002
    Scenario: Author connects to the Endorser and then creates a schema and credential definition with revocation and granularly auto-endorse
        Given There is a new agent "bob" that is connected to the endorser and has a public DID
        And "bob" has an "active" connection to the endorser
        And the endorser has an "active" connection with "bob"
        And "bob" has a public DID
        And the endorser has an "active" connection with "bob"
        When "bob" creates a new schema
        Then the endorser allows "bob" last schema
        And "bob" has an active schema on the ledger
        And "bob" creates a new credential definition with the last schema from "bob" "with" revocation support
        And the endorser allows "bob" last credential definition "with" revocation support
        And "bob" has an active credential definition on the ledger
        Then "bob" has an active schema on the ledger
        And "bob" has an active credential definition on the ledger


    @Endorsements-003
    Scenario: Author connects to the Endorser and then creates a schema and credential definition
        Given There is a new agent "bob" that is connected to the endorser and has a public DID
        And "bob" has an "active" connection to the endorser
        And the endorser has an "active" connection with "bob"
        And "bob" has a public DID
        And the endorser has an "active" connection with "bob"
        And the endorser has "bob" connection configuration "Active" and "AutoEndorse"
        When "bob" creates a new schema
        And "bob" has an active schema on the ledger
        And "bob" creates a new credential definition with the last schema from "bob" "without" revocation support
        And "bob" has an active credential definition on the ledger
        Then "bob" has an active schema on the ledger
        And "bob" has an active credential definition on the ledger

    @Endorsements-004
    Scenario: Author connects to the Endorser and then creates a schema and credential definition with revocation
        Given There is a new agent "bob" that is connected to the endorser and has a public DID
        And "bob" has an "active" connection to the endorser
        And the endorser has an "active" connection with "bob"
        And "bob" has a public DID
        And the endorser has an "active" connection with "bob"
        And the endorser has "bob" connection configuration "Active" and "AutoEndorse"
        When "bob" creates a new schema
        And "bob" has an active schema on the ledger
        And "bob" creates a new credential definition with the last schema from "bob" "with" revocation support
        And "bob" has an active credential definition on the ledger
        Then "bob" has an active schema on the ledger
        And "bob" has an active credential definition on the ledger
        And "bob" has an active revocation registry on the ledger


    @Endorsements-005
    Scenario: Author connects to the Endorser and then creates a schema and credential definition with revocation and specific auto-endorse
        Given There is a new agent "bob" that is connected to the endorser and has a public DID
        And "bob" has an "active" connection to the endorser
        And the endorser has an "active" connection with "bob"
        And "bob" has a public DID
        And the endorser has "bob" connection configuration "Active" and "AutoEndorse"
        And the endorser has "ENDORSER_AUTO_ENDORSE_REQUESTS" configured as "true"
        And the endorser has "ENDORSER_AUTO_ENDORSE_TXN_TYPES" configured as "113,114"
        When "bob" creates a new schema
        And the endorser receives an endorsement request from "bob"
        And the endorser endorses the transaction from "bob"
        And "bob" receives the endorsed transaction from the endorser
        And "bob" has an active schema on the ledger
        And "bob" creates a new credential definition with the last schema from "bob" "with" revocation support
        And the endorser receives an endorsement request from "bob"
        And the endorser endorses the transaction from "bob"
        And "bob" receives the endorsed transaction from the endorser
        And "bob" has an active credential definition on the ledger
        Then "bob" has an active schema on the ledger
        And "bob" has an active credential definition on the ledger
        And "bob" has an active revocation registry on the ledger

    @Endorsements-006
    Scenario: Endorser endorses the creation of a schema and credential definition by overwriting the allow list using a csv
        Given There is a new agent "bob" that is connected to the endorser and has a public DID
        And "bob" has an "active" connection to the endorser
        And the endorser has an "active" connection with "bob"
        And "bob" has a public DID
        And the endorser has an "active" connection with "bob"
        When "bob" creates a new schema
        Then the endorser allows "bob" last schema from file via "POST"
        And "bob" has an active schema on the ledger
        And "bob" creates a new credential definition with the last schema from "bob" "with" revocation support
        And the endorser allows "bob" last credential definition "with" revocation support from file via "PUT"
        And "bob" has an active credential definition on the ledger
        Then "bob" has an active schema on the ledger
        And "bob" has an active credential definition on the ledger
        
    @Endorsements-007
    Scenario: Endorser endorses the creation of a schema and credential definition by appending to the allow list using a csv
        Given There is a new agent "bob" that is connected to the endorser and has a public DID
        And "bob" has an "active" connection to the endorser
        And the endorser has an "active" connection with "bob"
        And "bob" has a public DID
        And the endorser has an "active" connection with "bob"
        When "bob" creates a new schema
        Then the endorser allows "bob" last schema from file via "PUT"
        And "bob" has an active schema on the ledger
        And "bob" creates a new credential definition with the last schema from "bob" "with" revocation support
        And the endorser allows "bob" last credential definition "with" revocation support from file via "PUT"
        And "bob" has an active credential definition on the ledger
        Then "bob" has an active schema on the ledger
        And "bob" has an active credential definition on the ledger

    @Endorsements-008
    Scenario: Endorser adds a 2 duplicate schemas causing a rollback without losing the previous state of the db using the csv
        Given There is a new agent "bob" that is connected to the endorser and has a public DID
        And "bob" has an "active" connection to the endorser
        And the endorser has an "active" connection with "bob"
        And "bob" has a public DID
        And the endorser has an "active" connection with "bob"
        When "bob" creates a new schema
        Then the endorser allows "bob" last schema from file via "POST"
        And the endorser fails to allow duplicate schemas from file
        And "bob" has an active schema on the ledger

    @Endorsements-009
    Scenario: Endorser adds a 2 duplicate schemas causing a rollback without losing the previous state of the db
        Given There is a new agent "bob" that is connected to the endorser and has a public DID
        And "bob" has an "active" connection to the endorser
        And the endorser has an "active" connection with "bob"
        And "bob" has a public DID
        And the endorser has an "active" connection with "bob"
        When "bob" creates a new schema
        Then the endorser allows "bob" last schema from file via "POST"
        And the endorser fails to allow "bob" duplicate schemas

    @Endorsements-010
    Scenario: Endorser endorses the creation of a schema and credential definition by appending to the allow list using a csv
        Given There is a new agent "bob" that is connected to the endorser and has a public DID
        And "bob" has an "active" connection to the endorser
        And the endorser has an "active" connection with "bob"
        And "bob" has a public DID
        Given There is a new agent "bill" that is connected to the endorser and has a public DID
        And the endorser has an "active" connection with "bill"
        And "bill" has an "active" connection to the endorser
        And the endorser has an "active" connection with "bill"
        And "bill" has a public DID
        And the endorser has an "active" connection with "bill"
        When "bill" creates a new schema
        Then the endorser allows "bill" last schema from file via "PUT"
        And "bill" has an active schema on the ledger
        And "bob" creates a new credential definition with the last schema from "bill" "with" revocation support
        And the endorser allows "bob" last credential definition with schema created by "bill" "with" revocation support
        And "bob" has an active credential definition on the ledger
        Then "bill" has an active schema on the ledger
