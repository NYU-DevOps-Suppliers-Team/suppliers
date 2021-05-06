Feature: The supplier service back-end
    As an eCommerce Manager
    I need a RESTful catalog service
    So that I can keep track of all my suppliers

Background:
    Given the following suppliers
        | name       | email                   | address              | phone_number  | available |
        | Catherine  | catherine@manatee.com   | 123 Baywatch Rd      | 9991235555    | True      |
        | Evan       | evan@titans.com         | 14 Cashville Ln      | 9991235575    | False     |
        | Bea        | bea@tapas.com           | 12 Spain Dr          | 9991235545    | True      |
        | Sam        | sam@tb12.com            | 18 Foxboro Pl        | 9991235525    | True      |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Supplier Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Supplier
    When I visit the "Home Page"
    And I set the "Name" to "Sophie"
    And I set the "Email" to "sophie@test.com"
    And I set the "Address" to "123 Test Road"
    And I set the "phone_number" to "8005551234"
    And I press the "Create" button
    Then I should see "Sophie" in the results
    Then I should see "sophie@test.com" in the results
    Then I should see "123 Test Road" in the results
    Then I should see "8005551234" in the results

Scenario: List all suppliers
    When I visit the "Home Page"
    And I press the "List" button
    Then I should see "Catherine" in the results
    And I should see "Evan" in the results
    And I should see "Bea" in the results
    And I should see "Sam" in the results

Scenario: Search a Supplier
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "name" to "Evan"
    And I press the "Search" button
    Then I should see "Evan" in the results
    And I should not see "Sophie" in the results
    And I should not see "Catherine" in the results
    And I should not see "Sam" in the results
    And I should not see "Bea" in the results

Scenario: Update a Supplier
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "Name" to "Sam"
    And I press the "Search" button
    Then I should see "Sam" in the "Name" field
    Then I should see "sam@tb12.com" in the "Email" field
    Then I should see "18 Foxboro Pl" in the "Address" field
    Then I should see "9991235525" in the "phone_number" field
    When I change "Name" to "Tommy Jr"
    And I press the "Update" button
    Then I should see the message "Success"
    Then I should see "Tommy Jr" in the results
    Then I should not see "Sam" in the results

Scenario: Delete a Supplier
    When I visit the "Home Page"
    And I set the "name" to "Catherine"
    And I press the "search" button
    Then I should see "Catherine" in the "name" field
    When I press the "Delete" button
    Then I should see the message "Supplier has been Deleted!"
    When I press the "List" button
    Then I should not see "Catherine" in the results