
Feature: Delete Todo
  As a user
  I want to delete todos that I no longer need
  So that I can keep my task list organized

  Background:
    Given the Todo Manager API is running

  # Normal Flow
  Scenario Outline: Delete an existing todo
    Given a todo exists with title "<title>"
    When I delete the current todo
    Then the response status should be 200
    And the deleted todo should not be retrievable

    Examples:
      | title           |
      | Old assignment  |
      | Finished report |

  # Alternate Flow
  Scenario Outline: Delete one todo while keeping another
    Given a todo exists with title "<deleted_title>"
    And a second todo exists with title "<kept_title>"
    When I delete the first todo
    Then the response status should be 200
    And the deleted todo should not be retrievable
    And the second todo should still have title "<kept_title>"

    Examples:
      | deleted_title  | kept_title      |
      | Old homework   | Current project |
      | Expired task   | Study notes     |

  # Error Flow
  Scenario Outline: Reject deleting an already deleted todo
    Given a todo exists with title "<title>"
    And I have already deleted the current todo
    When I delete the current todo again
    Then the response status should be 404
    And the deleted todo should not be retrievable

    Examples:
      | title           |
      | Temporary task  |
      | Duplicate delete|
