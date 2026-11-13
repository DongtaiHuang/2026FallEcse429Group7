
Feature: Retrieve Category by ID
  As a user
  I want to retrieve a category by its ID
  So that I can review its details

  Background:
    Given the Todo Manager API is running
    And I have recorded the current category collection

  # Normal Flow
  Scenario Outline: Retrieve a category with a title and description
    Given I have created a category with title "<title>" and description "<description>"
    When I request the category I last created by ID
    Then the response status should be 200
    And the response should contain the requested category with title "<title>" and description "<description>"

    Examples:
      | title   | description     |
      | Fitness | Weekly workouts |

  # Alternate Flow
  Scenario Outline: Retrieve a category created without a description
    Given I have created a category named "<title>"
    When I request the category I last created by ID
    Then the response status should be 200
    And the response should contain the requested category with title "<title>" and an empty description

    Examples:
      | title  |
      | Travel |

  # Error Flow
  Scenario Outline: Retrieve a category that no longer exists
    Given I have created a category named "<title>"
    And the category I last created has been deleted
    When I request the category I last created by ID
    Then the response status should be 404

    Examples:
      | title             |
      | Temporary Archive |
