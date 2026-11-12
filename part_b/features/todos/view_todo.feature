
Feature: View Todo
  As a user
  I want to view my todos
  So that I can check my tasks

  Background:
    Given the Todo Manager API is running

  # Normal Flow
  Scenario Outline: View an existing todo by ID
    Given a todo exists with title "<title>"
    When I request the todo by its ID
    Then the response status should be 200
    And the response should contain a todo with title "<title>"

    Examples:
      | title          |
      | Study ECSE 429 |
      | Finish project |

  # Alternate Flow
  Scenario Outline: View all todos
    Given a todo exists with title "<title>"
    When I request the todo list
    Then the response status should be 200
    And the todo list should contain title "<title>"

    Examples:
      | title      |
      | Assignment |
      | Groceries  |

  # Error Flow
  Scenario Outline: View a nonexistent todo
    When I request a todo with ID <todo_id>
    Then the response status should be 404

    Examples:
      | todo_id |
      | -1      |
