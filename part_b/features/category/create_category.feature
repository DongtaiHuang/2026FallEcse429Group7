
Feature: Create Category
  As a user
  I want to create a category
  So that I can classify my tasks

  Background:
    Given the Todo Manager API is running
    And I have recorded the current category collection

  # Normal Flow
  Scenario Outline: Create a category with a title and description
    When I create a category with title "<title>" and description "<description>"
    Then the response status should be 201
    And the saved category should have title "<title>" and description "<description>"

    Examples:
      | title      | description          |
      | Coursework | Tasks for my courses |

  # Alternate Flow
  Scenario Outline: Create a category with only a title
    When I create a category with only the title "<title>"
    Then the response status should be 201
    And the saved category should have title "<title>" and an empty description

    Examples:
      | title    |
      | Personal |

  # Error Flow
  Scenario Outline: Reject a category with an empty title
    When I try to create a category with an empty title and description "<description>"
    Then the response status should be 400
    And the category collection should be unchanged

    Examples:
      | description         |
      | Tasks for this week |
