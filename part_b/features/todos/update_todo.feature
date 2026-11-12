
Feature: Update Todo
  As a user
  I want to update an existing todo
  So that I can correct or change its information

  Background:
    Given the Todo Manager API is running

  # Normal Flow
  Scenario Outline: Update the title of an existing todo
    Given a todo exists with title "<old_title>"
    When I update the todo title to "<new_title>"
    Then the response status should be 200
    And the todo should have title "<new_title>"

    Examples:
      | old_title      | new_title           |
      | Study ECSE 429 | Study for ECSE 429  |
      | Buy groceries  | Buy weekly groceries|

  # Alternate Flow
  Scenario Outline: Update only the todo description
    Given a todo exists with title "<title>"
    When I update the todo description to "<description>"
    Then the response status should be 200
    And the todo should have description "<description>"
    And the todo title should remain "<title>"

    Examples:
      | title       | description          |
      | Assignment  | Complete by Friday   |
      | Gym         | Workout at 6 PM      |

  # Error Flow
  Scenario Outline: Reject an empty title during update
    Given a todo exists with title "<title>"
    When I update the todo title to an empty string
    Then the response status should be 400
    And the todo should still have its original title "<title>"

    Examples:
      | title        |
      | Study Python |
      | Finish lab   |
