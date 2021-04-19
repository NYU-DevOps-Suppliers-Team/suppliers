Feature: The supplier service back-end
    As an eCommerce Manager
    I need a RESTful catalog service
    So that I can keep track of all my suppliers

Background:
    Given the following suppliers
        | name       | email                   | address              | phone_number  | available |
        | Catherine  | catherine@manatee.com   | 123 Baywatch Rd      | 9991235555    | True      |
       
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
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Email" field should be empty
    And the "Address" field should be empty
    And the "phone_number" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see "Sophie" in the "Name" field
    Then I should see "sophie@test.com" in the "Email" field
    Then I should see "123 Test Road" in the "Address" field
    Then I should see "8005551234" in the "phone_number" field

# Scenario: List all pets
#     When I visit the "Home Page"
#     And I press the "Search" button
#     Then I should see "fido" in the results
#     And I should see "kitty" in the results
#     And I should not see "leo" in the results

# Scenario: List all dogs
#     When I visit the "Home Page"
#     And I set the "Category" to "dog"
#     And I press the "Search" button
#     Then I should see "fido" in the results
#     And I should not see "kitty" in the results
#     And I should not see "leo" in the results

# Scenario: Update a Pet
#     When I visit the "Home Page"
#     And I set the "Name" to "fido"
#     And I press the "Search" button
#     Then I should see "fido" in the "Name" field
#     And I should see "dog" in the "Category" field
#     When I change "Name" to "Boxer"
#     And I press the "Update" button
#     Then I should see the message "Success"
#     When I copy the "Id" field
#     And I press the "Clear" button
#     And I paste the "Id" field
#     And I press the "Retrieve" button
#     Then I should see "Boxer" in the "Name" field
#     When I press the "Clear" button
#     And I press the "Search" button
#     Then I should see "Boxer" in the results
#     Then I should not see "fido" in the results
