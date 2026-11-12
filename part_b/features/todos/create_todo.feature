
Feature: Create Todo
  As a user
  I want to create a new todo
  So that I can track my tasks

  Background:
    Given the Todo Manager API is running

  # Normal Flow
  Scenario Outline: Successfully create a todo
    When I create a todo with title "<title>"
    Then the response status should be 201
    And the todo with title "<title>" should exist

    Examples:
      | title          |
      | Study ECSE 429 |
      | Finish Part B  |

  # Alternate Flow
  Scenario Outline: Create a todo with title and description
    When I create a todo with title "<title>" and description "<description>"
    Then the response status should be 201
    And the created todo should have description "<description>"

    Examples:
      | title      | description           |
      | Assignment | Complete story tests  |
      | Groceries  | Buy milk and bread    |

  # Error Flow
  Scenario Outline: Reject a todo with an empty title
    When I attempt to create a todo with an empty title
    Then the response status should be <status>
    And the todo collection should remain unchanged

    Examples:
      | status |
      | 400    |
