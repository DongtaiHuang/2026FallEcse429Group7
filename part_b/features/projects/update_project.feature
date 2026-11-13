
Feature: Update Project
  As a user
  I want to update an existing project
  So that I can keep its information accurate

  Background:
    Given the Project API is running

  # Normal Flow
  Scenario Outline: Rename an existing project
    Given a project exists with title "<old_title>"
    When I rename the project to "<new_title>"
    Then the project response status should be 200
    And the updated project should have title "<new_title>"

    Examples:
      | old_title       | new_title        |
      | School Work     | University Work  |
      | Personal Tasks  | Daily Tasks      |

  # Alternate Flow
  Scenario Outline: Replace a project with only a title
    Given a project exists with title "<old_title>" and description "<description>"
    When I replace the project with title "<new_title>"
    Then the project response status should be 200
    And the updated project should have title "<new_title>"
    And the updated project description should be empty

    Examples:
      | old_title | description       | new_title      |
      | Website   | Old website work  | New Website    |
      | Research  | Research notes    | Updated Study  |

  # Error Flow
  Scenario Outline: Reject an invalid project completion status
    Given a project exists with title "<title>"
    When I update the project completed status to "<invalid_status>"
    Then the project response status should be 400
    And the project should remain unchanged

    Examples:
      | title         | invalid_status |
      | Test Project  | invalid        |
      | Course Work   | finished       |
