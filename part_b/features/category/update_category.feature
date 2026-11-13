
Feature: Update Category
  As a user
  I want to update an existing category
  So that I can correct its information

  Background:
    Given the Todo Manager API is running
    And I have recorded the current category collection

  # Normal Flow
  Scenario Outline: Rename an existing category
    Given I have created a category with title "<old_title>" and description "<description>"
    When I rename the saved category to "<new_title>"
    Then the response status should be 200
    And the saved category should have title "<new_title>" and description "<description>"

    Examples:
      | old_title | new_title     | description  |
      | Shopping  | Shopping List | Items to buy |

  # Alternate Flow
  Scenario Outline: Update only the category description
    Given I have created a category with title "<title>" and description "<old_description>"
    When I change the saved category description to "<new_description>"
    Then the response status should be 200
    And the saved category should have title "<title>" and description "<new_description>"

    Examples:
      | title   | old_description | new_description       |
      | Reading | Books to read   | Books to read in 2026 |

  # Error Flow
  Scenario Outline: Reject an empty category title during update
    Given I have created a category with title "<title>" and description "<description>"
    When I try to rename the saved category to an empty title
    Then the response status should be 400
    And the saved category should have title "<title>" and description "<description>"

    Examples:
      | title   | description       |
      | Errands | Tasks around town |
