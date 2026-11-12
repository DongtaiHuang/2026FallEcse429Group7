
Feature: Complete Todo
  As a user
  I want to mark my todos as completed or incomplete
  So that I can track my progress

  Background:
    Given the Todo Manager API is running

  # Normal Flow
  Scenario Outline: Mark an incomplete todo as completed
    Given a todo exists with title "<title>"
    And the todo has completion status "false"
    When I change the todo completion status to "true"
    Then the response status should be 200
    And the todo completion status should be "true"

    Examples:
      | title          |
      | Study ECSE 429 |
      | Finish report  |

  # Alternate Flow
  Scenario Outline: Mark a completed todo as incomplete
    Given a todo exists with title "<title>"
    And the todo has completion status "true"
    When I change the todo completion status to "false"
    Then the response status should be 200
    And the todo completion status should be "false"

    Examples:
      | title        |
      | Review notes |
      | Submit lab   |

  # Error Flow
  Scenario Outline: Reject an invalid completion status
    Given a todo exists with title "<title>"
    When I change the todo completion status to "<invalid_status>"
    Then the response status should be 400
    And the todo completion status should remain unchanged

    Examples:
      | title          | invalid_status |
      | Invalid status | invalid        |
      | Wrong status   | completed      |
