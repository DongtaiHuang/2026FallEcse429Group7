
Feature: Delete Project
  As a user
  I want to delete projects that I no longer need
  So that I can keep my project list organized

  Background:
    Given the Project API is running

  # Normal Flow
  Scenario Outline: Delete an existing project
    Given a project exists with title "<title>"
    When I delete the current project
    Then the project response status should be 200
    And the deleted project should not be retrievable

    Examples:
      | title           |
      | Old coursework  |
      | Finished sprint |

  # Alternate Flow
  Scenario Outline: Delete one project while keeping another
    Given a project exists with title "<deleted_title>"
    And a second project exists with title "<kept_title>"
    When I delete the first project
    Then the project response status should be 200
    And the deleted project should not be retrievable
    And the second project should still have title "<kept_title>"

    Examples:
      | deleted_title | kept_title      |
      | Old website   | Current website |
      | Old semester  | Winter courses  |

  # Error Flow
  Scenario Outline: Reject deleting an already deleted project
    Given a project exists with title "<title>"
    And the current project has been deleted
    When I delete the current project again
    Then the project response status should be 404
    And the deleted project should not be retrievable

    Examples:
      | title             |
      | Temporary project |
      | Duplicate delete  |
