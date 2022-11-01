@Endorsements
Feature: Author Creates various tranactions and asks for endorsement

    @Endorsements-001
    Scenario: Author connects to the Endorser and then creates a schema and credential definition
        Given There is a new agent "bob" that is connected to the endorser and has a public DID
        And "bob" has an "active" connection to the endorser
        And the endorser has an "active" connection with "bob"
        And "bob" has a public DID
        And the endorser has an "active" connection with "bob"
        And the endorser has "bob" connection configuration "Active" and "AutoEndorse"
        When "bob" creates a new schema
        And "bob" has an active schema on the ledger
        And "bob" creates a new credential definition "without" revocation support
        And "bob" has an active credential definition on the ledger
        Then "bob" has an active schema on the ledger
        And "bob" has an active credential definition on the ledger

    @Endorsements-002
    Scenario: Author connects to the Endorser and then creates a schema and credential definition with revocation
        Given There is a new agent "bob" that is connected to the endorser and has a public DID
        And "bob" has an "active" connection to the endorser
        And the endorser has an "active" connection with "bob"
        And "bob" has a public DID
        And the endorser has an "active" connection with "bob"
        And the endorser has "bob" connection configuration "Active" and "AutoEndorse"
        When "bob" creates a new schema
        And "bob" has an active schema on the ledger
        And "bob" creates a new credential definition "with" revocation support
        And "bob" has an active credential definition on the ledger
        Then "bob" has an active schema on the ledger
        And "bob" has an active credential definition on the ledger
        And "bob" has an active revocation registry on the ledger


    @Endorsements-003
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
        And "bob" creates a new credential definition "with" revocation support
        And the endorser receives an endorsement request from "bob"
        And the endorser endorses the transaction from "bob"
        And "bob" receives the endorsed transaction from the endorser
        And "bob" has an active credential definition on the ledger
        Then "bob" has an active schema on the ledger
        And "bob" has an active credential definition on the ledger
        And "bob" has an active revocation registry on the ledger
