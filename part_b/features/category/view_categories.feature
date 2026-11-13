
Feature: View Categories
  As a user
  I want to view my categories
  So that I can organize my tasks

  Background:
    Given the Todo Manager API is running
    And I have recorded the current category collection

  # Normal Flow
  Scenario Outline: View the category list
    Given I have created a category named "<title>"
    When I request the category list
    Then the response status should be 200
    And the category list should include the category I last created

    Examples:
      | title     |
      | Groceries |

  # Alternate Flow
  Scenario Outline: Filter categories by title
    Given I have created a category named "<other_title>"
    And I have created a category named "<title>"
    When I request categories with title "<title>"
    Then the response status should be 200
    And the category list should include the category I last created
    And every returned category should have title "<title>"

    Examples:
      | title   | other_title |
      | Reading | Errands     |

  # Error Flow
  Scenario Outline: Reject an unsupported response format
    When I request the category list with Accept "<media_type>"
    Then the response status should be 406
    And the category collection should be unchanged

    Examples:
      | media_type       |
      | application/yaml |
