
Feature: Retrieve Project by ID
  As a user
  I want to retrieve a specific project
  So that I can review its details

  Background:
    Given the Project API is running

  # Normal Flow
  Scenario Outline: Retrieve a project with title and description
    Given a project exists with title "<title>" and description "<description>"
    When I request the current project by ID
    Then the project response status should be 200
    And the retrieved project should have title "<title>"
    And the retrieved project should have description "<description>"

    Examples:
      | title          | description           |
      | ECSE 429       | Software testing      |
      | Final Project  | Complete assignments  |

  # Alternate Flow
  Scenario Outline: Retrieve a project without a description
    Given a project exists with title "<title>"
    When I request the current project by ID
    Then the project response status should be 200
    And the retrieved project should have title "<title>"
    And the retrieved project should have an empty description

    Examples:
      | title          |
      | Personal Tasks |
      | Winter Studies |

  # Error Flow
  Scenario Outline: Retrieve a deleted project
    Given a project exists with title "<title>"
    And the current project has been deleted
    When I request the current project by ID
    Then the project response status should be 404
    And the response should contain project error messages

    Examples:
      | title             |
      | Temporary Project |
      | Deleted Coursework|
